# YouTube to Facebook Video Poster

A minimal web application that allows users to download YouTube videos and post them directly to their Facebook pages.

## Features

- **User Authentication**: Register and login with JWT tokens
- **Facebook Integration**: Connect Facebook pages via OAuth
- **YouTube Processing**: Fetch video metadata and download in selected quality
- **Video Upload**: Upload downloaded videos to Facebook pages
- **Post History**: Track and view previously posted videos
- **Modern UI**: Clean Bootstrap-based interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (easily switchable to PostgreSQL)
- **yt-dlp**: YouTube video downloading
- **JWT**: Authentication tokens
- **Facebook Graph API**: Video uploading

### Frontend
- **Bootstrap 5**: UI framework
- **Vanilla JavaScript**: No complex frontend framework
- **Font Awesome**: Icons

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./youtube_fb_poster.db

# JWT Secret (change this in production!)
SECRET_KEY=your-secret-key-here-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Facebook App Credentials
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/auth/facebook/callback

# Server
HOST=0.0.0.0
PORT=8000
```

### 3. Facebook App Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Facebook Login" product
4. Set up OAuth redirect URI: `http://localhost:8000/auth/facebook/callback`
5. Add the following permissions:
   - `pages_manage_posts`
   - `pages_show_list`
   - `pages_read_engagement`
6. Copy your App ID and App Secret to the `.env` file

### 4. Run the Application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000`

## Usage

### 1. Register/Login
- Visit `http://localhost:8000`
- Register a new account or login with existing credentials

### 2. Connect Facebook Page
- Go to Dashboard
- Click "Connect Facebook Page"
- Authorize the app with your Facebook account
- Select the pages you want to connect

### 3. Post YouTube Video
- Paste a YouTube URL in the dashboard
- Select video quality
- Optionally customize title and description
- Choose target Facebook page
- Click "Post to Facebook"

### 4. View History
- All posted videos are tracked in the history section
- Click links to view on YouTube or Facebook

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/facebook/connect` - Start Facebook OAuth
- `GET /auth/facebook/callback` - Handle Facebook OAuth callback

### YouTube
- `POST /youtube/fetch` - Get video metadata
- `POST /youtube/download` - Download video file

### Facebook
- `POST /facebook/post` - Upload video to Facebook page

### General
- `GET /history` - Get user's post history
- `GET /dashboard` - Dashboard page

## Database Schema

### Users
- `id`: Primary key
- `email`: User email (unique)
- `password_hash`: Hashed password
- `created_at`: Registration timestamp
- `is_active`: Account status

### FB Pages
- `id`: Primary key
- `user_id`: Foreign key to users
- `page_id`: Facebook page ID
- `page_name`: Facebook page name
- `access_token`: Page access token
- `created_at`: Connection timestamp
- `is_active`: Connection status

### Posts
- `id`: Primary key
- `user_id`: Foreign key to users
- `fb_page_id`: Foreign key to fb_pages
- `youtube_url`: Original YouTube URL
- `youtube_title`: Video title
- `youtube_description`: Video description
- `youtube_thumbnail`: Thumbnail URL
- `fb_post_id`: Facebook post ID
- `fb_post_url`: Facebook post URL
- `video_quality`: Selected quality
- `created_at`: Post timestamp
- `status`: Post status (pending/uploaded/failed)

## File Structure

```
├── main.py                 # FastAPI application
├── models.py              # Database models
├── database.py            # Database configuration
├── auth.py                # Authentication logic
├── youtube.py             # YouTube processing
├── facebook.py            # Facebook integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Environment configuration
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/               # Static files
    ├── css/
    └── js/
```

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Consider using PostgreSQL for production
- Implement rate limiting for API endpoints
- Add input validation and sanitization
- Store Facebook tokens securely

## Troubleshooting

### Common Issues

1. **Facebook OAuth Error**: Ensure redirect URI matches exactly
2. **YouTube Download Fails**: Check if yt-dlp is up to date
3. **Database Errors**: Ensure database file permissions are correct
4. **Token Expired**: Reconnect Facebook page if access token expires

### Logs

Check the console output for detailed error messages. The application logs all major operations and errors.

## Production Deployment

For production deployment:

1. Use a production database (PostgreSQL)
2. Set up proper environment variables
3. Use a reverse proxy (nginx)
4. Enable HTTPS
5. Set up proper logging
6. Consider using Docker for containerization

## License

This project is for educational purposes. Make sure to comply with YouTube's Terms of Service and Facebook's Platform Policy when using this application.