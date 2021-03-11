import argparse

from youtube_uploader_selenium import YouTubeUploader


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--channel", required=True, help="ID of the YouTube channel")
	parser.add_argument("--headless", dest="headless", action="store_true", help="log in without browser interaction")
	parser.add_argument("--username", required=True, help="ČVUT username")
	parser.add_argument("--password", required=True, help="ČVUT password")
	parser.add_argument("--cookies", help="path to the directory where cookies should be saved")
	args = parser.parse_args()
	
	uploader = YouTubeUploader(args.headless, args.cookies, args.channel)
	success = uploader.login(args.username, args.password)
	
	if not success:
		exit(7)
