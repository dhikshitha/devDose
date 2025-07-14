import logging
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict
from sqlalchemy import and_, or_, func
from extensions import db
from models import (
    User, Concept, DailyContent, UserProgress, 
    Category, Tag
)
import random

logger = logging.getLogger(__name__)


class DailyDeliveryService:
    def __init__(self):
        self.max_concepts_per_day = 3
        self.lookahead_days = 7  # Schedule concepts for next 7 days
        
    def schedule_daily_concepts_for_user(self, user_id: int) -> Dict[str, int]:
        """
        Schedule daily concepts for a user for the next week
        """
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'scheduled': 0}
            
        try:
            scheduled_count = 0
            today = date.today()
            
            for day_offset in range(self.lookahead_days):
                target_date = today + timedelta(days=day_offset)
                
                # Check if concepts already scheduled for this date
                existing = DailyContent.query.filter_by(
                    user_id=user_id,
                    scheduled_date=target_date
                ).count()
                
                if existing >= self.max_concepts_per_day:
                    continue
                    
                # Get concepts to schedule
                concepts_needed = self.max_concepts_per_day - existing
                concepts = self._get_concepts_for_user(
                    user_id, 
                    concepts_needed,
                    target_date
                )
                
                # Schedule concepts
                for concept in concepts:
                    daily_content = DailyContent(
                        user_id=user_id,
                        concept_id=concept.id,
                        scheduled_date=target_date
                    )
                    db.session.add(daily_content)
                    scheduled_count += 1
                    
            db.session.commit()
            logger.info(f"Scheduled {scheduled_count} concepts for user {user_id}")
            
            return {
                'user_id': user_id,
                'scheduled': scheduled_count,
                'days_ahead': self.lookahead_days
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error scheduling concepts: {str(e)}")
            return {'error': str(e), 'scheduled': 0}
    
    def _get_concepts_for_user(self, 
                               user_id: int, 
                               limit: int,
                               target_date: date) -> List[Concept]:
        """
        Get suitable concepts for a user based on their progress and preferences
        """
        # Get user's completed concepts
        completed_concept_ids = db.session.query(UserProgress.concept_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.status == 'completed'
        ).subquery()
        
        # Get already scheduled concepts
        scheduled_concept_ids = db.session.query(DailyContent.concept_id).filter(
            DailyContent.user_id == user_id
        ).subquery()
        
        # Get user's preferred categories (based on progress)
        user_categories = db.session.query(
            Category.id,
            func.count(UserProgress.id).label('progress_count')
        ).join(
            Concept, Category.id == Concept.category_id
        ).join(
            UserProgress, UserProgress.concept_id == Concept.id
        ).filter(
            UserProgress.user_id == user_id
        ).group_by(
            Category.id
        ).all()
        
        preferred_category_ids = [cat.id for cat in user_categories] if user_categories else []
        
        # Build query for available concepts
        query = Concept.query.filter(
            Concept.is_active == True,
            ~Concept.id.in_(completed_concept_ids),
            ~Concept.id.in_(scheduled_concept_ids)
        )
        
        # Mix of preferred categories and new topics
        concepts = []
        
        # 60% from preferred categories if available
        if preferred_category_ids:
            preferred_limit = int(limit * 0.6)
            preferred_concepts = query.filter(
                Concept.category_id.in_(preferred_category_ids)
            ).order_by(func.random()).limit(preferred_limit).all()
            concepts.extend(preferred_concepts)
        
        # Fill remaining with diverse topics
        remaining_needed = limit - len(concepts)
        if remaining_needed > 0:
            exclude_ids = [c.id for c in concepts]
            diverse_concepts = query.filter(
                ~Concept.id.in_(exclude_ids)
            ).order_by(func.random()).limit(remaining_needed).all()
            concepts.extend(diverse_concepts)
        
        return concepts[:limit]
    
    def get_today_concepts(self, user_id: int) -> List[Dict]:
        """
        Get today's scheduled concepts for a user
        """
        today = date.today()
        
        daily_contents = DailyContent.query.filter_by(
            user_id=user_id,
            scheduled_date=today
        ).all()
        
        # Mark as delivered
        for dc in daily_contents:
            if not dc.is_delivered:
                dc.is_delivered = True
                dc.delivered_at = datetime.utcnow()
        
        db.session.commit()
        
        return [dc.to_dict() for dc in daily_contents]
    
    def get_upcoming_concepts(self, user_id: int, days: int = 7) -> Dict[str, List]:
        """
        Get upcoming scheduled concepts for a user
        """
        today = date.today()
        end_date = today + timedelta(days=days)
        
        daily_contents = DailyContent.query.filter(
            DailyContent.user_id == user_id,
            DailyContent.scheduled_date >= today,
            DailyContent.scheduled_date <= end_date
        ).order_by(DailyContent.scheduled_date).all()
        
        # Group by date
        grouped = {}
        for dc in daily_contents:
            date_str = dc.scheduled_date.isoformat()
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(dc.to_dict())
            
        return grouped
    
    def mark_concept_started(self, user_id: int, concept_id: int) -> UserProgress:
        """
        Mark a concept as started by a user
        """
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                concept_id=concept_id,
                status='in_progress',
                started_at=datetime.utcnow()
            )
            db.session.add(progress)
        elif progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = datetime.utcnow()
            
        db.session.commit()
        return progress
    
    def mark_concept_completed(self, 
                              user_id: int, 
                              concept_id: int,
                              rating: Optional[int] = None,
                              notes: Optional[str] = None) -> UserProgress:
        """
        Mark a concept as completed by a user
        """
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                concept_id=concept_id,
                status='completed',
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        else:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
            
        if rating:
            progress.rating = rating
        if notes:
            progress.notes = notes
            
        db.session.commit()
        return progress
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """
        Get learning statistics for a user
        """
        # Total concepts completed
        completed_count = UserProgress.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        # In progress
        in_progress_count = UserProgress.query.filter_by(
            user_id=user_id,
            status='in_progress'
        ).count()
        
        # Concepts by category
        category_stats = db.session.query(
            Category.name,
            func.count(UserProgress.id).label('count')
        ).join(
            Concept, Category.id == Concept.category_id
        ).join(
            UserProgress, UserProgress.concept_id == Concept.id
        ).filter(
            UserProgress.user_id == user_id,
            UserProgress.status == 'completed'
        ).group_by(
            Category.name
        ).all()
        
        # Learning streak
        streak = self._calculate_learning_streak(user_id)
        
        # Average rating
        avg_rating = db.session.query(
            func.avg(UserProgress.rating)
        ).filter(
            UserProgress.user_id == user_id,
            UserProgress.rating.isnot(None)
        ).scalar() or 0
        
        return {
            'completed_concepts': completed_count,
            'in_progress_concepts': in_progress_count,
            'total_concepts_seen': completed_count + in_progress_count,
            'categories_learned': [
                {'category': cat.name, 'count': cat.count} 
                for cat in category_stats
            ],
            'learning_streak': streak,
            'average_rating': round(float(avg_rating), 2)
        }
    
    def _calculate_learning_streak(self, user_id: int) -> int:
        """
        Calculate consecutive days of learning
        """
        # Get all completed dates
        completed_dates = db.session.query(
            func.date(UserProgress.completed_at)
        ).filter(
            UserProgress.user_id == user_id,
            UserProgress.status == 'completed',
            UserProgress.completed_at.isnot(None)
        ).order_by(
            func.date(UserProgress.completed_at).desc()
        ).all()
        
        if not completed_dates:
            return 0
            
        streak = 0
        today = date.today()
        current_date = today
        
        for (completed_date,) in completed_dates:
            if completed_date == current_date:
                streak += 1
                current_date = current_date - timedelta(days=1)
            elif completed_date < current_date:
                break
                
        return streak
    
    def schedule_all_users(self) -> Dict[str, int]:
        """
        Schedule concepts for all active users
        """
        users = User.query.filter_by(is_active=True).all()
        scheduled_total = 0
        
        for user in users:
            result = self.schedule_daily_concepts_for_user(user.id)
            scheduled_total += result.get('scheduled', 0)
            
        return {
            'users_processed': len(users),
            'concepts_scheduled': scheduled_total
        }