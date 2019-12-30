#  Drakkar-Software OctoBot-Services
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

from abc import ABCMeta, abstractmethod

from octobot_commons.config_util import has_invalid_default_config_value
from octobot_commons.singleton.singleton_class import Singleton


class AbstractService(Singleton):
    __metaclass__ = ABCMeta

    BACKTESTING_ENABLED = False
    _has_been_created = False

    def __init__(self):
        super().__init__()
        self.logger = None
        self.config = None
        self._created = True
        self._healthy = False

    @classmethod
    def set_has_been_created(cls, value):
        cls._has_been_created = value

    @classmethod
    def get_has_been_created(cls):
        return cls._has_been_created

    def is_healthy(self):
        return self._healthy

    @classmethod
    def get_name(cls):
        return cls.__name__

    def get_fields_description(self):
        return {}

    def get_default_value(self):
        return {}

    def get_required_config(self):
        return {}

    # Override this method if a user is to be registered in this service (ie: TelegramService)
    def register_user(self, user_key):
        pass

    # Override this method if a service feed is located in this service (ie: TelegramService)
    def start_service_feed(self):
        pass

    # Override this method to know if an updater is already running
    def is_running(self):
        return False

    @classmethod
    def get_help_page(cls) -> str:
        return ""

    # Returns true if all the service has an instance in config
    @staticmethod
    @abstractmethod
    def is_setup_correctly(config):
        raise NotImplementedError("is_setup_correctly not implemented")

    # Override this method to perform additional checks
    @staticmethod
    def get_is_enabled(config):
        return True

    # implement locally if the service has thread(s) to stop
    def stop(self):
        pass

    # implement locally if the service shouldn't raise warning at startup if configuration is not set
    @staticmethod
    def get_should_warn():
        return True

    # Returns true if all the configuration is available
    @abstractmethod
    def has_required_configuration(self):
        raise NotImplementedError("has_required_configuration not implemented")

    # Returns the service's endpoint
    @abstractmethod
    def get_endpoint(self) -> None:
        raise NotImplementedError("get_endpoint not implemented")

    # Called to put in the right service in config
    @abstractmethod
    def get_type(self) -> None:
        raise NotImplementedError("get_type not implemented")

    # Called after service setup
    @abstractmethod
    async def prepare(self) -> None:
        raise NotImplementedError("prepare not implemented")

    # Called by say_hello after service is prepared, return relevant service information and a boolean for
    # success or failure
    @abstractmethod
    def get_successful_startup_message(self):
        raise NotImplementedError("get_successful_startup_message not implemented")

    def check_required_config(self, config):
        return all(key in config for key in self.get_required_config()) and \
            not has_invalid_default_config_value(*(config[key] for key in self.get_required_config()))

    def log_connection_error_message(self, e):
        self.logger.error(f"{self.get_name()} is failing to connect, please check your internet connection: {e}")

    async def say_hello(self):
        message, self._healthy = self.get_successful_startup_message()
        if self._healthy:
            self.logger.info(message)
        return self._healthy
