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

from octobot_services.util.service_util import get_available_services
from octobot_services.services.service_factory import ServiceFactory


class AbstractServiceUser:
    __metaclass__ = ABCMeta

    # The service required to run this user
    REQUIRED_SERVICE = None

    def __init__(self, config):
        self.config = config
        self.paused = False

    async def initialize(self, backtesting_enabled) -> bool:
        # init associated service if not already init
        service_list = get_available_services()
        if self.REQUIRED_SERVICE:
            if self.REQUIRED_SERVICE in service_list:
                service_factory = ServiceFactory(self.config)
                if await service_factory.create_or_get_service(self.REQUIRED_SERVICE, backtesting_enabled):
                    return await self._post_initialize()
                else:
                    self.get_logger().error(f"Impossible to start {self.get_name()}: required service "
                                            f"is not available.")
            else:
                self.get_logger().error(f"Required service {self.REQUIRED_SERVICE} is not an available service")
        elif self.REQUIRED_SERVICE is None:
            self.get_logger().error(f"Required service is not set, set it at False if no service is required")
        return False

    # Implement _post_initialize if anything specific has to be done after initialize and before start
    async def _post_initialize(self) -> bool:
        return True

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_logger(cls):
        return get_logger(cls.get_name())
