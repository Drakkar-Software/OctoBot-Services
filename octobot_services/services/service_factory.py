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

    @staticmethod
    def get_available_services():
        return [service_class for service_class in AbstractService.__subclasses__()]

    async def create_service(self, service_instance):
        service_instance.set_logger(get_logger(service_instance.get_name()))
        service_instance.set_config(self.config)
        if service_instance.has_required_configuration():
            try:
                await service_instance.prepare()
                self.config[CONFIG_CATEGORY_SERVICES][service_instance.get_type()][CONFIG_SERVICE_INSTANCE] = \
                    service_instance
                if not await service_instance.say_hello():
                    self.logger.warning(f"{service_instance.get_name()} initial checkup failed.")
            except Exception as e:
                self.logger.error(f"{service_instance.get_name()} preparation produced the following error: {e}")
                self.logger.exception(e)
        else:
            if service_instance.get_should_warn():
                self.logger.warning(f"{service_instance.get_name()} can't be initialized: configuration is missing, "
                                    f"wrong or incomplete !")
