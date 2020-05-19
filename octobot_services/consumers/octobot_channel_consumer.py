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
from enum import Enum

from octobot_channels.channels.channel_instances import get_chan_at_id
from octobot_commons.channels_name import OctoBotChannelsName
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.enums import OctoBotChannelSubjects
from octobot_services.api.service_feeds import start_service_feed
from octobot_services.managers.interface_manager import start_interface

OCTOBOT_CHANNEL_EVALUATOR_CONSUMER_LOGGER_TAG = "OctoBotChannelServiceConsumer"


class OctoBotChannelServiceActions(Enum):
    """
    OctoBot Channel consumer supported actions
    """

    INTERFACE = "interface"
    NOTIFICATION = "notification"
    SERVICE_FEED = "service_feed"
    START_SERVICE_FEED = "start_service_feed"
    EXCHANGE_REGISTRATION = "exchange_registration"


class OctoBotChannelServiceDataKeys(Enum):
    """
    OctoBot Channel consumer supported data keys
    """

    EXCHANGE_ID = "exchange_id"
    BOT_ID = "bot_id"
    EDITED_CONFIG = "edited_config"
    BACKTESTING_ENABLED = "backtesting_enabled"
    INSTANCE = "instance"
    SUCCESSFUL_OPERATION = "successful_operation"
    CLASS = "class"
    FACTORY = "factory"


async def octobot_channel_callback(bot_id, subject, action, data) -> None:
    """
    OctoBot channel consumer callback
    :param bot_id: the callback bot id
    :param subject: the callback subject
    :param action: the callback action
    :param data: the callback data
    """
    if subject == OctoBotChannelSubjects.CREATION.value:
        await _handle_creation(bot_id, action, data)
    elif subject == OctoBotChannelSubjects.UPDATE.value:
        if action == OctoBotChannelServiceActions.EXCHANGE_REGISTRATION.value:
            await _handle_exchange_notification(data)
        elif action == OctoBotChannelServiceActions.START_SERVICE_FEED.value:
            await _handle_service_feed_start_notification(bot_id, action, data)


async def _handle_creation(bot_id, action, data):
    created_instance = None
    edited_config = data[OctoBotChannelServiceDataKeys.EDITED_CONFIG.value]
    backtesting_enabled = data[OctoBotChannelServiceDataKeys.BACKTESTING_ENABLED.value]
    to_create_class = data[OctoBotChannelServiceDataKeys.CLASS.value]
    factory = data[OctoBotChannelServiceDataKeys.FACTORY.value]
    if action == OctoBotChannelServiceActions.INTERFACE.value:
        created_instance = await _create__and_start_interface(factory, to_create_class, edited_config, backtesting_enabled)
    if action == OctoBotChannelServiceActions.NOTIFICATION.value:
        created_instance = await _create_notifier(factory, to_create_class, edited_config, backtesting_enabled)
    if action == OctoBotChannelServiceActions.SERVICE_FEED.value:
        created_instance = await _create_service_feed(factory, to_create_class)
    await get_chan_at_id(OctoBotChannelsName.OCTOBOT_CHANNEL.value, bot_id).get_internal_producer() \
        .send(bot_id=bot_id,
              subject=OctoBotChannelSubjects.NOTIFICATION.value,
              action=action,
              data={OctoBotChannelServiceDataKeys.INSTANCE.value: created_instance})


async def _create__and_start_interface(interface_factory, to_create_class, edited_config, backtesting_enabled):
    interface_instance = await interface_factory.create_interface(to_create_class)
    await interface_instance.initialize(backtesting_enabled, edited_config)
    return interface_instance if await start_interface(interface_instance) else None


async def _create_notifier(factory, to_create_class, edited_config, backtesting_enabled):
    notifier_instance = await factory.create_notifier(to_create_class)
    await notifier_instance.initialize(backtesting_enabled, edited_config)
    return notifier_instance


async def _create_service_feed(factory, to_create_class):
    return factory.create_service_feed(to_create_class)


async def _handle_exchange_notification(data):
    notifier_or_interface = data[OctoBotChannelServiceDataKeys.INSTANCE.value]
    exchange_id = data[OctoBotChannelServiceDataKeys.EXCHANGE_ID.value]
    await notifier_or_interface.register_new_exchange(exchange_id)


async def _handle_service_feed_start_notification(bot_id, action, data):
    service_feed = data[OctoBotChannelServiceDataKeys.INSTANCE.value]
    edited_config = data[OctoBotChannelServiceDataKeys.EDITED_CONFIG.value]
    await get_chan_at_id(OctoBotChannelsName.OCTOBOT_CHANNEL.value, bot_id).get_internal_producer() \
        .send(bot_id=bot_id,
              subject=OctoBotChannelSubjects.NOTIFICATION.value,
              action=action,
              data={OctoBotChannelServiceDataKeys.SUCCESSFUL_OPERATION.value: await _start_service_feed(service_feed,
                                                                                                        edited_config)})


async def _start_service_feed(service_feed, edited_config):
    if not await start_service_feed(service_feed, False, edited_config):
        get_logger(OCTOBOT_CHANNEL_EVALUATOR_CONSUMER_LOGGER_TAG).error(
            f"Failed to start {service_feed.get_name()}. Evaluators requiring this service feed "
            f"might not work properly")
        return False
    return True
