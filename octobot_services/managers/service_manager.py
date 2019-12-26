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
from octobot_services.util.service_util import get_available_services
from octobot_services.constants import CONFIG_CATEGORY_SERVICES, CONFIG_SERVICE_INSTANCE
from octobot_services.services.service_factory import ServiceFactory


def stop_services():
    for service_instance in _get_service_instances():
        try:
            service_instance.stop()
        except Exception as e:
            raise e


def _get_service_instances():
    instances = []
    for service_class in get_available_services():
        instances.append(service_class.instance())
    return instances
