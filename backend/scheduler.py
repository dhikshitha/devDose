#!/usr/bin/env python
"""
Scheduler for daily concept delivery and news fetching
Can be run as a cron job or scheduled task
"""
import logging
from datetime import datetime
from app import create_app
from services.daily_delivery_service import DailyDeliveryService
from services.news_service import NewsAPIService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_tasks():
    """Run all daily scheduled tasks"""
    app = create_app()
    
    with app.app_context():
        logger.info(f"Starting daily tasks at {datetime.utcnow()}")
        
        # Initialize services
        delivery_service = DailyDeliveryService()
        news_service = NewsAPIService()
        
        # Task 1: Fetch and process news articles
        try:
            logger.info("Fetching daily news articles...")
            news_results = news_service.fetch_and_process_daily()
            logger.info(f"News processing results: {news_results}")
        except Exception as e:
            logger.error(f"Error processing news: {str(e)}")
        
        # Task 2: Schedule concepts for all users
        try:
            logger.info("Scheduling daily concepts for all users...")
            schedule_results = delivery_service.schedule_all_users()
            logger.info(f"Scheduling results: {schedule_results}")
        except Exception as e:
            logger.error(f"Error scheduling concepts: {str(e)}")
        
        logger.info(f"Daily tasks completed at {datetime.utcnow()}")


if __name__ == "__main__":
    run_daily_tasks()