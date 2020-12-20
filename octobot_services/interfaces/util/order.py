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
import octobot_trading.api as trading_api

import octobot_services.interfaces as interfaces


def get_all_open_orders():
    simulated_open_orders = []
    real_open_orders = []

    for exchange_manager in interfaces.get_exchange_managers():
        if trading_api.is_trader_existing_and_enabled(exchange_manager):
            if trading_api.is_trader_simulated(exchange_manager):
                simulated_open_orders += trading_api.get_open_orders(exchange_manager)
            else:
                real_open_orders += trading_api.get_open_orders(exchange_manager)

    return real_open_orders, simulated_open_orders


def cancel_orders(order_ids):
    removed_count = 0
    if order_ids:
        for order_id in order_ids:
            for exchange_manager in interfaces.get_exchange_managers():
                if trading_api.is_trader_existing_and_enabled(exchange_manager):
                    removed_count += 1 if interfaces.run_in_bot_main_loop(
                        trading_api.cancel_order_with_id(exchange_manager, order_id)) else 0
    return removed_count


def cancel_all_open_orders(currency=None):
    for exchange_manager in interfaces.get_exchange_managers():
        if trading_api.is_trader_existing_and_enabled(exchange_manager):
            if currency is None:
                interfaces.run_in_bot_main_loop(
                    trading_api.cancel_all_open_orders(exchange_manager))
            else:
                interfaces.run_in_bot_main_loop(
                    trading_api.cancel_all_open_orders_with_currency(exchange_manager, currency))
