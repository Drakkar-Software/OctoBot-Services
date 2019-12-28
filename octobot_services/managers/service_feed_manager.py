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
from octobot_services.service_feeds.abstract_service_feed import AbstractServiceFeed


class ServiceFeedManager:

    @staticmethod
    async def start_service_feed(service_feed: AbstractServiceFeed, backtesting_enabled: bool):
        if not service_feed.is_running and not service_feed.should_stop:
            if await service_feed.initialize(backtesting_enabled):
                service_feed.start()
                return True
        return False

    @staticmethod
    def stop_service_feed(service_feed: AbstractServiceFeed):
        service_feed.stop()
