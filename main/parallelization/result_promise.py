#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Ivan de Paz Centeno"


class ResultPromise(object):
    """
    Promise object
    Wraps a result in order to allow storage of a result between different threads.
    Also, it allows to wait for the result to be ready.
    """

    def __init__(self, multithread_manager, original, extra_data, listener_func=None):
        """
        Initializes the result container.
        """

        self.original = original
        self.extra_data = extra_data
        self.result = None
        self.lock = multithread_manager.Lock()
        self.event = multithread_manager.Event()
        self.listener_func = listener_func

    def set_result(self, result):
        """
        Setter for the resource.
        """

        with self.lock:
            self.result = result

        self.event.set()

        if self.listener_func is not None:
            self.listener_func(self)

    def set_listener(self, listener_func):
        self.listener_func = listener_func

    def get_result(self):
        """
        Getter for the result. It will wait until the result is ready.
        :return: Resource object.
        """

        self.event.wait()

        with self.lock:
            result = self.result

        return result

    def get_original(self):
        return self.original

    def get_extra_data(self):
        return self.extra_data