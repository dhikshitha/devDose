#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Challenge

def test_search():
    app = create_app()
    with app.app_context():
        # Get some sample challenges
        challenges = Challenge.query.limit(5).all()
        
        print("Sample challenges in database:")
        for challenge in challenges:
            print(f"- ID: {challenge.id}, Title: '{challenge.title}', Description: '{challenge.description[:50]}...'")
        
        # Test search functionality
        search_term = "Hello"
        print(f"\nSearching for challenges containing '{search_term}':")
        
        from sqlalchemy import or_
        search_results = Challenge.query.filter(
            or_(
                Challenge.title.ilike(f'%{search_term}%'),
                Challenge.description.ilike(f'%{search_term}%')
            )
        ).all()
        
        print(f"Found {len(search_results)} challenges:")
        for challenge in search_results:
            print(f"- ID: {challenge.id}, Title: '{challenge.title}', Description: '{challenge.description[:50]}...'")
        
        # Test with different search terms
        for term in ["world", "python", "algorithm", "array"]:
            results = Challenge.query.filter(
                or_(
                    Challenge.title.ilike(f'%{term}%'),
                    Challenge.description.ilike(f'%{term}%')
                )
            ).all()
            print(f"\nSearch for '{term}': {len(results)} results")

if __name__ == "__main__":
    test_search()