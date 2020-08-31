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
from abc import abstractmethod, ABCMeta

from octobot_channels.util.channel_creator import create_channel_instance
from octobot_channels.channels.channel import set_chan, get_chan, Channel
from octobot_services.channel.notifications import NotificationChannel, NotificationChannelProducer
from octobot_services.constants import CONFIG_CATEGORY_NOTIFICATION, CONFIG_NOTIFICATION_TYPE
from octobot_services.notification.formated_notifications import OrderCreationNotification, OrderEndNotification
from octobot_services.notification.notification import Notification
from octobot_services.abstract_service_user import AbstractServiceUser
from octobot_services.util.exchange_watcher import ExchangeWatcher
from octobot_trading.api.channels import subscribe_to_order_channel
from octobot_trading.api.exchange import get_exchange_manager_from_exchange_id, get_is_backtesting
from octobot_trading.api.orders import parse_order_status, get_order_profitability
from octobot_trading.api.profitability import get_profitability_stats
from octobot_trading.api.trader import is_trader_simulated
from octobot_trading.enums import OrderStatus, ExchangeConstantsOrderColumns


class AbstractNotifier(AbstractServiceUser, ExchangeWatcher):
    __metaclass__ = ABCMeta
    # Override this key with the identifier of the notifier (used to know if enabled)
    NOTIFICATION_TYPE_KEY = None
    # The service required to run this notifier
    REQUIRED_SERVICES = None

    def __init__(self, config):
        AbstractServiceUser.__init__(self, config)
        ExchangeWatcher.__init__(self)
        self.logger = self.get_logger()
        self.enabled = self.is_enabled(config)
        self.services = None
        self.previous_notifications_by_identifier = {}

    async def register_new_exchange_impl(self, exchange_id):
        if exchange_id not in self.registered_exchanges_ids:
            await self._subscribe_to_order_channel(exchange_id)

    # Override this method to use a notification when received
    @abstractmethod
    async def _handle_notification(self, notification: Notification):
        raise NotImplementedError(f"_handle_notification is not implemented")

    async def _notification_callback(self, notification: Notification = None):
        try:
            if self._is_notification_category_enabled(notification):
                self.logger.debug(f"Publishing notification: {notification}")
                await self._handle_notification(notification)
        except Exception as e:
            self.logger.exception(e, True, f"Exception when handling notification: {e}")

    async def _initialize_impl(self, backtesting_enabled, edited_config) -> bool:
        if await AbstractServiceUser._initialize_impl(self, backtesting_enabled, edited_config):
            self.services = [service.instance() for service in self.REQUIRED_SERVICES]
            await self._create_and_subscribe_to_notification_channel()
            return True
        return False

    async def _create_and_subscribe_to_notification_channel(self):
        channel = await self._create_notification_channel_if_not_existing()
        await channel.new_consumer(self._notification_callback)
        self.logger.debug("Registered as notification consumer")

    async def _order_notification_callback(self, exchange, exchange_id, cryptocurrency, symbol, order,
                                           is_new, is_from_bot):
        exchange_manager = get_exchange_manager_from_exchange_id(exchange_id)
        # Do not notify on existing pre-start orders
        if is_from_bot and not get_is_backtesting(exchange_manager):
            order_identifier = f"{exchange}_{order[ExchangeConstantsOrderColumns.ID.value]}"
            # find the last notification for this order if any
            linked_notification = self.previous_notifications_by_identifier[order_identifier] \
                if order_identifier in self.previous_notifications_by_identifier else None
            await self._handle_order_notification(order, linked_notification, order_identifier,
                                                  exchange_manager, exchange)

    async def _handle_order_notification(self, dict_order, linked_notification, order_identifier,
                                         exchange_manager, exchange):
        notification = None
        order_status = parse_order_status(dict_order)

        if order_status is OrderStatus.OPEN:
            notification = OrderCreationNotification(linked_notification, dict_order, exchange)
            # update last notification for this order
            self.previous_notifications_by_identifier[order_identifier] = notification
        else:
            is_simulated = is_trader_simulated(exchange_manager)
            if order_status is OrderStatus.CANCELED or \
                    (order_status is OrderStatus.CLOSED
                     and dict_order[ExchangeConstantsOrderColumns.FILLED.value] == 0):
                notification = OrderEndNotification(linked_notification, None, exchange, [dict_order],
                                                    None, None, None, False, is_simulated)
            elif order_status in (OrderStatus.CLOSED, OrderStatus.FILLED):
                _,  profitability_percent, profitability_diff, _,  _ = get_profitability_stats(exchange_manager)
                order_profitability = get_order_profitability(exchange_manager,
                                                              dict_order[ExchangeConstantsOrderColumns.ID.value])
                notification = OrderEndNotification(linked_notification, dict_order, exchange, [], order_profitability,
                                                    profitability_percent, profitability_diff, True, is_simulated)
            # remove order from previous_notifications_by_identifier: no more notification from it to be received
            if order_identifier in self.previous_notifications_by_identifier:
                self.previous_notifications_by_identifier.pop(order_identifier)
        await self._notification_callback(notification)

    async def _subscribe_to_order_channel(self, exchange_id):
        try:
            await subscribe_to_order_channel(self._order_notification_callback, exchange_id)
        except KeyError:
            self.logger.error("No order channel to subscribe to: impossible to send order notifications")

    @classmethod
    def is_enabled(cls, config):
        if cls.NOTIFICATION_TYPE_KEY is None:
            cls.get_logger().warning(f"{cls.get_name()}.NOTIFICATION_TYPE_KEY is not set, it has to be set to identify "
                                     f"and activate this notifier.")
        return cls.NOTIFICATION_TYPE_KEY in AbstractNotifier._get_activated_notification_keys(config)

    @staticmethod
    def _get_activated_notification_keys(config):
        if CONFIG_CATEGORY_NOTIFICATION in config and CONFIG_NOTIFICATION_TYPE in config[CONFIG_CATEGORY_NOTIFICATION]:
            return config[CONFIG_CATEGORY_NOTIFICATION][CONFIG_NOTIFICATION_TYPE]
        return []

    @staticmethod
    async def _create_notification_channel_if_not_existing() -> Channel:
        try:
            return get_chan(NotificationChannel.get_name())
        except KeyError:
            channel = await create_channel_instance(NotificationChannel, set_chan)
            await channel.register_producer(NotificationChannelProducer.instance(channel))
            return channel

    def _is_notification_category_enabled(self, notification):
        return CONFIG_CATEGORY_NOTIFICATION in self.config and \
               notification.category.value in self.config[CONFIG_CATEGORY_NOTIFICATION]
