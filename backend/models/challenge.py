from extensions import db
from datetime import datetime
from sqlalchemy import JSON, Text

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='easy')  # easy, medium, hard
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Problem details
    problem_statement = db.Column(db.Text, nullable=False)
    initial_code = db.Column(db.Text, nullable=False)  # Starter code template
    solution_code = db.Column(db.Text)  # Example solution (hidden from users)
    hints = db.Column(JSON)  # List of hints
    
    # Constraints and requirements
    time_limit = db.Column(db.Integer, default=5000)  # milliseconds
    memory_limit = db.Column(db.Integer, default=256)  # MB
    
    # Metadata
    points = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='challenges')
    test_cases = db.relationship('TestCase', backref='challenge', cascade='all, delete-orphan')
    submissions = db.relationship('ChallengeSubmission', backref='challenge')
    
    def to_dict(self, include_solution=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'category': self.category.name if self.category else None,
            'problem_statement': self.problem_statement,
            'initial_code': self.initial_code,
            'hints': self.hints or [],
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'points': self.points,
            'test_cases_count': len(self.test_cases),
            'created_at': self.created_at.isoformat()
        }
        
        if include_solution:
            data['solution_code'] = self.solution_code
            
        return data


class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)  # Hidden test cases for validation
    description = db.Column(db.String(200))  # Optional description for visible test cases
    order_index = db.Column(db.Integer, default=0)
    
    def to_dict(self, show_hidden=False):
        if self.is_hidden and not show_hidden:
            return {
                'id': self.id,
                'is_hidden': True,
                'description': 'Hidden test case'
            }
            
        return {
            'id': self.id,
            'input': self.input_data,
            'expected_output': self.expected_output,
            'is_hidden': self.is_hidden,
            'description': self.description,
            'order_index': self.order_index
        }


class ChallengeSubmission(db.Model):
    __tablename__ = 'challenge_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default='python')  # python, javascript
    
    # Execution results
    status = db.Column(db.String(20), nullable=False)  # pending, running, passed, failed, error
    passed_tests = db.Column(db.Integer, default=0)
    total_tests = db.Column(db.Integer, default=0)
    execution_time = db.Column(db.Integer)  # milliseconds
    memory_used = db.Column(db.Integer)  # MB
    
    # Error information
    error_message = db.Column(db.Text)
    failed_test_case = db.Column(db.Integer)  # ID of first failed test case
    
    # Scoring
    points_earned = db.Column(db.Integer, default=0)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='challenge_submissions')
    test_results = db.relationship('TestResult', backref='submission', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'code': self.code,
            'language': self.language,
            'status': self.status,
            'passed_tests': self.passed_tests,
            'total_tests': self.total_tests,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'error_message': self.error_message,
            'points_earned': self.points_earned,
            'submitted_at': self.submitted_at.isoformat(),
            'test_results': [result.to_dict() for result in self.test_results]
        }


class TestResult(db.Model):
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('challenge_submissions.id'), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    
    passed = db.Column(db.Boolean, default=False)
    actual_output = db.Column(db.Text)
    execution_time = db.Column(db.Integer)  # milliseconds
    error_message = db.Column(db.Text)
    
    # Relationships
    test_case = db.relationship('TestCase')
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'passed': self.passed,
            'actual_output': self.actual_output,
            'execution_time': self.execution_time,
            'error_message': self.error_message,
            'test_case': self.test_case.to_dict() if not self.test_case.is_hidden else None
        }


class UserChallengeProgress(db.Model):
    __tablename__ = 'user_challenge_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    
    status = db.Column(db.String(20), default='not_attempted')  # not_attempted, attempted, solved
    best_submission_id = db.Column(db.Integer, db.ForeignKey('challenge_submissions.id'))
    attempts = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    first_solved_at = db.Column(db.DateTime)
    last_attempted_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='challenge_progress')
    challenge = db.relationship('Challenge')
    best_submission = db.relationship('ChallengeSubmission', foreign_keys=[best_submission_id])
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_id', name='_user_challenge_uc'),)
    
    def to_dict(self):
        return {
            'challenge_id': self.challenge_id,
            'status': self.status,
            'attempts': self.attempts,
            'hints_used': self.hints_used,
            'first_solved_at': self.first_solved_at.isoformat() if self.first_solved_at else None,
            'last_attempted_at': self.last_attempted_at.isoformat() if self.last_attempted_at else None
        }