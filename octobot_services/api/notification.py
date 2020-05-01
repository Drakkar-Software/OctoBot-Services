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
from octobot_channels.channels.channel import get_chan

from octobot_services.channel.notifications import NotificationChannelProducer, NotificationChannel
from octobot_commons.enums import MarkdownFormat
from octobot_services.notification.notification import Notification
from octobot_services.notifier.notifier_factory import NotifierFactory
from octobot_services.enums import NotificationLevel, NotificationCategory


def create_notifier_factory(config) -> NotifierFactory:
    return NotifierFactory(config)


def create_notification(text: str, title="", markdown_text="",
                        markdown_format: MarkdownFormat = MarkdownFormat.IGNORE,
                        level: NotificationLevel = NotificationLevel.INFO,
                        category: NotificationCategory = NotificationCategory.GLOBAL_INFO,
                        linked_notification=None) -> Notification:
    return Notification(text, title, markdown_text, markdown_format, level, category, linked_notification)


async def send_notification(notification: Notification) -> None:
    try:
        # send notification only if is a notification channel is running
        get_chan(NotificationChannel.get_name())
        await NotificationChannelProducer.instance().send(
            {
                "notification": notification
            }
        )
    except KeyError:
        pass


def is_enabled_in_config(notifier_class, config) -> bool:
    return notifier_class.is_enabled(config)


def get_enable_notifier(notifier) -> bool:
    return notifier.enabled


def set_enable_notifier(notifier, enabled) -> None:
    notifier.enabled = enabled
