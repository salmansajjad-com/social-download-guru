
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Download, Link, Video, X } from "lucide-react";

interface VideoItem {
  id: string;
  title: string;
  thumbnail: string;
  duration: string;
}

export function VideoDownloader() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [videos, setVideos] = useState<VideoItem[]>([]);

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      toast.error("Please enter a Facebook video URL");
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const mockVideos: VideoItem[] = [
        {
          id: "1",
          title: "Sample Video 1",
          thumbnail: "https://picsum.photos/400/225",
          duration: "2:30",
        },
        {
          id: "2",
          title: "Sample Video 2",
          thumbnail: "https://picsum.photos/400/225",
          duration: "1:45",
        },
      ];
      setVideos(mockVideos);
      toast.success("Videos fetched successfully");
    } catch (error) {
      toast.error("Failed to fetch videos");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (videoId: string) => {
    toast.success(`Downloading video ${videoId}`);
  };

  const handleDownloadAll = () => {
    toast.success("Downloading all videos");
  };

  const clearUrl = () => {
    setUrl("");
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Facebook Video Downloader
        </h1>
        <p className="mx-auto max-w-[600px] text-gray-500 md:text-lg">
          Download multiple videos from Facebook in high quality. Just paste the URL and we'll handle the rest.
        </p>
      </div>

      <form onSubmit={handleUrlSubmit} className="space-y-4">
        <div className="input-container">
          <div className="relative flex items-center">
            <Link className="ml-3 h-5 w-5 text-gray-400" />
            <Input
              type="url"
              placeholder="Paste Facebook video URL here..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="border-0 pl-2 pr-10 focus-visible:ring-0"
            />
            {url && (
              <button
                type="button"
                onClick={clearUrl}
                className="absolute right-3 text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
              <span>Fetching videos...</span>
            </div>
          ) : (
            <span>Fetch Videos</span>
          )}
        </Button>
      </form>

      {videos.length > 0 && (
        <div className="space-y-4 animate-fade-up">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              {videos.length} Videos Found
            </h2>
            <Button onClick={handleDownloadAll} variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Download All
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {videos.map((video) => (
              <Card key={video.id} className="video-card group">
                <div className="relative aspect-video">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  <div className="video-card-overlay flex items-center justify-center">
                    <Button
                      onClick={() => handleDownload(video.id)}
                      variant="secondary"
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                  <div className="absolute bottom-2 right-2 rounded bg-black/70 px-2 py-1 text-xs text-white">
                    {video.duration}
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="line-clamp-1 font-medium">{video.title}</h3>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
