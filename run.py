#!/usr/bin/env python3
"""
Startup script for YouTube to Facebook Video Poster
"""

import os
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure it:")
        print("   cp .env.example .env")
        print("   # Then edit .env with your Facebook app credentials")
        sys.exit(1)
    
    # Import and run the app
    try:
        import uvicorn
        from main import app
        
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        
        print("🚀 Starting YouTube to Facebook Video Poster...")
        print(f"📍 Server will be available at: http://{host}:{port}")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(app, host=host, port=port, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()