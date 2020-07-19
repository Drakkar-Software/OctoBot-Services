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
import os
from abc import ABCMeta

from octobot_commons.constants import CONFIG_ENABLED_OPTION
from octobot_services.interfaces.abstract_interface import AbstractInterface
from octobot_services.interfaces.util.bot import get_global_config, get_bot_api
from octobot_services.interfaces.util.order import get_all_open_orders, cancel_all_open_orders
from octobot_services.interfaces.util.portfolio import get_portfolio_current_value, \
    get_global_portfolio_currencies_amounts, trigger_portfolios_refresh
from octobot_services.interfaces.util.profitability import get_global_profitability, get_reference_market
from octobot_services.interfaces.util.trader import has_real_and_or_simulated_traders, get_currencies_with_status, \
    get_risk, get_trades_history, set_risk, set_enable_trading, get_total_paid_fees, \
    sell_all_currencies, sell_all
from octobot_trading.api.exchange import get_exchange_names
from octobot_trading.api.orders import get_order_exchange_name, order_to_dict
from octobot_trading.api.trades import get_trade_exchange_name
from octobot_trading.constants import REAL_TRADER_STR, SIMULATOR_TRADER_STR
from octobot_services.constants import PAID_FEES_STR
from octobot_services.constants import CONFIG_INTERFACES, CONFIG_CATEGORY_SERVICES, CONFIG_USERNAMES_WHITELIST
from octobot_services.interfaces.bots import EOL, NO_CURRENCIES_MESSAGE, NO_TRADER_MESSAGE
from octobot_commons.pretty_printer import get_markers, trade_pretty_printer, \
    open_order_pretty_printer, pretty_print_dict, global_portfolio_pretty_print, get_min_string_from_number, \
    portfolio_profitability_pretty_print
from octobot_commons.timestamp_util import convert_timestamp_to_datetime


class AbstractBotInterface(AbstractInterface):
    __metaclass__ = ABCMeta

    @staticmethod
    def enable(config, is_enabled, associated_config=None):
        if CONFIG_INTERFACES not in config:
            config[CONFIG_INTERFACES] = {}
        if associated_config not in config[CONFIG_INTERFACES]:
            config[CONFIG_INTERFACES][associated_config] = {}
        config[CONFIG_INTERFACES][associated_config][CONFIG_ENABLED_OPTION] = is_enabled

    @staticmethod
    def is_enabled(config, associated_config=None):
        return CONFIG_INTERFACES in config \
               and associated_config in config[CONFIG_INTERFACES] \
               and CONFIG_ENABLED_OPTION in config[CONFIG_INTERFACES][associated_config] \
               and config[CONFIG_INTERFACES][associated_config][CONFIG_ENABLED_OPTION]

    @staticmethod
    def _is_valid_user(user_name, associated_config=None):
        config_interface = get_global_config()[CONFIG_CATEGORY_SERVICES][associated_config]

        white_list = config_interface[CONFIG_USERNAMES_WHITELIST] \
            if CONFIG_USERNAMES_WHITELIST in config_interface else None

        is_valid = not white_list or user_name in white_list or f"@{user_name}" in white_list

        return is_valid, white_list

    @staticmethod
    def get_command_configuration(markdown=False):
        _, bold, code = get_markers(markdown)
        message = f"{bold}My configuration:{bold}{EOL}{EOL}"

        message += f"{bold}Traders: {bold}{EOL}"
        has_real_trader, has_simulated_trader = has_real_and_or_simulated_traders()
        if has_real_trader:
            message += f"{code}- Real trader{code}{EOL}"
        if has_simulated_trader:
            message += f"{code}- Simulated trader{code}{EOL}"

        message += f"{EOL}{bold}Exchanges:{bold}{EOL}"
        for exchange_name in get_exchange_names():
            message += f"{code}- {exchange_name.capitalize()}{code}{EOL}"

        try:
            from octobot_evaluators.api.evaluators import get_evaluator_classes_from_type
            from octobot_evaluators.enums import EvaluatorMatrixTypes
            tentacle_setup_config = get_bot_api().get_tentacles_setup_config()
            message += f"{EOL}{bold}Evaluators:{bold}{EOL}"
            evaluators = get_evaluator_classes_from_type(EvaluatorMatrixTypes.TA.value,
                                                         tentacle_setup_config)
            evaluators += get_evaluator_classes_from_type(EvaluatorMatrixTypes.SOCIAL.value,
                                                          tentacle_setup_config)
            evaluators += get_evaluator_classes_from_type(EvaluatorMatrixTypes.REAL_TIME.value,
                                                          tentacle_setup_config)
            for evaluator in evaluators:
                message += f"{code}- {evaluator.get_name()}{code}{EOL}"

            message += f"{EOL}{bold}Strategies:{bold}{EOL}"
            for strategy in get_evaluator_classes_from_type(EvaluatorMatrixTypes.STRATEGIES.value,
                                                            tentacle_setup_config):
                message += f"{code}- {strategy.get_name()}{code}{EOL}"
        except ImportError:
            message += f"{EOL}{bold}Impossible to retrieve evaluation configuration: requires OctoBot-Evaluators " \
                       f"package installed{bold}{EOL}"

        message += f"{EOL}{bold}Trading mode:{bold}{EOL}"
        trading_mode = get_bot_api().get_trading_mode()
        if trading_mode:
            message += f"{code}- {trading_mode.get_name()}{code}"

        return message

    @staticmethod
    def get_command_market_status(markdown=False):
        _, bold, code = get_markers(markdown)
        message = f"{bold}My cryptocurrencies evaluations are:{bold} {EOL}{EOL}"
        at_least_one_currency = False
        for currency_pair, currency_info in get_currencies_with_status().items():
            at_least_one_currency = True
            message += f"{code}{currency_pair}:{code}{EOL}"
            for _, evaluation in currency_info.items():
                message += f"{code}- {evaluation[2].capitalize()}: {evaluation[0]}{code}{EOL}"
        if not at_least_one_currency:
            message += f"{code}{NO_CURRENCIES_MESSAGE}{code}{EOL}"
        risk = get_risk()
        if risk:
            message += f"{EOL}{code}My current risk is: {get_risk()}{code}"

        return message

    @staticmethod
    def _print_trades(trades_history, trader_str, markdown=False):
        _, bold, code = get_markers(markdown)
        trades_history_string = f"{bold}{trader_str}{bold}{code}Trades :{EOL}{code}"
        if trades_history:
            for trade in trades_history:
                exchange_name = get_trade_exchange_name(trade)
                trades_history_string += \
                    f"{trade_pretty_printer(exchange_name, trade, markdown=markdown)}{EOL}"
        else:
            trades_history_string += f"{code}No trade yet.{code}"
        return trades_history_string

    @staticmethod
    def get_command_trades_history(markdown=False):
        has_real_trader, has_simulated_trader = has_real_and_or_simulated_traders()
        real_trades_history, simulated_trades_history = get_trades_history()

        trades_history_string = ""
        if has_real_trader:
            trades_history_string += AbstractBotInterface._print_trades(real_trades_history, REAL_TRADER_STR, markdown)

        if has_simulated_trader:
            trades_history_string += \
                f"{EOL}{AbstractBotInterface._print_trades(simulated_trades_history, SIMULATOR_TRADER_STR, markdown)}"

        if not trades_history_string:
            trades_history_string = NO_TRADER_MESSAGE

        return trades_history_string

    @staticmethod
    def _print_open_orders(open_orders, trader_str, markdown=False):
        _, bold, code = get_markers(markdown)
        orders_string = f"{bold}{trader_str}{bold}{code}Open orders :{code}{EOL}"
        if open_orders:
            for order in open_orders:
                exchange_name = get_order_exchange_name(order).capitalize()
                orders_string += open_order_pretty_printer(exchange_name,
                                                           order_to_dict(order),
                                                           markdown=markdown) + EOL
        else:
            orders_string += f"{code}No open order yet.{code}"
        return orders_string

    @staticmethod
    def get_command_open_orders(markdown=False):
        has_real_trader, has_simulated_trader = has_real_and_or_simulated_traders()
        portfolio_real_open_orders, portfolio_simulated_open_orders = get_all_open_orders()

        orders_string = ""
        if has_real_trader:
            orders_string += AbstractBotInterface._print_open_orders(portfolio_real_open_orders,
                                                                     REAL_TRADER_STR,
                                                                     markdown)

        if has_simulated_trader:
            message = AbstractBotInterface._print_open_orders(portfolio_simulated_open_orders,
                                                              SIMULATOR_TRADER_STR,
                                                              markdown)
            orders_string += f"{EOL}{message}"

        if not orders_string:
            orders_string = NO_TRADER_MESSAGE

        return orders_string

    @staticmethod
    def get_command_fees(markdown=False):
        _, bold, _ = get_markers(markdown)
        real_trader_fees, simulated_trader_fees = get_total_paid_fees()
        result_str = ""
        if real_trader_fees is not None:
            result_str = f"{bold}{REAL_TRADER_STR}{bold}{PAID_FEES_STR}: " \
                         f"{pretty_print_dict(real_trader_fees, markdown=markdown)}"
        if simulated_trader_fees is not None:
            result_str = f"{result_str}\n{bold}{SIMULATOR_TRADER_STR}{bold}{PAID_FEES_STR}: " \
                         f"{pretty_print_dict(simulated_trader_fees, markdown=markdown)}"
        if not result_str:
            result_str = NO_TRADER_MESSAGE
        return result_str

    @staticmethod
    def get_command_sell_all_currencies():
        try:
            cancel_all_open_orders()
            nb_created_orders = len(sell_all_currencies())
            if nb_created_orders:
                return f"Currencies sold in {nb_created_orders} order{'s' if nb_created_orders > 1 else ''}."
            else:
                return "Nothing to sell."
        except Exception as e:
            return f"An error occurred: {e.__class__.__name__}"

    @staticmethod
    def get_command_sell_all(currency):
        try:
            cancel_all_open_orders(currency)
            nb_created_orders = len(sell_all(currency))
            if nb_created_orders:
                return f"{currency} sold in {nb_created_orders} order{'s' if nb_created_orders > 1 else ''}."
            else:
                return f"Nothing to sell for {currency}."
        except Exception as e:
            return f"An error occurred: {e.__class__.__name__}"

    @staticmethod
    def _print_portfolio(current_val, ref_market, portfolio, trader_str, markdown=False):
        _, bold, code = get_markers(markdown)
        portfolios_string = f"{bold}{trader_str}{bold}Portfolio value : " \
                            f"{bold}{get_min_string_from_number(current_val)} {ref_market}{bold}" \
                            f"{EOL}"
        portfolio_str = global_portfolio_pretty_print(portfolio, markdown=markdown)
        if not portfolio_str:
            portfolio_str = "Nothing there."
        portfolios_string += f"{bold}{trader_str}{bold}Portfolio : {EOL}{code}{portfolio_str}{code}"
        return portfolios_string

    @staticmethod
    def get_command_portfolio(markdown=False):
        has_real_trader, has_simulated_trader, \
        portfolio_real_current_value, portfolio_simulated_current_value = get_portfolio_current_value()
        reference_market = get_reference_market()
        real_global_portfolio, simulated_global_portfolio = get_global_portfolio_currencies_amounts()

        portfolios_string = ""
        if has_real_trader:
            portfolios_string += AbstractBotInterface._print_portfolio(portfolio_real_current_value, reference_market,
                                                                       real_global_portfolio, REAL_TRADER_STR, markdown)

        if has_simulated_trader:
            portfolio_str = AbstractBotInterface._print_portfolio(portfolio_simulated_current_value, reference_market,
                                                                  simulated_global_portfolio, SIMULATOR_TRADER_STR,
                                                                  markdown)
            portfolios_string += f"{EOL}{portfolio_str}"

        if not portfolios_string:
            portfolios_string = NO_TRADER_MESSAGE

        return portfolios_string

    @staticmethod
    def get_command_profitability(markdown=False):
        _, bold, code = get_markers(markdown)
        has_real_trader, has_simulated_trader, \
        real_global_profitability, simulated_global_profitability, \
        real_percent_profitability, simulated_percent_profitability, \
        real_no_trade_profitability, simulated_no_trade_profitability, \
        market_average_profitability = get_global_profitability()
        profitability_string = ""
        if has_real_trader:
            real_profitability_pretty = portfolio_profitability_pretty_print(real_global_profitability,
                                                                             None,
                                                                             get_reference_market())
            profitability_string = \
                f"{bold}{REAL_TRADER_STR}{bold}Global profitability : {code}{real_profitability_pretty}" \
                f"({get_min_string_from_number(real_percent_profitability, 2)}%){code}, market: {code}" \
                f"{get_min_string_from_number(market_average_profitability, 2)}%{code}, initial portfolio:" \
                f" {code}{get_min_string_from_number(real_no_trade_profitability, 2)}%{code}{EOL}"
        if has_simulated_trader:
            simulated_profitability_pretty = \
                portfolio_profitability_pretty_print(simulated_global_profitability,
                                                     None,
                                                     get_reference_market())
            profitability_string += \
                f"{bold}{SIMULATOR_TRADER_STR}{bold}Global profitability : {code}{simulated_profitability_pretty}" \
                f"({get_min_string_from_number(simulated_percent_profitability, 2)}%){code}, " \
                f"market: {code}{get_min_string_from_number(market_average_profitability, 2)}%{code}, " \
                f"initial portfolio: {code}" \
                f"{get_min_string_from_number(simulated_no_trade_profitability, 2)}%{code}"
        if not profitability_string:
            profitability_string = NO_TRADER_MESSAGE

        return profitability_string

    @staticmethod
    def get_command_ping():
        return f"I'm alive since " \
               f"{convert_timestamp_to_datetime(get_bot_api().get_start_time(), '%Y-%m-%d %H:%M:%S')}."

    @staticmethod
    def get_command_version():
        return f"{AbstractInterface.project_name} {AbstractInterface.project_version}"

    @staticmethod
    def get_command_start(markdown=False):
        if markdown:
            return "Hello, I'm [OctoBot](https://github.com/Drakkar-Software/OctoBot), type /help to know my skills."
        else:
            return "Hello, I'm OctoBot, type /help to know my skills."

    @staticmethod
    def set_command_portfolios_refresh():
        return trigger_portfolios_refresh()

    @staticmethod
    def set_command_risk(new_risk):
        return set_risk(new_risk)

    @staticmethod
    def set_command_stop():
        get_bot_api().stop_bot()

    def set_command_pause(self):
        cancel_all_open_orders()
        set_enable_trading(False)
        self.paused = True

    def set_command_resume(self):
        set_enable_trading(True)
        self.paused = False

    @staticmethod
    def _split_messages_if_too_long(message, max_length, preferred_separator):
        if len(message) >= max_length:
            # split message using preferred_separator as separator
            messages_list = []
            first_part = message[:max_length]
            end_index = first_part.rfind(preferred_separator)
            if end_index != -1:
                messages_list.append(message[:end_index])
            else:
                messages_list.append(message[:max_length])
                end_index = len(first_part) - 1

            if end_index < len(message) - 1:
                remaining = message[end_index + 1:]
                return messages_list + AbstractBotInterface._split_messages_if_too_long(remaining, max_length,
                                                                                        preferred_separator)
            else:
                return messages_list
        else:
            return [message]
