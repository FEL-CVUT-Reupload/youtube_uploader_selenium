class Constant:
	"""A class for storing constants for YoutubeUploader class"""
	YOUTUBE_URL = 'https://www.youtube.com'
	YOUTUBE_STUDIO_URL = 'https://studio.youtube.com'
	YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
	USER_WAITING_TIME = 1
	VIDEO_TITLE = 'title'
	VIDEO_DESCRIPTION = 'description'
	DESCRIPTION_CONTAINER = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-details/div/ytcp-uploads-basics/ytcp-mention-textbox[2]/ytcp-form-input-container/div[1]/div[2]/ytcp-mention-input/div'
	TEXTBOX = 'textbox'
	TEXT_INPUT = 'text-input'
	RADIO_LABEL = 'radioLabel'
	NOT_MADE_FOR_KIDS_LABEL = 'NOT_MADE_FOR_KIDS'
	NEXT_BUTTON = 'next-button'
	PRIVATE_BUTTON = 'PRIVATE'
	UNLISTED_BUTTON = 'UNLISTED'
	PUBLIC_BUTTON = 'PUBLIC'
	VIDEO_URL_CONTAINER = "//span[@class='video-url-fadeable style-scope ytcp-video-info']"
	VIDEO_URL_ELEMENT = "//a[@class='style-scope ytcp-video-info']"
	HREF = 'href'
	UPLOADED = 'Uploading'
	ERROR_CONTAINER = '//*[@id="error-message"]'
	VIDEO_NOT_FOUND_ERROR = 'Could not find video_id'
	DONE_BUTTON = 'done-button'
	INPUT_FILE_VIDEO = "//input[@type='file']"
