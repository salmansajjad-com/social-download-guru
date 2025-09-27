#!/usr/bin/env python3
"""
Simple test script to verify the setup
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import yt_dlp
        import requests
        import jose
        import passlib
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_env_vars():
    """Test if environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'FACEBOOK_APP_ID',
        'FACEBOOK_APP_SECRET',
        'FACEBOOK_REDIRECT_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'your-{var.lower().replace("_", "-")}':
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing or default environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with actual values")
        return False
    else:
        print("✓ All environment variables are set")
        return True

def test_database():
    """Test database connection"""
    try:
        from database import engine, create_tables
        create_tables()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_youtube():
    """Test YouTube functionality"""
    try:
        from youtube import youtube_handler
        # Test with a simple YouTube URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
        info = youtube_handler.get_video_info(test_url)
        if info and 'title' in info:
            print("✓ YouTube functionality working")
            return True
        else:
            print("✗ YouTube functionality failed")
            return False
    except Exception as e:
        print(f"✗ YouTube error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing YouTube to Facebook Video Poster setup...")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Variables", test_env_vars),
        ("Database Connection", test_database),
        ("YouTube Functionality", test_youtube)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Please fix the {test_name.lower()} issue before running the app")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! You can now run the application with:")
        print("   python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the app.")
        sys.exit(1)

if __name__ == "__main__":
    main()