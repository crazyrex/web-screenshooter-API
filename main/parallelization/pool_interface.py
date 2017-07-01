#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from multiprocessing import Manager
from multiprocessing.pool import Pool
from multiprocessing import Lock
from queue import Empty

__author__ = 'Iván de Paz Centeno'


processor = None
abort_dict = None

def process(queue_element):
    """
    Generic process function.
    The pool process is going to execute this function on its own thread.
    :param queue_element: element extracted from the queue.
    :return: search engine request result.
    """
    global processor, abort_dict

    # We fetch the search variables from the queue element
    request = queue_element[0]

    is_aborted = abort_dict.get(request, False)

    try:
        if is_aborted:
            raise Exception("Request is aborted.")

        retrieved_result = processor.process(request)

    except Exception as ex:
        retrieved_result = None

    return [request, retrieved_result]


class PoolInterface(object):
    """
    Pool processes for a given operation.
    Allows to process something in parallel.
    """

    def __init__(self, processor_class, pool_limit=1, processor_class_init_args=None):

        self.manager = Manager()

        self.processing_queue = self.manager.Queue()
        self.abort_dict = self.manager.dict()

        self.pool = Pool(processes=pool_limit, initializer=self._init_pool_worker,
                         initargs=[processor_class, self.abort_dict, processor_class_init_args])

        self.pool_limit = pool_limit
        self.processes_free = pool_limit
        self._stop_processing = False
        self.lock_process_variable = Lock()

    @staticmethod
    def _init_pool_worker(processor_class, _abort_dict, processor_class_init_args=None):
        """
        Initializes the worker thread. Each worker of the pool has its own firefox and display instance.
        :return:
        """
        global processor, abort_dict

        if processor_class_init_args is None:
            processor_class_init_args = []

        if len(processor_class_init_args) > 0:
            processor = processor_class(*processor_class_init_args)
        else:
            processor = processor_class()

        abort_dict = _abort_dict

    def do_stop(self):
        with self.lock_process_variable:
            self._stop_processing = True

    def _stop_requested(self):
        with self.lock_process_variable:
            stop_requested = self._stop_processing

        return stop_requested

    def queue_request(self, request):
        """
        put a request in the request queue.
        :param request: request acceptable by the processor
        :return:
        """
        self.processing_queue.put([request, self.abort_dict])

    def get_processes_free(self):

        with self.lock_process_variable:
            processes_free = self.processes_free

        return processes_free

    def housekeep_abort_dict(self):
        with self.lock_process_variable:
            if self.processes_free == self.pool_limit and len(self.abort_dict) > 0:
                self.abort_dict.clear()

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

            self.housekeep_abort_dict()

    def _process_finished(self, wrapped_result):
        """
        Callback when the worker's thread is finished.
        This is an internal callback.
        It will call process_finished method if available to notify the result.
        :param wrapped_result:
        :return:
        """
        request = wrapped_result[0]

        try:
            del self.abort_dict[request]
        except KeyError:
            pass

        self.process_freed()

        if hasattr(self, 'process_finished'):
            self.process_finished(wrapped_result)

        return None

    def terminate(self):
        """
        Finishes safely the pool.
        :return:
        """
        self.pool.terminate()
        self.pool.join()

    def abort_request(self, request):
        try:
            self.abort_dict[request] = True
        except KeyError:
            pass

    def is_request_aborted(self, request):

        result = self.abort_dict.get(request, False)

        return result