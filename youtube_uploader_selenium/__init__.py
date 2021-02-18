"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc."""

import json
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Optional

from selenium_firefox.firefox import By, Firefox, Keys

from .Constant import *

logging.basicConfig()



def load_metadata(metadata_json_path: Optional[str] = None) -> DefaultDict[str, str]:
	if metadata_json_path is None:
		return defaultdict(str)
	with open(metadata_json_path) as metadata_json_file:
		return defaultdict(str, json.load(metadata_json_file))



class YouTubeUploader:
	"""A class for uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc"""
	
	
	def __init__(self, video_path: str, metadata_json_path: Optional[str] = None) -> None:
		self.video_path = video_path
		
		metadata_dict = load_metadata(metadata_json_path)
		self.meta_title = metadata_dict[Constant.VIDEO_TITLE]
		self.meta_description = metadata_dict[Constant.VIDEO_DESCRIPTION]
		
		current_working_dir = str(Path.cwd())
		self.browser = Firefox(current_working_dir, current_working_dir)
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)
		self.__validate_inputs()
	
	
	def __validate_inputs(self):
		if not self.meta_title:
			self.logger.warning("The video title was not found in a metadata file")
			self.meta_title = Path(self.video_path).stem
			self.logger.warning("The video title was set to {}".format(Path(self.video_path).stem))
		if not self.meta_description:
			self.logger.warning("The video description was not found in a metadata file")
	
	
	def upload(self):
		try:
			self.__login()
			return self.__upload()
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
			self.logger.info('Please sign in and then press enter')
			input()
			self.browser.get(Constant.YOUTUBE_URL)
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.save_cookies()
	
	
	def __upload(self) -> (bool, Optional[str]):
		self.browser.get(Constant.YOUTUBE_URL)
		time.sleep(Constant.USER_WAITING_TIME)
		self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
		time.sleep(Constant.USER_WAITING_TIME)
		absolute_video_path = str(Path.cwd() / self.video_path)
		self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(absolute_video_path)
		self.logger.debug('Attached video {}'.format(self.video_path))
		title_field = self.browser.find(By.ID, Constant.TEXTBOX, timeout=10)
		title_field.click()
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.clear()
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.send_keys(Keys.COMMAND + 'a')
		time.sleep(Constant.USER_WAITING_TIME)
		title_field.send_keys(self.meta_title)
		self.logger.debug('The video title was set to \"{}\"'.format(self.meta_title))
		
		video_description = self.meta_description
		if video_description:
			description_container = self.browser.find(By.XPATH, Constant.DESCRIPTION_CONTAINER)
			description_field = self.browser.find(By.ID, Constant.TEXTBOX, element=description_container)
			description_field.click()
			time.sleep(Constant.USER_WAITING_TIME)
			description_field.clear()
			time.sleep(Constant.USER_WAITING_TIME)
			description_field.send_keys(self.meta_description)
			self.logger.debug(
				'The video description was set to \"{}\"'.format(self.meta_description))
		
		kids_section = self.browser.find(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
		self.browser.find(By.ID, Constant.RADIO_LABEL, kids_section).click()
		self.logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		self.logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))
		
		public_main_button = self.browser.find(By.NAME, Constant.PUBLIC_BUTTON)
		self.browser.find(By.ID, Constant.RADIO_LABEL, public_main_button).click()
		self.logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))
		
		video_id = self.__get_video_id()
		
		status_container = self.browser.find(By.XPATH, Constant.STATUS_CONTAINER)
		while True:
			in_process = status_container.text.find(Constant.UPLOADED) != -1
			if in_process:
				time.sleep(Constant.USER_WAITING_TIME)
			else:
				break
		
		done_button = self.browser.find(By.ID, Constant.DONE_BUTTON)
		
		# Catch such error as
		# "File is a duplicate of a video you have already uploaded"
		if done_button.get_attribute('aria-disabled') == 'true':
			error_message = self.browser.find(By.XPATH, Constant.ERROR_CONTAINER).text
			self.logger.error(error_message)
			return False, None
		
		done_button.click()
		self.logger.debug("Published the video with video_id = {}".format(video_id))
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
			self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
			pass
		return video_id
	
	
	def __quit(self):
		self.browser.driver.quit()
