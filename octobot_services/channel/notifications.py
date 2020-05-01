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
from octobot_commons.singleton.singleton_class import Singleton
from octobot_channels.channels.channel import Channel
from octobot_channels.producer import Producer
from octobot_channels.consumer import Consumer


class NotificationChannelConsumer(Consumer):
    pass


class NotificationChannelProducer(Producer, Singleton):
    def __init__(self, channel):
        Producer.__init__(self, channel)


class NotificationChannel(Channel):
    PRODUCER_CLASS = NotificationChannelProducer
    CONSUMER_CLASS = NotificationChannelConsumer
