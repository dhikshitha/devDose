import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_
from extensions import db
from models import NewsArticle, Concept, Category, Tag
import logging

logger = logging.getLogger(__name__)


class NewsAPIService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2'
        self.tech_sources = [
            'techcrunch', 'the-verge', 'ars-technica', 'wired',
            'hacker-news', 'recode', 'engadget', 'techradar'
        ]
        
    def fetch_tech_news(self, 
                       query: Optional[str] = None,
                       category: str = 'technology',
                       page_size: int = 100) -> List[Dict]:
        """
        Fetch technology news from NewsAPI
        """
        if not self.api_key:
            logger.error("NEWS_API_KEY not configured")
            return []
            
        try:
            # Build query parameters
            params = {
                'apiKey': self.api_key,
                'category': category,
                'language': 'en',
                'pageSize': page_size,
                'sortBy': 'publishedAt'
            }
            
            # Add query if provided
            if query:
                params['q'] = query
            else:
                # Default technology-related keywords
                params['q'] = 'programming OR "machine learning" OR "web development" OR "cloud computing" OR "cybersecurity" OR "data science"'
            
            # Add date range (last 7 days)
            from_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
            params['from'] = from_date
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def save_articles(self, articles: List[Dict]) -> int:
        """
        Save fetched articles to database
        """
        saved_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = NewsArticle.query.filter_by(
                    url=article_data.get('url')
                ).first()
                
                if existing:
                    continue
                
                # Create new article
                article = NewsArticle(
                    title=article_data.get('title', '')[:300],
                    description=article_data.get('description', ''),
                    content=article_data.get('content', ''),
                    url=article_data.get('url', ''),
                    url_to_image=article_data.get('urlToImage'),
                    source_name=article_data.get('source', {}).get('name'),
                    author=article_data.get('author'),
                    published_at=self._parse_date(article_data.get('publishedAt')),
                    category='technology'
                )
                
                db.session.add(article)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving article: {str(e)}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"Saved {saved_count} new articles")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing articles: {str(e)}")
            
        return saved_count
    
    def convert_to_concept(self, article_id: int, category_name: str = 'General') -> Optional[Concept]:
        """
        Convert a news article to a learning concept
        """
        article = NewsArticle.query.get(article_id)
        if not article or article.is_processed:
            return None
            
        try:
            # Get or create category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(
                    name=category_name,
                    description=f"{category_name} technology concepts"
                )
                db.session.add(category)
                db.session.commit()
            
            # Create concept from article
            concept = Concept(
                title=article.title,
                short_description=article.description or article.title,
                content=self._enhance_content(article),
                difficulty='intermediate',
                category_id=category.id,
                source='newsapi',
                external_url=article.url,
                image_url=article.url_to_image,
                author=article.author,
                published_at=article.published_at,
                meta_info={
                    'source_name': article.source_name,
                    'original_article_id': article.id
                }
            )
            
            db.session.add(concept)
            
            # Mark article as processed
            article.is_processed = True
            article.concept_id = concept.id
            
            db.session.commit()
            logger.info(f"Converted article {article_id} to concept")
            
            return concept
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error converting article to concept: {str(e)}")
            return None
    
    def _enhance_content(self, article: NewsArticle) -> str:
        """
        Enhance article content for learning purposes
        """
        content = f"# {article.title}\n\n"
        
        if article.description:
            content += f"## Overview\n{article.description}\n\n"
            
        if article.content:
            content += f"## Details\n{article.content}\n\n"
        else:
            content += "## Details\nContent not available. Please visit the source for full article.\n\n"
            
        content += f"## Additional Resources\n"
        content += f"- [Original Article]({article.url})\n"
        content += f"- Source: {article.source_name}\n"
        
        if article.author:
            content += f"- Author: {article.author}\n"
            
        return content
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string from NewsAPI
        """
        if not date_str:
            return None
            
        try:
            # NewsAPI date format: 2024-01-14T10:30:00Z
            return datetime.strptime(date_str.replace('Z', '+00:00'), '%Y-%m-%dT%H:%M:%S%z')
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            except:
                return None
    
    def fetch_and_process_daily(self) -> Dict[str, int]:
        """
        Fetch and process daily news articles
        """
        results = {
            'fetched': 0,
            'saved': 0,
            'converted': 0
        }
        
        # Fetch articles for different tech topics
        topics = [
            'artificial intelligence',
            'web development',
            'cloud computing',
            'cybersecurity',
            'blockchain',
            'data science',
            'DevOps',
            'mobile development'
        ]
        
        all_articles = []
        for topic in topics:
            articles = self.fetch_tech_news(query=topic, page_size=20)
            all_articles.extend(articles)
            
        results['fetched'] = len(all_articles)
        
        # Save articles
        results['saved'] = self.save_articles(all_articles)
        
        # Auto-convert some high-quality articles
        unprocessed = NewsArticle.query.filter_by(
            is_processed=False
        ).order_by(NewsArticle.published_at.desc()).limit(10).all()
        
        for article in unprocessed:
            if article.content and len(article.content) > 500:
                concept = self.convert_to_concept(article.id)
                if concept:
                    results['converted'] += 1
                    
        return results