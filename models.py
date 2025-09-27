from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    fb_pages = relationship("FBPage", back_populates="user")
    posts = relationship("Post", back_populates="user")

class FBPage(Base):
    __tablename__ = "fb_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    page_id = Column(String, nullable=False)
    page_name = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="fb_pages")
    posts = relationship("Post", back_populates="fb_page")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fb_page_id = Column(Integer, ForeignKey("fb_pages.id"), nullable=False)
    youtube_url = Column(String, nullable=False)
    youtube_title = Column(String, nullable=False)
    youtube_description = Column(Text)
    youtube_thumbnail = Column(String)
    fb_post_id = Column(String)
    fb_post_url = Column(String)
    video_quality = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, uploaded, failed
    
    # Relationships
    user = relationship("User", back_populates="posts")
    fb_page = relationship("FBPage", back_populates="posts")