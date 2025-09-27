import yt_dlp
import os
import tempfile
from typing import Dict, List, Optional
from pathlib import Path

class YouTubeHandler:
    def __init__(self):
        self.temp_dir = Path("/tmp/videos")
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_video_info(self, url: str) -> Dict:
        """Fetch YouTube video metadata without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # Extract available formats
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':  # Video + Audio
                            formats.append({
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext'),
                                'resolution': fmt.get('resolution'),
                                'filesize': fmt.get('filesize'),
                                'quality': f"{fmt.get('resolution', 'Unknown')} ({fmt.get('ext', 'Unknown')})"
                            })
                
                # Sort by resolution (best first)
                formats.sort(key=lambda x: self._get_resolution_value(x.get('resolution', '0x0')), reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'formats': formats[:10],  # Limit to top 10 formats
                    'url': url
                }
            except Exception as e:
                raise Exception(f"Error fetching video info: {str(e)}")
    
    def download_video(self, url: str, format_id: str = None) -> str:
        """Download YouTube video to temp directory"""
        if format_id:
            format_selector = format_id
        else:
            format_selector = 'best[height<=720]'  # Default to 720p or lower
        
        output_template = str(self.temp_dir / "%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First get info to get the title for filename
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                for file in self.temp_dir.glob(f"{title}.*"):
                    if file.is_file():
                        return str(file)
                
                raise Exception("Downloaded file not found")
            except Exception as e:
                raise Exception(f"Error downloading video: {str(e)}")
    
    def _get_resolution_value(self, resolution: str) -> int:
        """Convert resolution string to numeric value for sorting"""
        if not resolution or 'x' not in resolution:
            return 0
        try:
            height = int(resolution.split('x')[1])
            return height
        except:
            return 0
    
    def cleanup_file(self, file_path: str):
        """Delete downloaded video file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")

# Global instance
youtube_handler = YouTubeHandler()