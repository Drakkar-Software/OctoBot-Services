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
from octobot_services.interfaces.util.util import get_exchange_managers, run_in_bot_main_loop
from octobot_trading.api.orders import get_open_orders, cancel_order_with_id, \
    cancel_all_open_orders_with_currency, cancel_all_open_orders as api_cancel_all_open_orders
from octobot_trading.api.trader import is_trader_enabled, is_trader_simulated


def get_all_open_orders():
    simulated_open_orders = []
    real_open_orders = []

    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_open_orders += get_open_orders(exchange_manager)
            else:
                real_open_orders += get_open_orders(exchange_manager)

    return real_open_orders, simulated_open_orders


def cancel_orders(order_ids):
    removed_count = 0
    if order_ids:
        for order_id in order_ids:
            for exchange_manager in get_exchange_managers():
                if is_trader_enabled(exchange_manager):
                    removed_count += 1 if run_in_bot_main_loop(cancel_order_with_id(exchange_manager, order_id)) else 0
    return removed_count


def cancel_all_open_orders(currency=None):
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if currency is None:
                run_in_bot_main_loop(api_cancel_all_open_orders(exchange_manager))
            else:
                run_in_bot_main_loop(cancel_all_open_orders_with_currency(exchange_manager, currency))
