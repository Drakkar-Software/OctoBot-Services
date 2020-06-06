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
import threading

from octobot_commons.logging.logging_util import get_logger
from octobot_services.interfaces.abstract_interface import AbstractInterface
from octobot_services.interfaces.util.bot import get_bot_api
from octobot_trading.api.exchange import get_exchange_managers_from_exchange_ids, get_trading_exchanges


def get_exchange_managers(bot_api=None, independent_backtesting=None, trading_exchanges_only=True):
    if bot_api is not None:
        return _filter_exchange_manager(get_exchange_managers_from_exchange_ids(bot_api.get_exchange_manager_ids()),
                                        trading_exchanges_only)
    elif independent_backtesting is not None:
        try:
            from octobot.api.backtesting import get_independent_backtesting_exchange_manager_ids
            return _filter_exchange_manager(
                get_exchange_managers_from_exchange_ids(
                    get_independent_backtesting_exchange_manager_ids(independent_backtesting)),
                trading_exchanges_only)
        except ImportError:
            get_logger("octobot_services/interfaces/util/util.py").error(
                "get_exchange_managers requires OctoBot package installed")
    else:
        return _filter_exchange_manager(AbstractInterface.get_exchange_managers(), trading_exchanges_only)


def _filter_exchange_manager(exchange_managers, trading_exchanges_only):
    if trading_exchanges_only:
        return get_trading_exchanges(exchange_managers)
    return exchange_managers


def run_in_bot_main_loop(coroutine, blocking=True):
    if blocking:
        return get_bot_api().run_in_main_asyncio_loop(coroutine)
    else:
        threading.Thread(target=get_bot_api().run_in_main_asyncio_loop,
                         args=(coroutine,),
                         name=f"run_in_bot_main_loop {coroutine.__name__}").start()


def run_in_bot_async_executor(coroutine):
    return get_bot_api().run_in_async_executor(coroutine)
