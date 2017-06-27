#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from main.processors.processor_interface import Processor

__author__ = 'Iván de Paz Centeno'


class PhantomJSProcessor(Processor):

    def __init__(self):
        """
        Constructor of the class.
        Initializes the webdriver for this processor.
        """
        Processor.__init__(self)
        self.driver = webdriver.PhantomJS("main/phantomjs/phantomjs")  # the normal SE phantomjs binding
        self.driver.set_window_size(1024, 768)

    def process(self, url, extra_data=None):
        """
        Retrieves a request (any url) and returns a screenshot in binary format.
        :param url: URL to process.
        :param promise: object containing metadata for this request. For example, whether this process should take
        place or not.
        :return: binary data in PNG format of the screenshot.
        """
        print("Processing {}".format(url))
        self.driver.get(url)  # whatever reachable url
        binary_data = self.driver.get_screenshot_as_png()
        self.driver.back()
        print("Processed {}".format(url))
        return binary_data

    def __del__(self):
        self.driver.quit()
