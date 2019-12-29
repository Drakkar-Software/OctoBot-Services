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

from abc import *
import threading

from octobot_channels.channels.channel import get_chan, set_chan

from octobot_commons.asyncio_tools import run_coroutine_in_asyncio_loop


# ****** Unique dispatcher side ******
from octobot_services.abstract_service_user import AbstractServiceUser
from octobot_services.channel.abstract_service_feed import AbstractServiceFeedChannelProducer


class AbstractServiceFeed(AbstractServiceUser, AbstractServiceFeedChannelProducer):
    __metaclass__ = ABCMeta

    # Override FEED_CHANNEL with a dedicated channel
    FEED_CHANNEL = None

    _SLEEPING_TIME_BEFORE_RECONNECT_ATTEMPT_SEC = 10
    DELAY_BETWEEN_STREAMS_QUERIES = 5
    REQUIRED_SERVICE_ERROR_MESSAGE = "Required services are not ready, service feed can't start"

    def __init__(self, config, main_async_loop):
        AbstractServiceUser.__init__(self, config)
        AbstractServiceFeedChannelProducer.__init__(self, set_chan(self.FEED_CHANNEL(), None))
        self.feed_config = {}
        self.main_async_loop = main_async_loop
        self.service = None

    # Override update_feed_config if any need in the extending feed
    def update_feed_config(self, config):
        pass

    # Override this method if the service feed implementation is using a dispatcher handled in the service layer
    # (ie: TelegramServiceFeed)
    @staticmethod
    def _get_service_layer_service_feed() -> object:
        return None

    # Override this method to specify the feed reception process
    @abstractmethod
    def _start_service_feed(self):
        raise NotImplementedError("start_dispatcher not implemented")

    @abstractmethod
    def _something_to_watch(self):
        raise NotImplementedError("_something_to_watch not implemented")

    @abstractmethod
    def _initialize(self):
        raise NotImplementedError("_initialize not implemented")

    def _init_chanel(self):
        channel = get_chan(self.FEED_CHANNEL.get_name())
        run_coroutine_in_asyncio_loop(channel.register_producer(self),
                                      self.main_async_loop)

    # Call _notify_consumers to send data to consumers
    def _notify_consumers(self, data):
        try:
            # send notification only if is a notification channel is running
            get_chan(self.FEED_CHANNEL.get_name())
            run_coroutine_in_asyncio_loop(self.feed_send_coroutine(data), self.main_async_loop)
        except KeyError:
            self.logger.error("Can't send notification data: no initialized channel found")

    async def feed_send_coroutine(self, data):
        await self.send(
            {
                "data": data
            }
        )

    def _run(self, should_init=True):
        self.is_running = True
        service_level_service_feed_if_any = self._get_service_layer_service_feed()
        if self._something_to_watch():
            if should_init:
                self._initialize()
                self._init_chanel()
            if service_level_service_feed_if_any is not None and self.service is not None and not self.service.is_running():
                self.service.start_service_feed()
            if not self._start_service_feed():
                self.logger.warning("Nothing can be monitored even though there is something to watch"
                                    ", feed is going closing.")
        else:
            self.logger.info("Nothing to monitor, feed is closing.")
            self.is_running = False

    # Override this method if the feed has to be run in a thread using this body:
    # threading.Thread.start(self)
    def start(self) -> None:
        self.run()

    def run(self):
        self.logger.info("Starting feed reception ...")
        self.service = self.REQUIRED_SERVICE.instance()
        self._run()

    def resume(self):
        self.should_stop = False
        self.logger.info("Resuming feed reception ...")
        self._run(should_init=False)

    def stop(self):
        self.should_stop = True
        self.is_running = False
