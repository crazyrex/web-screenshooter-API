#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from multiprocessing import Manager
from multiprocessing.pool import Pool
from multiprocessing import Lock
from queue import Empty

__author__ = 'Iván de Paz Centeno'


processor = None


def process(queue_element):
    """
    Generic process function.
    The pool process is going to execute this function on its own thread.
    :param queue_element: element extracted from the queue.
    :return: search engine request result.
    """
    global processor

    # We fetch the search variables from the queue element
    request = queue_element[0]
    extra_data = queue_element[1]

    try:
        retrieved_result = processor.process(request, extra_data)

    except Exception as ex:
        retrieved_result = None
        print(ex)

    return [request, retrieved_result, extra_data]


class PoolInterface(object):
    """
    Pool processes for a given operation.
    Allows to process something in parallel.
    """

    def __init__(self, processor_class, pool_limit=1):

        self.manager = Manager()

        self.processing_queue = self.manager.Queue()

        self.pool = Pool(processes=pool_limit, initializer=self._init_pool_worker,
                         initargs=[processor_class])

        self.processes_free = pool_limit
        self._stop_processing = False
        self.lock_process_variable = Lock()

    @staticmethod
    def _init_pool_worker(processor_class):
        """
        Initializes the worker thread. Each worker of the pool has its own firefox and display instance.
        :return:
        """
        global processor

        processor = processor_class()

    def do_stop(self):
        with self.lock_process_variable:
            self._stop_processing = True

    def _stop_requested(self):
        with self.lock_process_variable:
            stop_requested = self._stop_processing

        return stop_requested

    def queue_request(self, request, extra_data=None):
        """
        put a request in the request queue.
        :param request: request acceptable by the processor
        :return:
        """
        self.processing_queue.put([request, extra_data])

    def get_processes_free(self):

        with self.lock_process_variable:
            processes_free = self.processes_free

        return processes_free

    def take_process(self):

        with self.lock_process_variable:
            self.processes_free -= 1

    def process_freed(self):

        with self.lock_process_variable:
            self.processes_free += 1

    def process_queue(self):
        """
        Processes the queue until all the processes are busy or until the queue is empty
        :return:
        """

        while self.get_processes_free() > 0 and not self._stop_requested():
            try:
                queue_element = self.processing_queue.get(False)
                self.take_process()

                result = self.pool.apply_async(process, args=(queue_element,), callback=self._process_finished)

            except Empty:
                break

    def _process_finished(self, wrapped_result):
        """
        Callback when the worker's thread is finished.
        This is an internal callback.
        It will call process_finished method if available to notify the result.
        :param wrapped_result:
        :return:
        """
        self.process_freed()

        if hasattr(self, 'process_finished'):
            self.process_finished(wrapped_result)

        return None

    def clear_queue(self):
        """
        Clears the current queue.
        :return:
        """
        # Let's clear the queue by pulling each element until it is empty.
        # It will throw an exception.

        while not self._stop_requested():
            try:
                self.processing_queue.get(False)
            except Empty:
                break

    def terminate(self):
        """
        Finishes safely the pool.
        :return:
        """
        self.pool.terminate()
        self.pool.join()
