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
from octobot_services.managers.service_feed_manager import ServiceFeedManager
from octobot_services.service_feeds.abstract_service_feed import AbstractServiceFeed
from octobot_services.service_feeds.service_feed_factory import ServiceFeedFactory


def create_service_feed_factory(config, main_async_loop) -> ServiceFeedFactory:
    return ServiceFeedFactory(config, main_async_loop)


async def start_service_feed(service_feed: AbstractServiceFeed, backtesting_enabled: bool) -> bool:
    return await ServiceFeedManager.start_service_feed(service_feed, backtesting_enabled)


def stop_service_feed(service_feed: AbstractServiceFeed) -> None:
    ServiceFeedManager.stop_service_feed(service_feed)
