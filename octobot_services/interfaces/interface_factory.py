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
from octobot_commons.tentacles_management.class_inspector import is_abstract_using_inspection_and_class_naming
from octobot_commons.tentacles_management.class_inspector import get_all_classes_from_parent
from octobot_services.interfaces.abstract_interface import AbstractInterface


class InterfaceFactory:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_available_interfaces() -> list:
        return [interface_class
                for interface_class in get_all_classes_from_parent(AbstractInterface)
                if not is_abstract_using_inspection_and_class_naming(interface_class)]

    async def create_interface(self, interface_class) -> AbstractInterface:
        return interface_class(self.config)
