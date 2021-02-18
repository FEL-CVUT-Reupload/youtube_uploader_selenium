import argparse
from pathlib import Path

from youtube_uploader_selenium import Video, YouTubeUploader



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
	
	video = Video(Path(args.video), args.title, args.description, args.playlist, args.privacy)
	uploader = YouTubeUploader()
	
	# if not uploader.logged_in():
	# 	uploader.login(args.username, args.password)
	
	was_video_uploaded, video_id = uploader.upload(video)
	assert was_video_uploaded
