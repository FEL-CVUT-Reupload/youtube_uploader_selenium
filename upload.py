import argparse

from youtube_uploader_selenium import Video, YouTubeUploader


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--video", required=True, help="path to the video file")
	parser.add_argument("--channel", required=True, help="ID of the YouTube channel")
	parser.add_argument("--title")
	parser.add_argument("--description")
	parser.add_argument("--playlist")
	parser.add_argument("--privacy", choices=["public", "unlisted", "private"])
	parser.add_argument("--headless", dest="headless", action="store_true", help="log in without browser interaction")
	parser.add_argument("--username", help="ČVUT username")
	parser.add_argument("--password", help="ČVUT password")
	parser.add_argument("--cookies", help="path to the directory where cookies should be saved")
	args = parser.parse_args()
	
	video = Video(args.video, args.title, args.description, args.playlist, args.privacy)
	
	with YouTubeUploader(args.headless, args.cookies, args.channel) as uploader:
		while not (login_success := uploader.login(args.username, args.password)):
			args.username = input("ČVUT username: ")
			args.password = input("ČVUT password: ")
		
		upload_success, video_id = uploader.upload(video)
	
	assert upload_success
