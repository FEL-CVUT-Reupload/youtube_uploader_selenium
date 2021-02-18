import argparse
from typing import Optional

from youtube_uploader_selenium import YouTubeUploader



def main(video_path: str, metadata_path: Optional[str] = None):
	uploader = YouTubeUploader(video_path, metadata_path)
	was_video_uploaded, video_id = uploader.upload()
	assert was_video_uploaded



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--video",
	                    help='Path to the video file',
	                    required=True)
	parser.add_argument("--title")
	parser.add_argument("--description")
	parser.add_argument("--playlist")
	parser.add_argument("--privacy", help="public | unlisted | private")
	parser.add_argument("--username", help="Google Account username")
	parser.add_argument("--password", help="Google Account password")
	args = parser.parse_args()
	
	main(args.video, args.meta)
