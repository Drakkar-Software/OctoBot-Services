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
import enum


class NotificationLevel(enum.Enum):
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class NotificationCategory(enum.Enum):
    GLOBAL_INFO = "global-info"
    PRICE_ALERTS = "price-alerts"
    TRADES = "trades"
    TRADING_SCRIPT_ALERTS = "trading-script-alerts"
    OTHER = "other"


class NotificationSound(enum.Enum):
    NO_SOUND = None
    FINISHED_PROCESSING = "finished_processing.mp3"
