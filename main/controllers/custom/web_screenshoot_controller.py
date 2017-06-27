#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO

from flask import jsonify, request, send_file
from main.controllers.controller import route, Controller
from main.exceptions.invalid_request import InvalidRequest

__author__ = "Ivan de Paz Centeno"


class WebScreenshootController(Controller):
    """
    Controller for /web-screenshot/ URL.
    """

    def __init__(self, flask_web_app, available_services, config):
        """
        Constructor of the controller.
        :param flask_web_app: web app from Flask already initialized.
        :param available_services: list of services filtered to be compatible with this controller.
        :param config: config object containing all the service definitions.
        """
        Controller.__init__(self, flask_web_app, available_services, config)

        self.exposed_methods += [
            self.make_web_screenshot,
            self.batch_web_screenshot,
            self.get_batch_status,
            self.remove_batch,
            self.get_batch,
            self.get_batches
        ]

        self._init_exposed_methods()

    @route("/web-screenshot/make", methods=['PUT'])
    def make_web_screenshot(self):
        """
        Retrieves the screenshot for the specified page
        """
        json_request = request.get_json(force=True, silent=True, cache=False)

        try:
            url = json_request['url']

        except Exception as ex:
            raise InvalidRequest("url is missing in the request JSON.")

        if not (url.lower().startswith("http://") or url.lower().startswith("https://")):
            raise InvalidRequest("Specified URL is not valid, must start with http:// or https://")

        service = self.available_services['web_screenshoot_processor']

        promise = service.queue_request(url)

        binary_result = promise.get_result()

        img_io = BytesIO(binary_result)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')

    @route("/web-screenshot/batches", methods=['POST'])
    def batch_web_screenshot(self):

        json_request = request.get_json(force=True, silent=True, cache=False)

        try:
            urls = json_request['urls']

        except Exception as ex:
            raise InvalidRequest("url is missing in the request JSON.")

        service = self.available_services['batch_screenshoot_processor']

        if len(urls) == 0:
            raise InvalidRequest("Required at least 1 URL in the 'url' list")

        batch_id = service.new_batch(urls)

        return jsonify({"batch_id": batch_id})

    @route("/web-screenshot/batches/<batch_id>/status", methods=['GET'])
    def get_batch_status(self, batch_id):

        service = self.available_services['batch_screenshoot_processor']

        percentage, is_zipped = service.get_processed_percentage(batch_id)

        return jsonify({'percentage_completed': percentage, 'is_zipped': is_zipped})

    @route("/web-screenshot/batches/<batch_id>", methods=['DELETE'])
    def remove_batch(self, batch_id):

        service = self.available_services['batch_screenshoot_processor']

        try:
            service.remove_batch(batch_id)
        except:
            raise InvalidRequest("Batch ID not valid or not available for removing.")

        return jsonify({'status': "done"})

    @route("/web-screenshot/batches/<batch_id>", methods=['PATCH'])
    def close_batch(self, batch_id):

        service = self.available_services['batch_screenshoot_processor']

        try:
            service.cancel_batch(batch_id)
        except:
            raise InvalidRequest("Batch ID not valid or not available for cancelling.")

        return jsonify({'status': "done"})

    @route("/web-screenshot/batches/<batch_id>", methods=['GET'])
    def get_batch(self, batch_id):
        service = self.available_services['batch_screenshoot_processor']

        try:
            zip_uri = service.get_batch_zip_uri(batch_id)
            percentage, is_zipped = service.get_processed_percentage(batch_id)
        except:
            raise InvalidRequest("Batch ID not valid or not available for cancelling.")

        if not is_zipped:
            raise InvalidRequest("Batch is not ready yet.")

        return send_file(zip_uri)

    @route("/web-screenshot/batches", methods=['GET'])
    def get_batches(self):
        service = self.available_services['batch_screenshoot_processor']
        batches_ids = service.get_batches_ids()
        return jsonify(batches_ids)