import re
from json import loads
from pytube import YouTube, Playlist
from pytube.exceptions import RegexMatchError


class YouTubeProcessor:
    def __init__(self, url: str):
        self.url = url
        self.yt = None
        self.playlist = None

    def get_description(self, video: YouTube) -> str | None:
        """Extract the video description from YouTube's HTML."""

        watch_html = video.watch_html
        if watch_html is None:
            print("Error retrieving description: watch_html is None.")
            return None

        short_description_start = watch_html.find('"shortDescription":"')
        if short_description_start == -1:
            print("Description not found in video HTML.")
            return None

        # Calculate the starting index of the actual description text
        short_description_start += len('"shortDescription":"')
        description = '"'

        i = short_description_start
        while i < len(watch_html):
            char = watch_html[i]
            description += char
            i += 1

            if char == "\\":  # Handle escaped characters
                if i < len(watch_html):  # Ensure there's a next character to escape
                    description += watch_html[i]
                    i += 1
            elif char == '"':  # End of description
                break

        try:
            return loads(description)
        except Exception as e:
            print(f"Error parsing description JSON: {e}")
            return None

    def has_timestamps(self, video: YouTube) -> bool:
        """Check if the video description contains timestamps."""
        description = self.get_description(video)
        if not description:
            return False

        # Regex pattern to match timestamps like 0:00, 12:34, 2:00:20, etc.
        time_pattern = r"\b[0-2]?\d:[0-5]\d(?::[0-5]\d)?\b"
        return re.search(time_pattern, description) is not None

    def process_video(self, video: YouTube) -> None:
        """Process a single video and print its type."""
        if self.has_timestamps(video):
            print(f"Playlist Video: {video.title}")
        else:
            print(f"Video: {video.title}")

    def process_playlist(self, playlist: Playlist) -> None:
        """Process a playlist and print details of each video."""
        print(f"Playlist: {playlist.title}")
        for video_url in playlist.video_urls:
            video = YouTube(video_url)
            self.process_video(video)

    def process(self) -> None:
        """Determine whether the URL is a video or playlist and process accordingly."""
        try:
            self.yt = YouTube(self.url)
            self.process_video(self.yt)
        except RegexMatchError:
            try:
                self.playlist = Playlist(self.url)
                self.process_playlist(self.playlist)
            except Exception as e:
                print(f"Failed to process playlist: {e}")
        except Exception as e:
            print(f"Error encountered: {e}")


# Example usage
if __name__ == "__main__":
    test_urls = [
        "https://youtube.com/playlist?list=PL_VgE-UO0wuwrd5dLSHOm_PMpOn7yzgt6&si=3QaO3FCKlt56zyBX",
        "https://www.youtube.com/watch?v=qQzvkyGHtl0",
        "https://www.youtube.com/watch?v=DXKojYz25Gw"
    ]

    for url in test_urls:
        print(f"Processing URL: {url}")
        processor = YouTubeProcessor(url)
        processor.process()
        print("-" * 50)