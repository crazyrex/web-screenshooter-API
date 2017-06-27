#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from queue import Empty
from time import sleep

from main.parallelization.pool_interface import PoolInterface
from main.parallelization.result_promise import ResultPromise
from main.parallelization.service_interface import ServiceInterface, SERVICE_STOPPED

__author__ = 'Iván de Paz Centeno'


class ProcessorService(ServiceInterface, PoolInterface):

    def __init__(self, processor_class, parallel_workers=10):
        ServiceInterface.__init__(self)
        PoolInterface.__init__(self, processor_class=processor_class, pool_limit=parallel_workers)
        self.total_workers = parallel_workers
        self.promises = {}

    def queue_request(self, request, extra_data=None, callback=None):
        with self.lock:
            if request in self.promises:
                promise = self.promises[request]

            else:
                promise = ResultPromise(self.manager, request, extra_data, callback)
                self.promises[request] = promise
                PoolInterface.queue_request(self, request, extra_data)

        return promise

    def get_queue_remaining(self):

        with self.lock_process_variable:
            queue_size = self.processing_queue.qsize()

        return queue_size

    def get_workers_processing(self):

        workers_free = self.get_processes_free()
        return self.total_workers - workers_free

    def __internal_thread__(self):
        ServiceInterface.__internal_thread__(self)

        while not self.__get_stop_flag__():

            if self.get_queue_remaining() == 0 or self.get_processes_free() == 0:
                sleep(0.1)

            self.process_queue()

        self.__set_status__(SERVICE_STOPPED)

    def process_finished(self, wrapped_result):
        """
        Method invoked when the process of the processor finished processing the request.
        :param wrapped_result: parameters of the result
        :return:
        """

        try:
            request = wrapped_result[0]
            result = wrapped_result[1]
            promise = None

            with self.lock:
                if request in self.promises:
                    promise = self.promises[request]
                    del self.promises[request]
                else:
                    raise Exception("Retrieved result for a request not listed as queued.")

            if promise is not None:
                promise.set_result(result)


        except Exception as ex:
            print(ex)

        self.process_queue()

    def clear_queue(self, batch_id=None):
        """
        Clears the current queue.
        :return:
        """
        # Let's clear the queue by pulling each element until it is empty.
        # It will throw an exception.

        if batch_id is None:
            PoolInterface.clear_queue(self)
        else:
            temp_batches = []
            invalid_promises = []

            while not self._stop_requested():
                try:
                    [request, saved_batch] = self.processing_queue.get(False)
                    if saved_batch != batch_id:
                        temp_batches.append([request, saved_batch])
                    else:
                        with self.lock:
                            if request in self.promises:
                                promise = self.promises[request]
                                del self.promises[request]
                                invalid_promises.append(promise)
                except Empty:
                    for request in temp_batches:
                        self.processing_queue.put(request)
                    break

            for promise in invalid_promises:
                promise.set_result(b'')
