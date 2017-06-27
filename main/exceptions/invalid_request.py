#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Ivan de Paz Centeno"


class InvalidRequest(Exception):
    """
    Exception that allows flask to notify through an HTTP code response.
    """
    def __init__(self, message, status_code=400, payload=None):
        """
        Initialization of the exception.
        :param message: message of the exception to be raised.
        :param status_code: code to answer in the HTTP response
        :param payload: extra data to append to the response's headers
        """
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        Translates the request into a dictionary.
        :return: dictionary JSON-ificable.
        """
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
