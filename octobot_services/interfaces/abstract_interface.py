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
from abc import abstractmethod, ABCMeta

from octobot_services.abstract_service_user import AbstractServiceUser
from octobot_services.util.returning_startable import ReturningStartable


class AbstractInterface(AbstractServiceUser, ReturningStartable):
    __metaclass__ = ABCMeta
    # The service required to run this interface
    REQUIRED_SERVICES = None

    # References that will be shared by interfaces
    bot_api = None
    project_name = None
    project_version = None
    enabled = True

    @staticmethod
    def initialize_global_project_data(bot_api, project_name, project_version):
        AbstractInterface.bot_api = bot_api
        AbstractInterface.project_name = project_name
        AbstractInterface.project_version = project_version

    @staticmethod
    def get_exchange_managers():
        try:
            from octobot_trading.api.exchange import get_exchange_managers_from_exchange_ids
            return get_exchange_managers_from_exchange_ids(AbstractInterface.bot_api.get_exchange_manager_ids())
        except ImportError:
            AbstractInterface.get_logger().error("AbstractInterface requires OctoBot-Trading package installed")

    @staticmethod
    def is_bot_ready():
        return AbstractInterface.bot_api.is_initialized()

    @abstractmethod
    async def stop(self):
        raise NotImplementedError(f"stop is not implemented for {self.get_name()}")