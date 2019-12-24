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

from octobot_services.dispatchers.abstract_dispatcher import DispatcherAbstractClient
from octobot_services.dispatchers.dispatcher_exception import DispatcherException


class DispatcherManager:

    @staticmethod
    def bind_to_dispatcher_if_necessary(evaluator_instance, dispatchers_list, symbol, is_evaluator_to_be_used):
        # If evaluator is a dispatcher client --> check if dispatcher exists
        # else warn and pass this evaluator
        if evaluator_instance.has_class_in_parents(DispatcherAbstractClient):
            try:
                client_found_dispatcher = DispatcherManager.set_evaluator_dispatcher(evaluator_instance,
                                                                                     dispatchers_list)
                if not client_found_dispatcher:
                    get_logger(DispatcherManager.get_name()).warning(
                        f"No dispatcher found for evaluator: {evaluator_instance.get_name()} "
                        f"for symbol: {symbol}, evaluator has been disabled.")
                    return True, False
            except DispatcherException as e:
                get_logger(DispatcherManager.get_name()).exception(e)
                return True, False
            return True, is_evaluator_to_be_used
        return False, is_evaluator_to_be_used

    @staticmethod
    def set_evaluator_dispatcher(eval_instance, dispatchers_list):
        for evaluator_dispatcher in dispatchers_list:
            if eval_instance.is_client_to_this_dispatcher(evaluator_dispatcher):
                eval_instance.set_dispatcher(evaluator_dispatcher)
                evaluator_dispatcher.register_client(eval_instance)
                return True
        return False

    @staticmethod
    def start_dispatchers(dispatcher_list):
        for thread in dispatcher_list:
            thread.start()

    @staticmethod
    def stop_dispatchers(dispatcher_list):
        for thread in dispatcher_list:
            thread.stop()

    @classmethod
    def get_name(cls):
        return cls.__name__
