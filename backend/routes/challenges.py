from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Challenge, Category
from services.challenge_service import ChallengeService
from extensions import db
import logging

logger = logging.getLogger(__name__)

challenges_bp = Blueprint('challenges', __name__)
challenge_service = ChallengeService()


@challenges_bp.route('', methods=['GET'])
@jwt_required()
def get_challenges():
    """Get all challenges with filtering"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        difficulty = request.args.get('difficulty')
        status = request.args.get('status')
        
        challenges = challenge_service.get_challenges(
            user_id=user_id,
            category_id=category_id,
            difficulty=difficulty,
            status=status
        )
        
        return jsonify({
            'challenges': challenges,
            'total': len(challenges)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching challenges: {str(e)}")
        return jsonify({'error': 'Failed to fetch challenges'}), 500


@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """Get specific challenge details"""
    try:
        user_id = int(get_jwt_identity())
        
        challenge_data = challenge_service.get_challenge_details(
            challenge_id=challenge_id,
            user_id=user_id
        )
        
        return jsonify(challenge_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching challenge: {str(e)}")
        return jsonify({'error': 'Challenge not found'}), 404


@challenges_bp.route('/<int:challenge_id>/submit', methods=['POST'])
@jwt_required()
def submit_solution(challenge_id):
    """Submit a solution for validation"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        code = data.get('code')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        result = challenge_service.submit_solution(
            user_id=user_id,
            challenge_id=challenge_id,
            code=code,
            language=language
        )
        
        if not result['success']:
            return jsonify(result), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error submitting solution: {str(e)}")
        return jsonify({'error': 'Failed to submit solution'}), 500


@challenges_bp.route('/<int:challenge_id>/hint/<int:hint_index>', methods=['GET'])
@jwt_required()
def get_hint(challenge_id, hint_index):
    """Get a hint for a challenge"""
    try:
        user_id = int(get_jwt_identity())
        
        hint = challenge_service.get_hint(
            user_id=user_id,
            challenge_id=challenge_id,
            hint_index=hint_index
        )
        
        if hint is None:
            return jsonify({'error': 'Hint not found'}), 404
            
        return jsonify({
            'hint': hint,
            'hint_index': hint_index
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting hint: {str(e)}")
        return jsonify({'error': 'Failed to get hint'}), 500


@challenges_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get overall leaderboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        leaderboard = challenge_service.get_leaderboard(limit=limit)
        
        return jsonify({
            'leaderboard': leaderboard,
            'type': 'overall'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500


@challenges_bp.route('/<int:challenge_id>/leaderboard', methods=['GET'])
def get_challenge_leaderboard(challenge_id):
    """Get leaderboard for specific challenge"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        leaderboard = challenge_service.get_leaderboard(
            challenge_id=challenge_id,
            limit=limit
        )
        
        return jsonify({
            'leaderboard': leaderboard,
            'type': 'challenge',
            'challenge_id': challenge_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching challenge leaderboard: {str(e)}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500


@challenges_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_challenge_stats():
    """Get user's challenge statistics"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get statistics
        from models import UserChallengeProgress, ChallengeSubmission
        
        total_attempted = UserChallengeProgress.query.filter_by(
            user_id=user_id
        ).count()
        
        total_solved = UserChallengeProgress.query.filter_by(
            user_id=user_id,
            status='solved'
        ).count()
        
        total_points = db.session.query(
            db.func.sum(ChallengeSubmission.points_earned)
        ).filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.status == 'passed'
        ).scalar() or 0
        
        # Get breakdown by difficulty
        difficulty_stats = db.session.query(
            Challenge.difficulty,
            db.func.count(UserChallengeProgress.id)
        ).join(
            UserChallengeProgress,
            Challenge.id == UserChallengeProgress.challenge_id
        ).filter(
            UserChallengeProgress.user_id == user_id,
            UserChallengeProgress.status == 'solved'
        ).group_by(
            Challenge.difficulty
        ).all()
        
        return jsonify({
            'total_attempted': total_attempted,
            'total_solved': total_solved,
            'total_points': total_points,
            'success_rate': round(total_solved / total_attempted * 100, 1) if total_attempted > 0 else 0,
            'difficulty_breakdown': {
                diff: count for diff, count in difficulty_stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching challenge stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500