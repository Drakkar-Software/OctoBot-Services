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
from octobot_commons.logging.logging_util import get_logger
from octobot_services.interfaces.util.bot import get_bot_api
from octobot_services.interfaces.util.util import run_in_bot_main_loop, get_exchange_managers
from octobot_trading.api.exchange import get_trading_pairs, get_exchange_name, get_exchange_manager_id
from octobot_trading.api.modes import get_trading_modes, get_trading_mode_symbol, get_trading_mode_current_state
from octobot_trading.api.portfolio import refresh_real_trader_portfolio
from octobot_trading.api.trader import is_trader_simulated, get_trader_risk, is_trader_enabled, set_trader_risk, \
    set_trading_enabled, sell_all_everything_for_reference_market, \
    sell_currency_for_reference_market, is_trader_enabled_in_config_from_exchange_manager
from octobot_trading.api.trades import get_trade_history, get_total_paid_trading_fees


def has_real_and_or_simulated_traders():
    has_real_trader = False
    has_simulated_trader = False
    exchange_managers = get_exchange_managers()
    for exchange_manager in exchange_managers:
        if is_trader_simulated(exchange_manager):
            has_simulated_trader = True
        else:
            has_real_trader = True
    return has_real_trader, has_simulated_trader


def sell_all_currencies():
    orders = []
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += run_in_bot_main_loop(sell_all_everything_for_reference_market(exchange_manager))
    return orders


def sell_all(currency):
    orders = []
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += run_in_bot_main_loop(sell_currency_for_reference_market(exchange_manager, currency))
    return orders


def set_enable_trading(enable):
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled_in_config_from_exchange_manager(exchange_manager):
            set_trading_enabled(exchange_manager, enable)


def _merge_trader_fees(current_fees, exchange_manager):
    current_fees_dict = current_fees if current_fees else {}
    for key, val in get_total_paid_trading_fees(exchange_manager).items():
        if key in current_fees_dict:
            current_fees_dict[key] += val
        else:
            current_fees_dict[key] = val
    return current_fees_dict


def get_total_paid_fees(bot=None):
    real_trader_fees = None
    simulated_trader_fees = None

    for exchange_manager in get_exchange_managers(bot):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trader_fees = _merge_trader_fees(simulated_trader_fees, exchange_manager)
            else:
                real_trader_fees = _merge_trader_fees(real_trader_fees, exchange_manager)

    return real_trader_fees, simulated_trader_fees


def get_trades_history(bot_api=None, symbol=None, independent_backtesting=None, since=None, as_dict=False):
    simulated_trades_history = []
    real_trades_history = []

    for exchange_manager in get_exchange_managers(bot_api=bot_api, independent_backtesting=independent_backtesting):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trades_history += get_trade_history(exchange_manager, symbol, since, as_dict)
            else:
                real_trades_history += get_trade_history(exchange_manager, symbol, since, as_dict)

    return real_trades_history, simulated_trades_history


def set_risk(risk):
    result_risk = None
    for exchange_manager in get_exchange_managers():
        result_risk = set_trader_risk(exchange_manager, risk)
    return result_risk


def get_risk():
    try:
        return get_trader_risk(next(iter(get_exchange_managers())))
    except StopIteration:
        return None


def get_currencies_with_status():
    evaluations_by_exchange_by_pair = {}
    for exchange_manager in get_exchange_managers():
        trading_modes = get_trading_modes(exchange_manager)
        for pair in get_trading_pairs(exchange_manager):
            if pair not in evaluations_by_exchange_by_pair:
                evaluations_by_exchange_by_pair[pair] = {}
            status_explanation = "N/A"
            status = "N/A"
            for trading_mode in trading_modes:
                if get_trading_mode_symbol(trading_mode) == pair:
                    status_explanation, status = get_trading_mode_current_state(trading_mode)
                    try:
                        status = round(status, 3)
                    except TypeError:
                        pass
                    break
            evaluations_by_exchange_by_pair[pair][get_exchange_manager_id(exchange_manager)] = \
                [status_explanation.replace("_", " "), status, get_exchange_name(exchange_manager).capitalize()]
    return evaluations_by_exchange_by_pair


def _get_tentacles_values(evaluations, tentacle_type_node, exchange):
    try:
        from octobot_evaluators.api.matrix import get_children_list, has_children, get_value
    except ImportError:
        get_logger("InterfaceUtil").error("_get_tentacles_values requires OctoBot-Evaluators package installed")
        return {}
    for tentacle_name, tentacle_name_node in get_children_list(tentacle_type_node).items():
        evaluations[exchange][tentacle_name] = {}
        for cryptocurrency, cc_node in get_children_list(tentacle_name_node).items():
            evaluations[exchange][tentacle_name][cryptocurrency] = {}
            if has_children(cc_node):
                for symbol, symbol_node in get_children_list(cc_node).items():
                    if has_children(symbol_node):
                        evaluations[exchange][tentacle_name][symbol] = {}
                        for time_frame, time_frame_node in get_children_list(symbol_node).items():
                            evaluations[exchange][tentacle_name][symbol][time_frame] = \
                                get_value(time_frame_node)
                    else:
                        evaluations[exchange][tentacle_name][symbol] = get_value(symbol_node)
            else:
                evaluations[exchange][tentacle_name][cryptocurrency] = get_value(cc_node)


def get_matrix_list():
    try:
        from octobot_evaluators.api.matrix import get_matrix, get_node_children_by_names, get_children_list
    except ImportError:
        get_logger("InterfaceUtil").error("get_matrix_list requires OctoBot-Evaluators package installed")
        return {}
    evaluations = {}
    matrix = get_matrix(get_bot_api().get_matrix_id())
    for exchange, exchange_node in get_node_children_by_names(matrix).items():
        evaluations[exchange] = {}
        for tentacle_type_node in get_children_list(exchange_node).values():
            _get_tentacles_values(evaluations, tentacle_type_node, exchange)
    return evaluations
