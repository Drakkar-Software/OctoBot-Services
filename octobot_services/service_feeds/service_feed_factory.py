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
from octobot_commons.tentacles_management.advanced_manager import get_all_classes_from_parent

from octobot_commons.logging.logging_util import get_logger

from octobot_services.service_feeds.abstract_service_feed import AbstractServiceFeed


class ServiceFeedFactory:
    def __init__(self, config, main_async_loop):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.main_async_loop = main_async_loop

    @staticmethod
    def get_available_service_feeds() -> list:
        return get_all_classes_from_parent(AbstractServiceFeed)

    def create_service_feed(self, service_feed_class) -> AbstractServiceFeed:
        return service_feed_class.instance(self.config, self.main_async_loop)
