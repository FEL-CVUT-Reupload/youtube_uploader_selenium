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
		assert self.privacy in {None, "public", "unlisted", "private"}
		if not self.title:
			_logger.warning("The video title was not provided")
			self.title = os.path.basename(self.filename)
			_logger.warning(f"The video title was set to {self.title}")



class YouTubeUploader:
	"""A class for uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc"""
	
	
	def __init__(self, headless: bool, channel: str) -> None:
		self.channel = channel
		current_working_dir = str(Path.cwd())
		self.browser = Firefox(current_working_dir, current_working_dir, headless=headless)
	
	
	def login(self, username: Optional[str], password: Optional[str]):
		self.browser.get(Constant.YOUTUBE_URL)
		time.sleep(Constant.USER_WAITING_TIME * 2)
		
		if self.browser.has_cookies_for_current_website():
			self.browser.load_cookies()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.refresh()
		else:
			if None in {username, password}:
				username = input("ČVUT username: ")
				password = input("ČVUT password: ")
			
			_logger.info("Logging in...")
			
			# [YT] click 'login' button
			self.browser.find(By.ID, "action-button").click()
			time.sleep(Constant.USER_WAITING_TIME)
			
			# [G] fill in the username (email)
			email_field = self.browser.find(By.ID, "identifierId", timeout=10)
			email_field.click()
			email_field.clear()
			email_field.send_keys(f"{username}@fel.cvut.cz")
			time.sleep(Constant.USER_WAITING_TIME)
			
			# [G] click 'next' button
			self.browser.find(By.ID, "identifierNext").click()
			time.sleep(Constant.USER_WAITING_TIME)
			
			# [SSO] fill in the username
			sso_username_field = self.browser.find(By.ID, "username", timeout=10)
			sso_username_field.click()
			sso_username_field.clear()
			sso_username_field.send_keys(username)
			time.sleep(Constant.USER_WAITING_TIME)
			
			# [SSO] fill in the password
			sso_password_field = self.browser.find(By.ID, "password", timeout=10)
			sso_password_field.click()
			sso_password_field.clear()
			sso_password_field.send_keys(password)
			time.sleep(Constant.USER_WAITING_TIME)
			
			# [SSO] click 'SSO login' button
			self.browser.find(By.NAME, "_eventId_proceed").click()
			time.sleep(Constant.USER_WAITING_TIME * 5)
			
			# save cookies
			self.browser.get(Constant.YOUTUBE_URL)
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.save_cookies()
	
	
	def upload(self, video: Video):
		try:
			return self.__upload(video)
		except Exception as e:
			print(e)
			self.__quit()
			raise
	
	
	def __upload(self, video: Video) -> (bool, Optional[str]):
		self.browser.get(f"https://studio.youtube.com/channel/{self.channel}")
		time.sleep(Constant.USER_WAITING_TIME)
		
		# click 'CREATE' button
		self.browser.find(By.ID, "create-icon").click()
		time.sleep(Constant.USER_WAITING_TIME)
		
		# click 'Upload videos' button
		self.browser.find(By.ID, "text-item-0").click()
		time.sleep(Constant.USER_WAITING_TIME)
		
		self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(os.path.abspath(video.filename))
		_logger.debug('Attached video {}'.format(video.filename))
		
		title_field = self.browser.find(By.ID, Constant.TEXTBOX, timeout=20)
		time.sleep(Constant.USER_WAITING_TIME * 3)
		title_field.click()
		title_field.clear()
		title_field.send_keys(Keys.CONTROL + 'a')
		title_field.send_keys(video.title)
		_logger.debug('The video title was set to \"{}\"'.format(video.title))
		time.sleep(Constant.USER_WAITING_TIME)
		
		if video.description:
			description_container = self.browser.find(By.XPATH, Constant.DESCRIPTION_CONTAINER)
			description_field = self.browser.find(By.ID, Constant.TEXTBOX, element=description_container)
			description_field.click()
			description_field.clear()
			description_field.send_keys(video.description)
			_logger.debug('The video description was set to \"{}\"'.format(video.description))
			time.sleep(Constant.USER_WAITING_TIME)
		
		if video.playlist:
			self.browser.find(By.CLASS_NAME, "dropdown").click()
			time.sleep(Constant.USER_WAITING_TIME)
			playlists = self.browser.find_all(By.CSS_SELECTOR, "label.style-scope.ytcp-checkbox-group.ytcp-checkbox-label")
			
			for playlist in playlists:
				playlist_name = self.browser.find(By.CSS_SELECTOR, "span.label.label-text", playlist).text
				if video.playlist == playlist_name:
					# click the checkbox
					self.browser.find(By.CSS_SELECTOR, "ytcp-checkbox-lit.ytcp-checkbox-group", playlist).click()
					time.sleep(Constant.USER_WAITING_TIME)
					break
			else:  # create a new playlist
				self.browser.find(By.CLASS_NAME, "new-playlist-button").click()
				time.sleep(Constant.USER_WAITING_TIME)
				
				create_playlist_form = self.browser.find(By.ID, "create-playlist-form")
				textarea = self.browser.find(By.TAG_NAME, "textarea", element=create_playlist_form)
				textarea.click()
				textarea.clear()
				textarea.send_keys(video.playlist)
				time.sleep(Constant.USER_WAITING_TIME)
				
				self.browser.find(By.CLASS_NAME, "visibility", element=create_playlist_form).click()
				time.sleep(Constant.USER_WAITING_TIME)
				
				print(video.privacy.upper())
				self.browser.find(By.CLASS_NAME, f'paper-item[test-id="{video.privacy.upper()}"]', element=create_playlist_form).click()
				time.sleep(Constant.USER_WAITING_TIME)
				
				self.browser.find(By.CLASS_NAME, "create-playlist-button").click()
				time.sleep(Constant.USER_WAITING_TIME)
			
			self.browser.find(By.CLASS_NAME, "done-button").click()
			time.sleep(Constant.USER_WAITING_TIME)
		
		kids_section = self.browser.find(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
		self.browser.find(By.ID, Constant.RADIO_LABEL, kids_section).click()
		_logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		_logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))
		
		self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		_logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))
		
		if video.privacy:
			privacy_button_name = dict(private=Constant.PRIVATE_BUTTON, unlisted=Constant.UNLISTED_BUTTON, public=Constant.PUBLIC_BUTTON)[video.privacy]
			privacy_button = self.browser.find(By.NAME, privacy_button_name)
			self.browser.find(By.ID, Constant.RADIO_LABEL, privacy_button).click()
			_logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))
		
		video_id = self.__get_video_id()
		
		status_container = self.browser.find(By.XPATH, Constant.STATUS_CONTAINER)
		while True:
			in_process = status_container.text.find(Constant.UPLOADED) != -1
			_logger.debug(status_container.text)
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
