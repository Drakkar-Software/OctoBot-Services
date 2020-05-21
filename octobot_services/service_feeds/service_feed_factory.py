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
from octobot_commons.tentacles_management.class_inspector import get_all_classes_from_parent

from octobot_commons.logging.logging_util import get_logger

from octobot_services.service_feeds.abstract_service_feed import AbstractServiceFeed
from octobot_services.service_feeds.service_feeds import ServiceFeeds


class ServiceFeedFactory:
    def __init__(self, config, main_async_loop, bot_id):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.main_async_loop = main_async_loop
        self.bot_id = bot_id

    @staticmethod
    def get_available_service_feeds(in_backtesting: bool) -> list:
        feeds = get_all_classes_from_parent(AbstractServiceFeed)
        if in_backtesting:
            feeds = [feed.SIMULATOR_CLASS
                     for feed in feeds
                     if feed.SIMULATOR_CLASS is not None]
        return feeds

    def create_service_feed(self, service_feed_class) -> AbstractServiceFeed:
        feed = service_feed_class(self.config, self.main_async_loop, self.bot_id)
        ServiceFeeds.instance().add_service_feed(self.bot_id, service_feed_class.get_name(), feed)
        return feed
