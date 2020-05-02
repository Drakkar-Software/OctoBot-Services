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
from abc import ABCMeta

from octobot_commons.logging.logging_util import get_logger
from octobot_services.services.service_factory import ServiceFactory
from octobot_services.util.initializable_with_post_actions import InitializableWithPostAction


class AbstractServiceUser(InitializableWithPostAction):
    __metaclass__ = ABCMeta

    # The service required to run this user
    REQUIRED_SERVICES = None

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.paused = False

    async def _initialize_impl(self, backtesting_enabled, edited_config) -> bool:
        # init associated service if not already init
        service_list = ServiceFactory.get_available_services()
        if self.REQUIRED_SERVICES:
            for service in self.REQUIRED_SERVICES:
                if service in service_list:
                    if not await self._create_or_get_service_instance(service, backtesting_enabled, edited_config):
                        return False
                else:
                    self.get_logger().error(f"Required service {self.REQUIRED_SERVICES} is not an available service")
            return True
        elif self.REQUIRED_SERVICES is None:
            self.get_logger().error(f"Required service is not set, set it at False if no service is required")
        return False

    async def _create_or_get_service_instance(self, service, backtesting_enabled, edited_config):
        service_factory = ServiceFactory(self.config)
        if await service_factory.create_or_get_service(service, backtesting_enabled, edited_config):
            return True
        else:
            self.get_logger().warning(f"Impossible to start {self.get_name()}: required service "
                                      f"{service.get_name()} is not available.")
            return False

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_logger(cls):
        return get_logger(cls.get_name())
