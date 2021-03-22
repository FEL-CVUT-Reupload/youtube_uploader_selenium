"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc."""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from selenium_firefox.firefox import By, Firefox, Keys

from .Constant import *



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
			print("WARNING: The video title was not provided")
			self.title = os.path.basename(self.filename)
			print(f"The video title was set to {self.title}")



class YouTubeUploader:
	"""A class for uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc"""
	
	
	def __init__(self, headless: bool, cookies_path: str, channel: str) -> None:
		self.channel = channel
		cookies_path = str(Path(cookies_path)) if cookies_path else str(Path.cwd())
		assert os.path.isdir(cookies_path), f"Directory '{cookies_path}' does not exist!"
		self.browser = Firefox(cookies_path, cookies_path, headless=headless)
	
	
	def __enter__(self):
		return self
	
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.browser.driver.quit()
	
	
	def login(self, username: Optional[str], password: Optional[str]) -> bool:
		self.browser.get(Constant.YOUTUBE_URL)
		
		if self.browser.has_cookies_for_current_website():
			print("Loading cookies")
			self.browser.load_cookies()
		
		YOUTUBE_STUDIO_URL = f"https://studio.youtube.com/channel/{self.channel}"
		self.browser.get(YOUTUBE_STUDIO_URL)
		
		if self.browser.driver.current_url == YOUTUBE_STUDIO_URL:
			print("Logged in!")
			return True
		
		if None in {username, password} or "" in {username.strip(), password.strip()}:
			print("Username or password not provided!")
			return False
		
		# [G] fill in the username (email)
		print(f"Sending keys: email: '{username}@fel.cvut.cz'")
		email_field = self.browser.find(By.ID, "identifierId")
		email_field.click()
		email_field.clear()
		email_field.send_keys(f"{username}@fel.cvut.cz")
		
		# [G] click 'next' button
		print("Click: next")
		self.browser.find(By.ID, "identifierNext").click()
		
		if self.browser.find(By.XPATH, Constant.G_LOGIN_FAILED, timeout=2) is not None:
			print("Invalid username!")
			return False
		
		# [SSO] fill in the username
		print(f"Sending keys: SSO username: '{username}'")
		sso_username_field = self.browser.find(By.ID, "username")
		sso_username_field.click()
		sso_username_field.clear()
		sso_username_field.send_keys(username)
		
		# [SSO] fill in the password
		print(f"Sending keys: SSO password: '<hidden>'")
		sso_password_field = self.browser.find(By.ID, "password")
		sso_password_field.click()
		sso_password_field.clear()
		sso_password_field.send_keys(password)
		
		# [SSO] click 'SSO login' button
		print("Click: SSO login")
		self.browser.find(By.NAME, "_eventId_proceed").click()
		
		if self.browser.find(By.CLASS_NAME, "error-message", timeout=2) is not None:
			print("Invalid username or password!")
			return False
		
		print("Waiting for Google login...")
		if self.browser.find(By.ID, "upload-icon", timeout=20) is None:
			print("Login timeout!")
			return False
		
		if self.browser.driver.current_url != YOUTUBE_STUDIO_URL:
			print("Login failed!")
			return False
		
		# save cookies
		print("Saving cookies")
		self.browser.save_cookies()
		
		print("Logged in!")
		return True
	
	
	
	def upload(self, video: Video) -> (bool, Optional[str]):
		self.browser.get(f"https://studio.youtube.com/channel/{self.channel}")
		
		print("Click: upload")
		self.browser.find(By.ID, "upload-icon").click()
		
		print(f"Attaching video: '{video.filename}'")
		self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(os.path.abspath(video.filename))
		
		if video.description:
			print(f"Sending keys: video description: '{video.description}'")
			description_field = self.browser.find(By.XPATH, Constant.DESCRIPTION_CONTAINER)
			description_field.click()
			description_field.clear()
			description_field.send_keys(video.description)
		
		if video.playlist:
			print("Click: playlist dropdown")
			self.browser.find(By.CLASS_NAME, "dropdown").click()
			
			# TODO: playlist ID
			print("Selecting the playlist")
			playlists = self.browser.find_all(By.CSS_SELECTOR, "label.style-scope.ytcp-checkbox-group.ytcp-checkbox-label")
			
			for playlist in playlists:
				playlist_name = self.browser.find(By.CSS_SELECTOR, "span.label.label-text", playlist).text
				if video.playlist == playlist_name:
					print(f"Click: playlist checkbox: '{playlist_name}'")
					self.browser.find(By.CSS_SELECTOR, "ytcp-checkbox-lit.ytcp-checkbox-group", playlist).click()
					break
			else:  # create a new playlist
				print("Playlist not found in the list, creating a new one")
				self.browser.find(By.CLASS_NAME, "new-playlist-button").click()
				
				create_playlist_form = self.browser.find(By.ID, "create-playlist-form")
				
				print(f"Sending keys: playlist name: '{video.playlist}'")
				textarea = self.browser.find(By.TAG_NAME, "textarea", element=create_playlist_form)
				textarea.click()
				textarea.clear()
				textarea.send_keys(video.playlist)
				
				print("Click: visibility dropdown")
				self.browser.find(By.CLASS_NAME, "visibility", element=create_playlist_form).click()
				
				print(f"Click: visibility: '{video.privacy.upper()}'")
				self.browser.find(By.CLASS_NAME, f'paper-item[test-id="{video.privacy.upper()}"]', element=create_playlist_form).click()
				
				print("Click: create playlist")
				self.browser.find(By.CLASS_NAME, "create-playlist-button").click()
			
			print("Click: done")
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find(By.CLASS_NAME, "done-button").click()
		
		print("Click: not made for kids")
		kids_section = self.browser.find(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
		self.browser.find(By.ID, Constant.RADIO_LABEL, kids_section).click()
		
		print(f"Sending keys: video title: '{video.title}'")
		title_field = self.browser.find(By.ID, Constant.TEXTBOX, timeout=30)
		title_field.click()
		title_field.clear()
		title_field.send_keys(Keys.CONTROL + 'a')
		title_field.send_keys(video.title)
		
		for _ in range(3):
			print("Click: next")
			self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
		
		if video.privacy:
			print(f"Click: visibility: '{video.privacy.upper()}'")
			privacy_button = self.browser.find(By.NAME, video.privacy.upper())
			self.browser.find(By.ID, Constant.RADIO_LABEL, privacy_button).click()
		
		time.sleep(Constant.USER_WAITING_TIME)
		video_id = self.__get_video_id()
		print(f"Video link: https://youtu.be/{video_id}")
		
		container = self.browser.find(By.CSS_SELECTOR, ".left-button-area.style-scope.ytcp-uploads-dialog")
		
		while True:
			texts = [a.text for a in self.browser.find_all(By.CLASS_NAME, "progress-label", container)]
			print(f'\r{texts[-1]}\033[K', end="")
			if any(substring in element for substring in {"complete", "dokončeno"} for element in texts):
				print()
				time.sleep(Constant.USER_WAITING_TIME)
				break
			else:
				time.sleep(0.5)
		
		print("Click: done")
		done_button = self.browser.find(By.ID, Constant.DONE_BUTTON)
		
		# Catch such error as
		# "File is a duplicate of a video you have already uploaded"
		if done_button.get_attribute('aria-disabled') == 'true':
			error_message = self.browser.find(By.XPATH, Constant.ERROR_CONTAINER).text
			print(f"Upload ERROR: {error_message}")
			return False, None
		
		done_button.click()
		self.browser.get(Constant.YOUTUBE_URL)
		return True, video_id
	
	
	def __get_video_id(self) -> Optional[str]:
		video_id = None
		
		try:
			video_url_container = self.browser.find(By.XPATH, Constant.VIDEO_URL_CONTAINER)
			video_url_element = self.browser.find(By.XPATH, Constant.VIDEO_URL_ELEMENT, element=video_url_container)
			video_id = video_url_element.get_attribute(Constant.HREF).split('/')[-1]
		except:
			print(f"ERROR: could not find video_id")
		
		return video_id
