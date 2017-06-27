#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import uuid
from shutil import make_archive, move, rmtree
import os
from main.parallelization.service_interface import ServiceInterface, SERVICE_STOPPED

__author__ = 'Iván de Paz Centeno'

ZIP_FOLDER = "/tmp/screenshooter_batches_zip/"

class BatchesService(ServiceInterface):

    def __init__(self, processor_service):
        ServiceInterface.__init__(self)
        self.batches = {}
        self.processor_service = processor_service
        try:
            os.mkdir(ZIP_FOLDER)
        except:
            pass

    def new_batch(self, url_list):

        callback = self._batch_element_processed

        promises = {}

        with self.lock:
            batch_keys = [-1] + list(self.batches.keys())
            batch_id = max(batch_keys)
            batch_id += 1
            uri = "/tmp/batch_folder_{}/".format(batch_id)
            try:
                os.mkdir(uri)
            except:
                pass

            for url in url_list:
                promises[url] = self.processor_service.queue_request(url, batch_id, callback)

            self.batches[batch_id] = {"uri": uri, "url_processed": [], "url_pending": url_list, "zip_uri": "", "promises": promises, "url_uri_map": {}}

        return batch_id

    def _batch_element_processed(self, batch_element_promise):
        result = batch_element_promise.get_result()
        original = batch_element_promise.get_original()
        batch_id = batch_element_promise.get_extra_data()

        with self.lock:
            father_uri = self.batches[batch_id]["uri"]

        uri = os.path.join(father_uri, "{}.png".format(original.replace("://", "----").replace("/", "--")))
        self._save_screenshot(result, uri)

        with self.lock:
            del self.batches[batch_id]["promises"][original]
            self.batches[batch_id]["url_processed"].append(original)
            self.batches[batch_id]["url_uri_map"][original] = uri

    @staticmethod
    def _save_screenshot(binary_data, filename):
        if not filename.endswith(".png"):
            filename += ".png"

        with open(filename, "wb") as file:
            file.write(binary_data)

    def remove_batch(self, batch_id):
        if not str(batch_id).isdigit():
            return

        batch_id = int(batch_id)

        with self.lock:
            rmtree("/tmp/batch_folder_{}".format(batch_id))
            os.remove(self.batches[batch_id]['zip_uri'])
            del self.batches[batch_id]

    def get_batch_zip_bytes(self, batch_id):
        if not str(batch_id).isdigit():
            return ""

        with self.lock:
            zip_uri = self.batches[batch_id]['zip_uri']

        with open(zip_uri) as f:
            zip_content = f.read()

        return zip_content

    def get_batch_zip_uri(self, batch_id):
        if not str(batch_id).isdigit():
            return ""

        batch_id = int(batch_id)

        with self.lock:
            zip_uri = self.batches[batch_id]['zip_uri']

        return zip_uri

    def get_processed_percentage(self, batch_id):
        if not str(batch_id).isdigit():
            return

        batch_id = int(batch_id)

        with self.lock:
            batch = self.batches[batch_id]

        processed_percentage = round(len(batch["url_processed"]) / len(batch["url_pending"]) * 100)
        is_zipped = batch["zip_uri"] != ""
        return processed_percentage, is_zipped

    def get_batches_ids(self):
        with self.lock:
            batches_ids = list(self.batches.keys())

        return batches_ids

    @staticmethod
    def _zip_file(folder):
        filename = "{}".format(str(uuid.uuid4()))

        make_archive(filename, 'zip', root_dir=folder)

        filename = "{}.zip".format(filename)
        dst = os.path.join(ZIP_FOLDER, filename)

        move(filename, dst)

        return dst

    def __internal_thread__(self):
        ServiceInterface.__internal_thread__(self)

        while not self.__get_stop_flag__():
            try:

                with self.lock:
                    batch_ids = list(self.batches.keys())

                for batch_id in batch_ids:
                    completion_percentage, is_zipped = self.get_processed_percentage(batch_id)

                    if completion_percentage == 100 and not is_zipped:
                            with self.lock:

                                if batch_id not in self.batches:
                                    continue

                                batch_data = self.batches[batch_id]

                            url_uri_map = batch_data["url_uri_map"]
                            father_uri = batch_data["uri"]

                            with open(os.path.join(father_uri, "content.json"), "w") as f:
                                json.dump(url_uri_map, f, indent=4)

                            zip_uri = self._zip_file(father_uri)

                            with self.lock:

                                if batch_id not in self.batches:
                                    continue

                                self.batches[batch_id]["zip_uri"] = zip_uri
            except:
                # We don't care if a key has been removed from the list, next while iteration will take rid of it.
                pass

        self.__set_status__(SERVICE_STOPPED)

    def __del__(self):
        rmtree(ZIP_FOLDER)