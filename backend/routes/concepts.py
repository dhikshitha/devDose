from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Concept, Category, Tag, DailyContent, UserProgress, User
from services.daily_delivery_service import DailyDeliveryService
from services.news_service import NewsAPIService
from extensions import db
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

concepts_bp = Blueprint('concepts', __name__)
delivery_service = DailyDeliveryService()
news_service = NewsAPIService()


@concepts_bp.route('', methods=['GET'])
@jwt_required()
def get_concepts():
    """Get all available concepts with filtering"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        tag_name = request.args.get('tag')
        difficulty = request.args.get('difficulty')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Concept.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
            
        if tag_name:
            query = query.join(Concept.tags).filter(Tag.name == tag_name)
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'concepts': [concept.to_dict() for concept in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching concepts: {str(e)}")
        return jsonify({'error': 'Failed to fetch concepts'}), 500


@concepts_bp.route('/<int:concept_id>', methods=['GET'])
@jwt_required()
def get_concept(concept_id):
    """Get a specific concept by ID"""
    try:
        concept = Concept.query.get_or_404(concept_id)
        user_id = int(get_jwt_identity())
        
        # Get user progress for this concept
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        concept_data = concept.to_dict()
        concept_data['user_progress'] = progress.to_dict() if progress else None
        
        return jsonify(concept_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching concept: {str(e)}")
        return jsonify({'error': 'Concept not found'}), 404


@concepts_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([cat.to_dict() for cat in categories]), 200
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500


@concepts_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all tags"""
    try:
        tags = Tag.query.all()
        return jsonify([tag.to_dict() for tag in tags]), 200
    except Exception as e:
        logger.error(f"Error fetching tags: {str(e)}")
        return jsonify({'error': 'Failed to fetch tags'}), 500


# Daily Delivery Routes
@concepts_bp.route('/daily/today', methods=['GET'])
@jwt_required()
def get_today_concepts():
    """Get today's concepts for the current user"""
    try:
        user_id = int(get_jwt_identity())
        concepts = delivery_service.get_today_concepts(user_id)
        
        return jsonify({
            'date': date.today().isoformat(),
            'concepts': concepts,
            'count': len(concepts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching today's concepts: {str(e)}")
        return jsonify({'error': 'Failed to fetch today\'s concepts'}), 500


@concepts_bp.route('/daily/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_concepts():
    """Get upcoming scheduled concepts"""
    try:
        user_id = int(get_jwt_identity())
        days = request.args.get('days', 7, type=int)
        
        upcoming = delivery_service.get_upcoming_concepts(user_id, days)
        
        return jsonify({
            'upcoming': upcoming,
            'days_ahead': days
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching upcoming concepts: {str(e)}")
        return jsonify({'error': 'Failed to fetch upcoming concepts'}), 500


@concepts_bp.route('/daily/schedule', methods=['POST'])
@jwt_required()
def schedule_concepts():
    """Schedule concepts for the current user"""
    try:
        user_id = int(get_jwt_identity())
        result = delivery_service.schedule_daily_concepts_for_user(user_id)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error scheduling concepts: {str(e)}")
        return jsonify({'error': 'Failed to schedule concepts'}), 500


# Progress Routes
@concepts_bp.route('/progress/start/<int:concept_id>', methods=['POST'])
@jwt_required()
def start_concept(concept_id):
    """Mark a concept as started"""
    try:
        user_id = int(get_jwt_identity())
        progress = delivery_service.mark_concept_started(user_id, concept_id)
        
        return jsonify(progress.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error starting concept: {str(e)}")
        return jsonify({'error': 'Failed to start concept'}), 500


@concepts_bp.route('/progress/complete/<int:concept_id>', methods=['POST'])
@jwt_required()
def complete_concept(concept_id):
    """Mark a concept as completed"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        rating = data.get('rating')
        notes = data.get('notes')
        
        progress = delivery_service.mark_concept_completed(
            user_id, concept_id, rating, notes
        )
        
        return jsonify(progress.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error completing concept: {str(e)}")
        return jsonify({'error': 'Failed to complete concept'}), 500


@concepts_bp.route('/progress/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user learning statistics"""
    try:
        user_id = int(get_jwt_identity())
        stats = delivery_service.get_user_statistics(user_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500


# NewsAPI Integration Routes
@concepts_bp.route('/news/fetch', methods=['POST'])
@jwt_required()
def fetch_news():
    """Fetch latest tech news (admin only)"""
    try:
        # Check if user is admin (you might want to add role checking)
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # For now, any authenticated user can trigger this
        # In production, restrict to admin users
        
        data = request.get_json()
        query = data.get('query')
        
        articles = news_service.fetch_tech_news(query=query)
        saved = news_service.save_articles(articles)
        
        return jsonify({
            'fetched': len(articles),
            'saved': saved
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({'error': 'Failed to fetch news'}), 500


@concepts_bp.route('/news/process-daily', methods=['POST'])
@jwt_required()
def process_daily_news():
    """Process daily news fetch and conversion"""
    try:
        user_id = int(get_jwt_identity())
        # Add admin check here
        
        results = news_service.fetch_and_process_daily()
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error processing daily news: {str(e)}")
        return jsonify({'error': 'Failed to process daily news'}), 500