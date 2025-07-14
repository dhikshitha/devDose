from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import and_, or_, func
from extensions import db
from models import (
    Challenge, TestCase, ChallengeSubmission,
    TestResult, UserChallengeProgress, User
)
from .challenge_execution_service import ChallengeValidator
import logging

logger = logging.getLogger(__name__)


class ChallengeService:
    def __init__(self):
        self.validator = ChallengeValidator()
    
    def get_challenges(self, 
                      user_id: int,
                      category_id: Optional[int] = None,
                      difficulty: Optional[str] = None,
                      status: Optional[str] = None) -> List[Dict]:
        """
        Get challenges with user progress
        """
        query = Challenge.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        challenges = query.all()
        
        # Get user progress for all challenges
        progress_map = {}
        user_progress = UserChallengeProgress.query.filter_by(user_id=user_id).all()
        for prog in user_progress:
            progress_map[prog.challenge_id] = prog
        
        # Filter by status if specified
        result = []
        for challenge in challenges:
            prog = progress_map.get(challenge.id)
            challenge_dict = challenge.to_dict()
            
            if prog:
                challenge_dict['user_progress'] = prog.to_dict()
                if status and prog.status != status:
                    continue
            else:
                challenge_dict['user_progress'] = {
                    'status': 'not_attempted',
                    'attempts': 0
                }
                if status and status != 'not_attempted':
                    continue
            
            result.append(challenge_dict)
        
        return result
    
    def get_challenge_details(self, challenge_id: int, user_id: int) -> Dict:
        """
        Get detailed challenge information
        """
        challenge = Challenge.query.get_or_404(challenge_id)
        challenge_dict = challenge.to_dict()
        
        # Get visible test cases
        visible_tests = TestCase.query.filter_by(
            challenge_id=challenge_id,
            is_hidden=False
        ).order_by(TestCase.order_index).all()
        
        challenge_dict['visible_test_cases'] = [
            test.to_dict() for test in visible_tests
        ]
        
        # Get user progress
        progress = UserChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if progress:
            challenge_dict['user_progress'] = progress.to_dict()
            
            # Get recent submissions
            recent_submissions = ChallengeSubmission.query.filter_by(
                user_id=user_id,
                challenge_id=challenge_id
            ).order_by(ChallengeSubmission.submitted_at.desc()).limit(5).all()
            
            challenge_dict['recent_submissions'] = [
                {
                    'id': sub.id,
                    'status': sub.status,
                    'passed_tests': sub.passed_tests,
                    'total_tests': sub.total_tests,
                    'submitted_at': sub.submitted_at.isoformat()
                }
                for sub in recent_submissions
            ]
        else:
            challenge_dict['user_progress'] = {
                'status': 'not_attempted',
                'attempts': 0
            }
            challenge_dict['recent_submissions'] = []
        
        return challenge_dict
    
    def submit_solution(self, 
                       user_id: int,
                       challenge_id: int,
                       code: str,
                       language: str = 'python') -> Dict:
        """
        Submit and validate a solution
        """
        # Get challenge and test cases
        challenge = Challenge.query.get_or_404(challenge_id)
        test_cases = TestCase.query.filter_by(challenge_id=challenge_id).order_by(TestCase.order_index).all()
        
        if not test_cases:
            return {
                'success': False,
                'error': 'No test cases found for this challenge'
            }
        
        # Check syntax first
        valid, syntax_error = self.validator.validate_syntax(code, language)
        if not valid:
            return {
                'success': False,
                'error': syntax_error,
                'status': 'error'
            }
        
        # Create submission record
        submission = ChallengeSubmission(
            user_id=user_id,
            challenge_id=challenge_id,
            code=code,
            language=language,
            status='running',
            total_tests=len(test_cases)
        )
        db.session.add(submission)
        db.session.commit()
        
        try:
            # Prepare test cases for validation
            test_case_data = [
                {
                    'id': tc.id,
                    'input': tc.input_data,
                    'expected_output': tc.expected_output
                }
                for tc in test_cases
            ]
            
            # Run validation
            validation_result = self.validator.validate_submission(
                code=code,
                language=language,
                test_cases=test_case_data,
                time_limit=challenge.time_limit,
                memory_limit=challenge.memory_limit
            )
            
            # Update submission with results
            submission.status = validation_result['overall_status']
            submission.passed_tests = validation_result['passed']
            submission.execution_time = validation_result['execution_time']
            
            # Save test results
            for test_result in validation_result['test_results']:
                result = TestResult(
                    submission_id=submission.id,
                    test_case_id=test_result['test_case_id'],
                    passed=test_result['passed'],
                    actual_output=test_result.get('actual_output', ''),
                    execution_time=test_result.get('execution_time', 0),
                    error_message=test_result.get('error', '')
                )
                db.session.add(result)
                
                # Stop on first failure
                if not test_result['passed']:
                    submission.failed_test_case = test_result['test_case_id']
                    submission.error_message = test_result.get('error', 'Wrong answer')
                    break
            
            # Calculate points if all tests passed
            if submission.status == 'passed':
                submission.points_earned = challenge.points
            
            # Update user progress
            self._update_user_progress(user_id, challenge_id, submission)
            
            db.session.commit()
            
            return {
                'success': True,
                'submission': submission.to_dict(),
                'validation_result': validation_result
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Submission error: {str(e)}")
            
            submission.status = 'error'
            submission.error_message = str(e)
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'status': 'error'
            }
    
    def _update_user_progress(self, user_id: int, challenge_id: int, submission: ChallengeSubmission):
        """
        Update user progress for a challenge
        """
        progress = UserChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if not progress:
            progress = UserChallengeProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                status='attempted',
                attempts=1,
                last_attempted_at=datetime.utcnow()
            )
            db.session.add(progress)
        else:
            progress.attempts += 1
            progress.last_attempted_at = datetime.utcnow()
        
        # Update status and best submission
        if submission.status == 'passed':
            if progress.status != 'solved':
                progress.status = 'solved'
                progress.first_solved_at = datetime.utcnow()
            
            # Update best submission if this one is better
            if not progress.best_submission_id or submission.points_earned > 0:
                progress.best_submission_id = submission.id
        
        return progress
    
    def get_hint(self, user_id: int, challenge_id: int, hint_index: int) -> Optional[str]:
        """
        Get a hint for a challenge
        """
        challenge = Challenge.query.get_or_404(challenge_id)
        
        if not challenge.hints or hint_index >= len(challenge.hints):
            return None
        
        # Update hints used count
        progress = UserChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if progress:
            progress.hints_used = max(progress.hints_used, hint_index + 1)
        else:
            progress = UserChallengeProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                status='attempted',
                hints_used=hint_index + 1,
                attempts=0
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return challenge.hints[hint_index]
    
    def get_leaderboard(self, challenge_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """
        Get leaderboard for challenges
        """
        if challenge_id:
            # Leaderboard for specific challenge
            query = db.session.query(
                User.username,
                ChallengeSubmission.points_earned,
                ChallengeSubmission.execution_time,
                ChallengeSubmission.submitted_at
            ).join(
                ChallengeSubmission, User.id == ChallengeSubmission.user_id
            ).filter(
                ChallengeSubmission.challenge_id == challenge_id,
                ChallengeSubmission.status == 'passed'
            ).order_by(
                ChallengeSubmission.points_earned.desc(),
                ChallengeSubmission.execution_time
            ).limit(limit)
        else:
            # Overall leaderboard
            query = db.session.query(
                User.username,
                func.sum(ChallengeSubmission.points_earned).label('total_points'),
                func.count(ChallengeSubmission.id).label('challenges_solved')
            ).join(
                ChallengeSubmission, User.id == ChallengeSubmission.user_id
            ).filter(
                ChallengeSubmission.status == 'passed'
            ).group_by(
                User.username
            ).order_by(
                func.sum(ChallengeSubmission.points_earned).desc()
            ).limit(limit)
        
        results = query.all()
        
        if challenge_id:
            return [
                {
                    'rank': i + 1,
                    'username': r.username,
                    'points': r.points_earned,
                    'execution_time': r.execution_time,
                    'submitted_at': r.submitted_at.isoformat()
                }
                for i, r in enumerate(results)
            ]
        else:
            return [
                {
                    'rank': i + 1,
                    'username': r.username,
                    'total_points': r.total_points,
                    'challenges_solved': r.challenges_solved
                }
                for i, r in enumerate(results)
            ]