#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Ivan de Paz Centeno"


class ControllerFactory(object):
    """
    Factory for controllers.
    Eases the creation of controllers by injecting common dependencies, like the services definition
    and the app handler.
    """

    def __init__(self, flask_app, config):
        """
        Initializes the factory with minimum parameters.
        :param flask_app: application of Flask to handle the requests.
        :param config: configuration object containing all the definitions of services.
        """
        self.flask_app = flask_app
        self.config = config
        self.controllers = {}
        self.available_services = {}

    def _create_atomic_controller(self, controller_proto, controller_services):
        """
        Generates a controller for the given name.

        :param controller_name: The name of the controller to create
        :param controller_proto: proto of the controller.
        :param controller_services: services to inject to the controller.
        :return: The created controller instance. If the name of the controller does not exist, it will raise an
        exception.
        """

        return controller_proto(flask_web_app=self.flask_app,
                                available_services=controller_services,
                                config=self.config)


    def create_controller(self, controller_proto, controller_services):
        """
        Singleton-creation of the specified controller.
        When this method is invoked, it will add the controller to the flask app.
        If the controller already exists, it will only return a reference to it.
        :return: the controller that handles custom requests.
        """
        controller_name = controller_proto.__name__

        if controller_name not in self.controllers:
            self.available_services[controller_name] = controller_services
            self.controllers[controller_name] = self._create_atomic_controller(controller_proto,
                                                                               controller_services=controller_services)

        return self.controllers[controller_name]

    def release_all(self, wait_for_release=True):
        """
        Releases all the services and controllers from the APP.
        """

        for service_name, service in self.available_services.items():
            service.stop(wait_for_release)

    def __del__(self):
        """
        On destruction of the factory, the controllers and services will be gone.
        """

        self.release_all()
