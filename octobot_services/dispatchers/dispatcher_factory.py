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

from octobot_services.dispatchers.abstract_dispatcher import AbstractDispatcher


class DispatcherFactory:
    def __init__(self, config, main_async_loop):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.main_async_loop = main_async_loop

    def create_all(self):
        dispatchers_list = []
        for dispatcher_class in AbstractDispatcher.__subclasses__():
            dispatcher_instance = dispatcher_class(self.config, self.main_async_loop)
            dispatchers_list.append(dispatcher_instance)
        return dispatchers_list
