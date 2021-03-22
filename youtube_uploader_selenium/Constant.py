class Constant:
	"""A class for storing constants for YoutubeUploader class"""
	YOUTUBE_URL = "https://www.youtube.com/feed/library"
	YOUTUBE_STUDIO_URL = 'https://studio.youtube.com'
	YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
	USER_WAITING_TIME = 1
	VIDEO_TITLE = 'title'
	VIDEO_DESCRIPTION = 'description'
	DESCRIPTION_CONTAINER = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-mention-textbox/ytcp-form-input-container/div[1]/div[2]/ytcp-mention-input/div'
	G_LOGIN_FAILED = "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[2]/div[2]/div"
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
	ERROR_CONTAINER = '//*[@id="error-message"]'
	DONE_BUTTON = 'done-button'
	INPUT_FILE_VIDEO = "//input[@type='file']"
