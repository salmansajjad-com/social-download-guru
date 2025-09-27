from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import timedelta

from database import get_db, create_tables
from models import User, FBPage, Post
from auth import (
    get_current_user, authenticate_user, create_user, 
    create_access_token, get_password_hash, verify_password
)
from youtube import youtube_handler
from facebook import facebook_handler
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube to Facebook Video Poster", version="1.0.0")

# Create database tables
create_tables()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class YouTubeFetchRequest(BaseModel):
    url: str

class YouTubeDownloadRequest(BaseModel):
    url: str
    format_id: str

class FacebookPostRequest(BaseModel):
    youtube_url: str
    youtube_title: str
    youtube_description: str
    youtube_thumbnail: str
    video_quality: str
    fb_page_id: int
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None

# Auth endpoints
@app.post("/auth/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(db, user_data.email, user_data.password)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@app.post("/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

# Facebook OAuth endpoints
@app.get("/auth/facebook/connect")
async def connect_facebook():
    """Redirect to Facebook OAuth"""
    auth_url = facebook_handler.get_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/facebook/callback")
async def facebook_callback(code: str, state: str = None, request: Request = None, db: Session = Depends(get_db)):
    """Handle Facebook OAuth callback"""
    try:
        # Exchange code for token
        token_data = facebook_handler.exchange_code_for_token(code)
        access_token = token_data['access_token']
        
        # Get user pages
        pages = facebook_handler.get_user_pages(access_token)
        
        # For MVP, we'll redirect to a page where user can select which pages to connect
        # In a real app, you'd store user_id in the OAuth state parameter
        return templates.TemplateResponse("facebook_callback.html", {
            "request": request,
            "pages": pages,
            "access_token": access_token
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Facebook connection failed: {str(e)}"
        )

@app.post("/facebook/save-pages")
async def save_facebook_pages(
    pages_data: dict, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Save selected Facebook pages to user's account"""
    try:
        pages = pages_data.get('pages', [])
        access_token = pages_data.get('access_token')
        
        saved_pages = []
        for page in pages:
            fb_page = facebook_handler.save_page_to_db(db, current_user.id, page)
            saved_pages.append({
                'id': fb_page.id,
                'page_name': fb_page.page_name,
                'page_id': fb_page.page_id
            })
        
        return {"message": "Pages saved successfully", "pages": saved_pages}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error saving pages: {str(e)}"
        )

# YouTube endpoints
@app.post("/youtube/fetch")
async def fetch_youtube_metadata(request: YouTubeFetchRequest):
    """Fetch YouTube video metadata"""
    try:
        info = youtube_handler.get_video_info(request.url)
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching video info: {str(e)}"
        )

@app.post("/youtube/download")
async def download_youtube_video(request: YouTubeDownloadRequest):
    """Download YouTube video"""
    try:
        file_path = youtube_handler.download_video(request.url, request.format_id)
        return {"file_path": file_path, "message": "Video downloaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error downloading video: {str(e)}"
        )

# Facebook posting endpoint
@app.post("/facebook/post")
async def post_to_facebook(request: FacebookPostRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload video to Facebook page"""
    try:
        # Get Facebook page
        fb_page = db.query(FBPage).filter(
            FBPage.id == request.fb_page_id,
            FBPage.user_id == current_user.id
        ).first()
        
        if not fb_page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facebook page not found"
            )
        
        # Download video
        file_path = youtube_handler.download_video(request.youtube_url, request.video_quality)
        
        try:
            # Upload to Facebook
            title = request.custom_title or request.youtube_title
            description = request.custom_description or request.youtube_description
            
            upload_result = facebook_handler.upload_video(
                fb_page.page_id,
                fb_page.access_token,
                file_path,
                title,
                description
            )
            
            # Save post to database
            post = Post(
                user_id=current_user.id,
                fb_page_id=fb_page.id,
                youtube_url=request.youtube_url,
                youtube_title=request.youtube_title,
                youtube_description=request.youtube_description,
                youtube_thumbnail=request.youtube_thumbnail,
                fb_post_id=upload_result.get('id'),
                fb_post_url=facebook_handler.get_post_url(fb_page.page_id, upload_result.get('id')),
                video_quality=request.video_quality,
                status="uploaded"
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            
            return {
                "message": "Video posted successfully",
                "post_id": upload_result.get('id'),
                "post_url": facebook_handler.get_post_url(fb_page.page_id, upload_result.get('id'))
            }
        
        finally:
            # Clean up downloaded file
            youtube_handler.cleanup_file(file_path)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error posting to Facebook: {str(e)}"
        )

# History endpoint
@app.get("/history")
async def get_post_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's post history"""
    posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()
    
    return [
        {
            "id": post.id,
            "youtube_title": post.youtube_title,
            "youtube_url": post.youtube_url,
            "fb_post_url": post.fb_post_url,
            "video_quality": post.video_quality,
            "status": post.status,
            "created_at": post.created_at.isoformat()
        }
        for post in posts
    ]

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user's Facebook pages
    fb_pages = db.query(FBPage).filter(FBPage.user_id == current_user.id).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "fb_pages": fb_pages
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)