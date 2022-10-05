# Solaris - A Discord bot designed to make your server a safer and better place.
# Copyright (C) 2020-2021  Ethan Henderson
# Copyright (C) 2021-present  Aoi Yuito

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Ethan Henderson (Original author)
# parafoxia@carberra.xyz

# Aoi Yuito (Rewritten author)
# aoi.yuito.ehou@gmail.com

from collections import deque

from apscheduler.triggers.cron import CronTrigger
from hikari import Status, Activity, ActivityType

ACTIVITY_TYPES = (ActivityType.WATCHING, ActivityType.PLAYING, ActivityType.LISTENING, ActivityType.STREAMING)


class PresenceSetter:
    def __init__(self, bot):
        self.bot = bot

        self._name = "@Solaris help • {message} • Version {version}"
        self._type = "watching"
        self._messages = deque(
            (
                "Invite Solaris to your server by using @Solaris invite",
                "To view information about Solaris, use @Solaris botinfo",
                "Need help with Solaris? Join the support server! Use @Solaris support to get an invite",
                "Developed by Yuito#8637, and available under the GPLv3 license",
            )
        )

        self.bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def name(self):
        message = self._messages[0].format(bot=self.bot)
        return self._name.format(message=message, version=self.bot.version)

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        return getattr(ActivityType, self._type, ActivityType.WATCHING)

    @type.setter
    def type(self, value):
        if value not in ACTIVITY_TYPES:
            raise ValueError("The activity should be one of the following: {}".format(", ".join(ACTIVITY_TYPES)))

        self._type = value

    async def set(self):
        await self.bot.update_presence(status=Status.ONLINE, activity=Activity(name=self.name, type=self.type))
        self._messages.rotate(-1)