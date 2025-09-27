import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import FBPage

load_dotenv()

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")

class FacebookHandler:
    def __init__(self):
        self.app_id = FACEBOOK_APP_ID
        self.app_secret = FACEBOOK_APP_SECRET
        self.redirect_uri = FACEBOOK_REDIRECT_URI
    
    def get_auth_url(self) -> str:
        """Generate Facebook OAuth URL"""
        scope = "pages_manage_posts,pages_show_list,pages_read_engagement"
        return (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code"
        )
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_pages(self, access_token: str) -> List[Dict]:
        """Get list of Facebook pages user manages"""
        pages_url = "https://graph.facebook.com/v18.0/me/accounts"
        
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(pages_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('data', [])
    
    def upload_video(self, page_id: str, page_access_token: str, video_path: str, 
                    title: str, description: str = "") -> Dict:
        """Upload video to Facebook page"""
        upload_url = f"https://graph-video.facebook.com/v18.0/{page_id}/videos"
        
        with open(video_path, 'rb') as video_file:
            files = {
                'source': video_file
            }
            
            data = {
                'access_token': page_access_token,
                'title': title,
                'description': description
            }
            
            response = requests.post(upload_url, files=files, data=data)
            response.raise_for_status()
            
            return response.json()
    
    def get_post_url(self, page_id: str, post_id: str) -> str:
        """Generate Facebook post URL"""
        return f"https://www.facebook.com/{page_id}/posts/{post_id}"
    
    def save_page_to_db(self, db: Session, user_id: int, page_data: Dict) -> FBPage:
        """Save Facebook page data to database"""
        # Check if page already exists
        existing_page = db.query(FBPage).filter(
            FBPage.user_id == user_id,
            FBPage.page_id == page_data['id']
        ).first()
        
        if existing_page:
            # Update existing page
            existing_page.page_name = page_data['name']
            existing_page.access_token = page_data['access_token']
            db.commit()
            return existing_page
        else:
            # Create new page
            fb_page = FBPage(
                user_id=user_id,
                page_id=page_data['id'],
                page_name=page_data['name'],
                access_token=page_data['access_token']
            )
            db.add(fb_page)
            db.commit()
            db.refresh(fb_page)
            return fb_page

# Global instance
facebook_handler = FacebookHandler()