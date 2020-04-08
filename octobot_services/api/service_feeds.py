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


def get_service_feed(service_feed_class) -> AbstractServiceFeed:
    try:
        return service_feed_class.instance()
    except TypeError:
        raise RuntimeError(f"can't get {service_feed_class} instance: service feed has not been properly created yet")


def get_backtesting_service_feed(service_feed_class) -> AbstractServiceFeed:
    if service_feed_class.SIMULATOR_CLASS is not None:
        try:
            return service_feed_class.SIMULATOR_CLASS.instance()
        except TypeError:
            raise RuntimeError(f"can't get {service_feed_class.SIMULATOR_CLASS} "
                               f"instance: service feed has not been properly created yet")
    else:
        return None


def is_enabled_in_backtesting(service_feed_class) -> bool:
    return service_feed_class.IS_BACKTESTING_ENABLED


async def start_service_feed(service_feed: AbstractServiceFeed, backtesting_enabled: bool) -> bool:
    return await ServiceFeedManager.start_service_feed(service_feed, backtesting_enabled)


async def stop_service_feed(service_feed: AbstractServiceFeed) -> None:
    await ServiceFeedManager.stop_service_feed(service_feed)
