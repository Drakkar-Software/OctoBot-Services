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
import abc

import async_channel.channels as channels

import octobot_commons.asyncio_tools as asyncio_tools

import octobot_services.abstract_service_user as abstract_service_user
import octobot_services.channel as service_channels
import octobot_services.util as util


class AbstractServiceFeed(abstract_service_user.AbstractServiceUser,
                          util.ReturningStartable,
                          service_channels.AbstractServiceFeedChannelProducer):
    __metaclass__ = abc.ABCMeta

    # Override FEED_CHANNEL with a dedicated channel
    FEED_CHANNEL = None

    # Set simulator class when available in order to use it in backtesting for this feed
    SIMULATOR_CLASS = None

    _SLEEPING_TIME_BEFORE_RECONNECT_ATTEMPT_SEC = 10
    DELAY_BETWEEN_STREAMS_QUERIES = 5
    REQUIRED_SERVICE_ERROR_MESSAGE = "Required services are not ready, service feed can't start"

    def __init__(self, config, main_async_loop, bot_id):
        abstract_service_user.AbstractServiceUser.__init__(self, config)
        service_channels.AbstractServiceFeedChannelProducer.__init__(self, channels.set_chan(self.FEED_CHANNEL(), None))
        self.feed_config = {}
        self.main_async_loop = main_async_loop
        self.bot_id = bot_id
        self.services = None
        self.should_stop = False

    # Override update_feed_config if any need in the extending feed
    def update_feed_config(self, config):
        pass

    # Override this method if the service feed implementation is using a dispatcher handled in the service layer
    # (ie: TelegramServiceFeed)
    @staticmethod
    def _get_service_layer_service_feed() -> object:
        return None

    # Override this method to specify the feed reception process
    @abc.abstractmethod
    async def _start_service_feed(self):
        raise NotImplementedError("start_dispatcher not implemented")

    @abc.abstractmethod
    def _something_to_watch(self):
        raise NotImplementedError("_something_to_watch not implemented")

    @abc.abstractmethod
    def _initialize(self):
        raise NotImplementedError("_initialize not implemented")

    async def _init_channel(self):
        channel = channels.get_chan(self.FEED_CHANNEL.get_name())
        await channel.register_producer(self)

    # Call _notify_consumers to send data to consumers
    def _notify_consumers(self, data):
        try:
            # send notification only if is a notification channel is running
            channels.get_chan(self.FEED_CHANNEL.get_name())
            asyncio_tools.run_coroutine_in_asyncio_loop(self.feed_send_coroutine(data), self.main_async_loop)
        except KeyError:
            self.logger.error("Can't send notification data: no initialized channel found")

    # Call _async_notify_consumers to send data to consumers (same as _notify_consumers but directly from async context)
    async def _async_notify_consumers(self, data):
        try:
            # send notification only if is a notification channel is running
            channels.get_chan(self.FEED_CHANNEL.get_name())
            await self.feed_send_coroutine(data)
        except KeyError:
            self.logger.error("Can't send notification data: no initialized channel found")

    async def feed_send_coroutine(self, data):
        await self.send(
            {
                "data": data
            }
        )

    async def _run(self, should_init=True):
        self.is_running = True
        service_level_service_feed_if_any = self._get_service_layer_service_feed()
        if self._something_to_watch():
            if should_init:
                self._initialize()
                await self._init_channel()
            if self.services is not None:
                for service in self.services:
                    if service_level_service_feed_if_any is not None \
                            and not service.is_running():
                        await service.start_service_feed()
            if not await self._start_service_feed():
                self.logger.warning("Nothing can be monitored even though there is something to watch"
                                    ", feed is going closing.")
        else:
            self.logger.info("Nothing to monitor, feed is closing.")
            self.is_running = False
        return True

    async def _async_run(self) -> bool:
        self.logger.info("Initializing feed reception ...")
        self.services = [service.instance() for service in self.REQUIRED_SERVICES]
        return await self._run()

    async def resume(self) -> bool:
        self.should_stop = False
        self.logger.info("Resuming feed reception ...")
        return await self._run(should_init=False)

    async def stop(self):
        if self.is_running:
            self.should_stop = True
            self.is_running = False
