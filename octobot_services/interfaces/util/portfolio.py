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
from octobot_commons.constants import PORTFOLIO_AVAILABLE, PORTFOLIO_TOTAL

from octobot_services.interfaces.util.util import get_exchange_managers, run_in_bot_main_loop
from octobot_trading.api.portfolio import get_portfolio, refresh_real_trader_portfolio
from octobot_trading.api.profitability import get_current_holdings_values, get_origin_portfolio_value, \
    get_current_portfolio_value
from octobot_trading.api.trader import is_trader_enabled, is_trader_simulated


def _merge_portfolio_values(portfolio1, portfolio2):
    for key, value in portfolio2.items():
        if key in portfolio1:
            portfolio1[key] += value
        else:
            portfolio1[key] = value
    return portfolio1


def get_portfolio_holdings():
    real_currency_portfolio = {}
    simulated_currency_portfolio = {}

    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            trader_currencies_values = run_in_bot_main_loop(get_current_holdings_values(exchange_manager))
            if is_trader_simulated(exchange_manager):
                _merge_portfolio_values(simulated_currency_portfolio, trader_currencies_values)
            else:
                _merge_portfolio_values(real_currency_portfolio, trader_currencies_values)

    return real_currency_portfolio, simulated_currency_portfolio


def get_portfolio_current_value():
    simulated_value = 0
    real_value = 0
    has_real_trader = False
    has_simulated_trader = False

    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            current_value = get_current_portfolio_value(exchange_manager)

            # current_value might be 0 if no trades have been made / canceled => use origin value
            if current_value == 0:
                current_value = get_origin_portfolio_value(exchange_manager)

            if is_trader_simulated(exchange_manager):
                simulated_value += current_value
                has_simulated_trader = True
            else:
                real_value += current_value
                has_real_trader = True

    return has_real_trader, has_simulated_trader, real_value, simulated_value


def _get_portfolios():
    simulated_portfolios = []
    real_portfolios = []

    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_portfolios.append(get_portfolio(exchange_manager))
            else:
                real_portfolios.append(get_portfolio(exchange_manager))

    return real_portfolios, simulated_portfolios


def _merge_portfolios(base_portfolio, to_merge_portfolio):
    for currency, amounts in to_merge_portfolio.items():
        if currency not in base_portfolio:
            base_portfolio[currency] = {
                PORTFOLIO_AVAILABLE: 0,
                PORTFOLIO_TOTAL: 0
            }

        base_portfolio[currency][PORTFOLIO_AVAILABLE] += amounts[PORTFOLIO_AVAILABLE]
        base_portfolio[currency][PORTFOLIO_TOTAL] = amounts[PORTFOLIO_TOTAL]


def get_global_portfolio_currencies_amounts():
    real_portfolios, simulated_portfolios = _get_portfolios()
    real_global_portfolio = {}
    simulated_global_portfolio = {}

    for portfolio in simulated_portfolios:
        _merge_portfolios(simulated_global_portfolio, portfolio)

    for portfolio in real_portfolios:
        _merge_portfolios(real_global_portfolio, portfolio)

    return real_global_portfolio, simulated_global_portfolio


def trigger_portfolios_refresh():
    at_least_one = False
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            at_least_one = True
            run_in_bot_main_loop(refresh_real_trader_portfolio(exchange_manager))

    if not at_least_one:
        raise RuntimeError("no real trader to update.")
