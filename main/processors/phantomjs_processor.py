#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from main.processors.processor_interface import Processor

__author__ = 'Iván de Paz Centeno'

MAX_PROCESS_COUNT = 5
WAIT_TIME_AFTER_GET = 5
RETRY_COUNT = 2
BINARY_DATA_EMPTY = 0
BINARY_DATA_FAIL = 3150

class PhantomJSProcessor(Processor):

    def __init__(self):
        """
        Constructor of the class.
        Initializes the webdriver for this processor.
        """
        Processor.__init__(self)
        self.driver = webdriver.PhantomJS("main/phantomjs/phantomjs")  # the normal SE phantomjs binding
        self.driver.set_window_size(1024, 768)
        self.process_count = 0

    def process(self, url_wrapper):
        """
        Retrieves a request (any url) and returns a screenshot in binary format.
        :param url: URL to process.
        :return: binary data in PNG format of the screenshot.
        """
        url = str(url_wrapper)
        retries = 0
        binary_data = b""

        while retries < RETRY_COUNT and (len(binary_data) == BINARY_DATA_EMPTY or len(binary_data) == BINARY_DATA_FAIL):
            print("Processing {}".format(url))
            self.driver.get(url)  # whatever reachable url
            time.sleep(WAIT_TIME_AFTER_GET)
            binary_data = self.driver.get_screenshot_as_png()
            if len(binary_data) == 3150:
                print("URL {} did not apparently report a valid screenshot. Retrying... ({}/{})".format(url, retries,
                                                                                                        RETRY_COUNT))
            self.driver.back()
            print("Processed {}".format(url))
            self.process_count += 1

            if self.process_count % MAX_PROCESS_COUNT == 0:
                self.restart()

            retries += 1

        return binary_data

    def restart(self):
        print("Reseted one.")
        self.driver.quit()
        self.driver = webdriver.PhantomJS("main/phantomjs/phantomjs")  # the normal SE phantomjs binding
        self.driver.set_window_size(1024, 768)

    def __del__(self):
        self.driver.quit()
