"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc."""

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from selenium_firefox.firefox import By, Firefox, Keys

from .Constant import *

logging.basicConfig()

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



@dataclass
class Video:
	filename: str
	title: Optional[str] = field(default=None)
	description: Optional[str] = field(default=None)
	playlist: Optional[str] = field(default=None)
	privacy: Optional[str] = field(default=None)
	
	
	def __post_init__(self):
		if not self.title:
			_logger.warning("The video title was not provided")
			self.title = os.path.basename(self.filename)
			_logger.warning(f"The video title was set to {self.title}")



class YouTubeUploader:
	"""A class for uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc"""
	
	
	def __init__(self) -> None:
		current_working_dir = str(Path.cwd())
		self.browser = Firefox(current_working_dir, current_working_dir)
	
	
	def upload(self, video: Video):
		try:
			self.__login()
			return self.__upload(video)
		except Exception as e:
			print(e)
			self.__quit()
			raise
	
	
	def __login(self):
		self.browser.get(Constant.YOUTUBE_URL)
		time.sleep(Constant.USER_WAITING_TIME)
		
		if self.browser.has_cookies_for_current_website():
			self.browser.load_cookies()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.refresh()
		else:
			_logger.info('Please sign in and then press enter')
			input()
			self.browser.get(Constant.YOUTUBE_URL)
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.save_cookies()
	
	
	def __upload(self, video: Video) -> (bool, Optional[str]):
		self.browser.get(Constant.YOUTUBE_URL)
		time.sleep(Constant.USER_WAITING_TIME)
		self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
		time.sleep(Constant.USER_WAITING_TIME)
		self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(os.path.abspath(video.filename))
		_logger.debug('Attached video {}'.format(video.filename))
		title_field = self.browser.find(By.ID, Constant.TEXTBOX, timeout=10)
		title_field.click()
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.clear()
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.send_keys(Keys.COMMAND + 'a')
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.send_keys(video.title)
		_logger.debug('The video title was set to \"{}\"'.format(video.title))
		
		if video.description:
			description_container = self.browser.find(By.XPATH, Constant.DESCRIPTION_CONTAINER)
			description_field = self.browser.find(By.ID, Constant.TEXTBOX, element=description_container)
			description_field.click()
			time.sleep(Constant.USER_WAITING_TIME)
			description_field.clear()
			time.sleep(Constant.USER_WAITING_TIME)
			description_field.send_keys(video.description)
			_logger.debug('The video description was set to \"{}\"'.format(video.description))
		
		kids_section = self.browser.find(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
		self.browser.find(By.ID, Constant.RADIO_LABEL, kids_section).click()
		_logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		_logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		_logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))
		
		public_main_button = self.browser.find(By.NAME, Constant.PUBLIC_BUTTON)
		self.browser.find(By.ID, Constant.RADIO_LABEL, public_main_button).click()
		_logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))
		
		video_id = self.__get_video_id()
		
		status_container = self.browser.find(By.XPATH, Constant.STATUS_CONTAINER)
		while True:
			in_process = status_container.text.find(Constant.UPLOADED) != -1
			if in_process:
				time.sleep(Constant.USER_WAITING_TIME)
			else:
				break
		
		time.sleep(Constant.USER_WAITING_TIME)
		done_button = self.browser.find(By.ID, Constant.DONE_BUTTON)
		
		# Catch such error as
		# "File is a duplicate of a video you have already uploaded"
		if done_button.get_attribute('aria-disabled') == 'true':
			error_message = self.browser.find(By.XPATH, Constant.ERROR_CONTAINER).text
			_logger.error(error_message)
			return False, None
		
		done_button.click()
		_logger.debug("Published the video with video_id = {}".format(video_id))
		time.sleep(Constant.USER_WAITING_TIME)
		self.browser.get(Constant.YOUTUBE_URL)
		self.__quit()
		return True, video_id
	
	
	def __get_video_id(self) -> Optional[str]:
		video_id = None
		try:
			video_url_container = self.browser.find(By.XPATH, Constant.VIDEO_URL_CONTAINER)
			video_url_element = self.browser.find(By.XPATH, Constant.VIDEO_URL_ELEMENT, element=video_url_container)
			video_id = video_url_element.get_attribute(Constant.HREF).split('/')[-1]
		except:
			_logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
			pass
		return video_id
	
	
	def __quit(self):
		self.browser.driver.quit()
