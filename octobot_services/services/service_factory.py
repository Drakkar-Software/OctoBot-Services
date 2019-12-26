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

from octobot_commons.logging.logging_util import get_logger

from octobot_services.constants import CONFIG_CATEGORY_SERVICES, CONFIG_SERVICE_INSTANCE
from octobot_services.services.abstract_service import AbstractService


class ServiceFactory:
    def __init__(self, config):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config

    async def create_or_get_service(self, service_class, backtesting_enabled):
        """
        create_or_get_service will create a service instance if it doesn't exist, check the existing one otherwise
        :param service_class: the class of the service to create
        :return: True if the created service is working properly, False otherwise
        """
        service_instance = service_class()
        if service_class.get_has_been_created():
            return service_instance.is_healthy()
        else:
            service_instance.is_backtesting_enabled = backtesting_enabled
            service_instance.set_has_been_created(True)
            service_instance.set_logger(get_logger(service_instance.get_name()))
            service_instance.set_config(self.config)
            if service_instance.has_required_configuration():
                try:
                    await service_instance.prepare()
                    self.config[CONFIG_CATEGORY_SERVICES][service_instance.get_type()][CONFIG_SERVICE_INSTANCE] = \
                        service_instance
                    if await service_instance.say_hello():
                        return service_instance.is_healthy()
                    else:
                        self.logger.warning(f"{service_instance.get_name()} initial checkup failed.")
                except Exception as e:
                    self.logger.error(f"{service_instance.get_name()} preparation produced the following error: {e}")
                    self.logger.exception(e)
            else:
                if service_instance.get_should_warn():
                    self.logger.warning(f"{service_instance.get_name()} can't be initialized: configuration "
                                        f"is missing, wrong or incomplete !")
            return False

    @staticmethod
    def has_already_been_created(service_class):
        return service_class.get_has_been_created()
