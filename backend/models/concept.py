from extensions import db
from datetime import datetime
from sqlalchemy import JSON

class Concept(db.Model):
    __tablename__ = 'concepts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    source = db.Column(db.String(50), default='manual')
    external_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    author = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    meta_info = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='concepts')
    tags = db.relationship('Tag', secondary='concept_tags', backref='concepts')
    user_progress = db.relationship('UserProgress', backref='concept')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'short_description': self.short_description,
            'content': self.content,
            'difficulty': self.difficulty,
            'category': self.category.name if self.category else None,
            'source': self.source,
            'external_url': self.external_url,
            'image_url': self.image_url,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat()
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }


class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


# Association table for many-to-many relationship between concepts and tags
concept_tags = db.Table('concept_tags',
    db.Column('concept_id', db.Integer, db.ForeignKey('concepts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class DailyContent(db.Model):
    __tablename__ = 'daily_content'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    is_delivered = db.Column(db.Boolean, default=False)
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='daily_content')
    concept = db.relationship('Concept', backref='daily_deliveries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'concept': self.concept.to_dict() if self.concept else None,
            'scheduled_date': self.scheduled_date.isoformat(),
            'is_delivered': self.is_delivered,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }


class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='progress')
    
    # Add unique constraint to prevent duplicate progress entries
    __table_args__ = (db.UniqueConstraint('user_id', 'concept_id', name='_user_concept_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'concept_id': self.concept_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'rating': self.rating
        }


class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    url = db.Column(db.String(500), unique=True, nullable=False)
    url_to_image = db.Column(db.String(500))
    source_name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    category = db.Column(db.String(50))
    is_processed = db.Column(db.Boolean, default=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'))
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to concept if converted
    related_concept = db.relationship('Concept', backref='news_source')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'url_to_image': self.url_to_image,
            'source_name': self.source_name,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category,
            'is_processed': self.is_processed
        }