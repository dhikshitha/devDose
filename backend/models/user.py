from datetime import datetime
from extensions import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column('password_hash', db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')
    skill_level = db.Column(db.String(20), default='beginner')
    
    preferences = db.Column(db.JSON, default=lambda: {
        'daily_reminder_time': '09:00',
        'email_notifications': True,
        'categories': [],
        'difficulty_preference': 'adaptive'
    })
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email.lower()
        self.password = password
    
    @hybrid_property
    def password(self):
        return self._password_hash
    
    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_email=True):
        data = {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'timezone': self.timezone,
            'skill_level': self.skill_level,
            'preferences': self.preferences
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def update_preferences(self, preferences):
        if self.preferences is None:
            self.preferences = {}
        # Deep merge preferences
        current_prefs = dict(self.preferences)
        current_prefs.update(preferences)
        self.preferences = current_prefs
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'