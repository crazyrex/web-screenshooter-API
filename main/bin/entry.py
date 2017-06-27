#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, url_for, jsonify
import json
from main.controllers.controller_factory import ControllerFactory
from main.controllers.custom.web_screenshoot_controller import WebScreenshootController
from main.processors.phantomjs_processor import PhantomJSProcessor
from main.services.batches_service import BatchesService
from main.services.processor_service import ProcessorService

__author__ = 'Iván de Paz Centeno'


app = Flask(__name__)

def load_config():
    with open("main/etc/config.json") as f:
        config = json.load(f)

    return config

def get_site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        try:
            #if "GET" in rule.methods:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, [m for m in rule.methods]))
        except:
            pass
            # links is now a list of url, endpoint tuples

    return links

@app.route("/site-map")
def site_map():
    return jsonify(get_site_map())


# Custom configuration values (anything). They are accessible from the controller side.
config = load_config()

controller_factory = ControllerFactory(app, config)

# Services to inject to the controller. They are accessible from the controller side.
processor_service = ProcessorService(PhantomJSProcessor, int(config['workers']))

services = {
    'web_screenshoot_processor': processor_service,
    'batch_screenshoot_processor': BatchesService(processor_service)
}

for service in services.values(): service.start()

controller_factory.create_controller(WebScreenshootController, services)

print("Visit http://{}:{}/site-map for a list of endpoints.".format(config['host'], config['port']))

app.run(config['host'], config['port'], threaded=True)

controller_factory.release_all()