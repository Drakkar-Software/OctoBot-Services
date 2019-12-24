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
from octobot_services.constants import CONFIG_CATEGORY_SERVICES, CONFIG_SERVICE_INSTANCE


def stop_services(config):
    for service_instance in _get_service_instances(config):
        try:
            service_instance.stop()
        except Exception as e:
            raise e


def _get_service_instances(config):
    instances = []
    for services in config[CONFIG_CATEGORY_SERVICES]:
        if CONFIG_SERVICE_INSTANCE in config[CONFIG_CATEGORY_SERVICES][services]:
            instance = config[CONFIG_CATEGORY_SERVICES][services][CONFIG_SERVICE_INSTANCE]
            if isinstance(instance, list):
                for i in instance:
                    instances.append(i)
            else:
                instances.append(instance)
    return instances
