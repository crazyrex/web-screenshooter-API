#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread, Lock

__author__ = 'Iván de Paz Centeno'

SERVICE_RUNNING = 0
SERVICE_STOPPED = 1


class ServiceInterface(object):

    def __init__(self):
        self.__do_stop = False
        self.__status = SERVICE_STOPPED
        self.lock = Lock()

    def __reset_thread__(self):
        self.worker_thread = Thread(target=self.__internal_thread__)

    def __set_stop_flag__(self, value=True):
        """
        Sets thread-safely the value of the stop flag.
        Use this method instead of accessing the __do_stop flag directly

        :param value:
        """
        with self.lock:
            self.__do_stop = value

    def __get_stop_flag__(self):
        """
        Retrieves the stop flag value thread-safely.
        Use this method instead of accessing the __do_stop flag directly.

        :return:
        """
        with self.lock:
            stop_flag = self.__do_stop

        return stop_flag

    def __set_status__(self, status_value):
        """
        Sets thread-safely the value of the status.
        Use this method instead of accessing the __status attribute directly

        :param value: SERVICE_RUNNING or SERVICE_STOPPED
        """
        with self.lock:
            self.__status = status_value

    def __get_status__(self):
        """
        Retrieves the status value thread-safely.
        Use this method instead of accessing the __status attribute directly.

        :return: Status of the service. May be SERVICE_RUNNING or SERVICE_STOPPED
        """
        with self.lock:
            status = self.__status

        return status

    def get_status(self):
        return self.__get_status__()

    def start(self):
        """
        Starts the service in background.

        """
        if self.get_status() <= SERVICE_RUNNING:
            return

        self.__set_stop_flag__(False)
        self.__reset_thread__()
        self.worker_thread.start()

        self.__set_status__(SERVICE_RUNNING)

    def stop(self, wait_for_finish=True):
        """
        Stops the service from working on background.

        :type wait_for_finish: bool   specify if the current thread must wait for the service to
        finish or not.
        """

        if self.get_status() >= SERVICE_STOPPED or self.__get_stop_flag__():
            return

        self.__set_stop_flag__(True)

        if wait_for_finish:
            self.worker_thread.join()

        self.__set_status__(SERVICE_STOPPED)

    def __internal_thread__(self):
        """
        Internal backgrounded code. Override this method with your own.
        Ensure that the 'do_stop' variable is checked to exit the loop.

        :return: None
        """
        return None
