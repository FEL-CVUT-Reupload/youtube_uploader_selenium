import argparse

from youtube_uploader_selenium import Video, YouTubeUploader



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--video", required=True, help="path to the video file")
	parser.add_argument("--channel", required=True, help="ID of the YouTube channel")
	parser.add_argument("--title")
	parser.add_argument("--description")
	parser.add_argument("--playlist")
	parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="private")
	parser.add_argument("--headless", dest="headless", action="store_true", help="log in without browser interaction")
	parser.add_argument("--username", help="ČVUT username")
	parser.add_argument("--password", help="ČVUT password")
	args = parser.parse_args()
	
	video = Video(args.video, args.title, args.description, args.playlist, args.privacy)
	uploader = YouTubeUploader()
	
	# if not uploader.logged_in():
	# 	uploader.login(args.username, args.password)
	
	was_video_uploaded, video_id = uploader.upload(video)
	assert was_video_uploaded
