#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from main.processors.processor_interface import Processor
from pyvirtualdisplay import Display
import time

__author__ = 'Iván de Paz Centeno'

WAIT_TIME_AFTER_GET = 5


class FirefoxProcessor(Processor):

    def __init__(self):
        """
        Constructor of the class.
        Initializes the webdriver for this processor.
        """
        Processor.__init__(self)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)

        self.virtual_browser_display = Display(visible=0, size=(800, 600))
        self.virtual_browser_display.start()

        self.driver = webdriver.Firefox(firefox_profile=profile, executable_path="main/drivers/geckodriver") 
        #self.driver.set_window_size(1024, 768)

    def process(self, url):
        """
        Retrieves a request (any url) and returns a screenshot in binary format.
        :param url: URL to process.
        :return: binary data in PNG format of the screenshot.
        """
        print("Processing {}".format(url))
        self.driver.get(url)  # whatever reachable url
        time.sleep(WAIT_TIME_AFTER_GET) # Wait 10 seconds for page to be loaded.
        binary_data = self.driver.get_screenshot_as_png()
        self.driver.back()
        print("Processed {}".format(url))
        return binary_data

    def __del__(self):
        self.driver.quit()
        self.virtual_browser_display.stop()
