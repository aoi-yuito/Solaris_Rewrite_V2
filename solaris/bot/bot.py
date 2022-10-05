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

from __future__ import annotations

import time
from pathlib import Path

import hikari
import lightbulb
import datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from solaris import Config, utils
from solaris.db import Database

EMOJI_GUILD = None

class Bot(lightbulb.BotApp):
    
    def __init__(self, version) -> None:
        self.version = version
        self._extensions = [p.stem for p in Path(".").glob("./solaris/bot/extensions/*.py")]
        self._dynamic = "./solaris/data/dynamic"
        self._static = "./solaris/data/static"
        self._transcripts = "./solaris/data/transcripts"
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)
        self.db = Database(self)

        self.embed = utils.EmbedConstructor(self)
        #self.emoji = utils.EmojiGetter(self) Note: emoji.py or EmojiGetter() class is not rewritten
        self.loc = utils.CodeCounter()
        self.presence = utils.PresenceSetter(self)
        self.ready = utils.Ready(self)

        self.loc.count()


        super().__init__(
            prefix=lightbulb.when_mentioned_or(self.command_prefix),
            help_class=None,
            case_insensitive_prefix_commands=True,
            token=Config.TOKEN,
            intents=hikari.Intents.ALL
        )


    def run(self) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.ShardConnectedEvent, self.on_shard_connected)
        self.event_manager.subscribe(hikari.ShardDisconnectedEvent, self.on_shard_disconnected)
        
        super().run(
            activity=hikari.Activity(
                name=f"@Solaris help • Version {self.version}",
            ),
            status=hikari.Status.DO_NOT_DISTURB,
        )


    async def prefix(self, guild_id):
        if guild_id is not None:
            return await self.db.field("SELECT Prefix FROM system WHERE GuildID = ?", guild_id)
        return Config.DEFAULT_PREFIX


    async def command_prefix(self, _: lightbulb.Bot, message: hikari.Message) -> None:
        prefix = await self.prefix(message.guild_id)
        return prefix


    async def on_starting(self, event: hikari.StartingEvent) -> None:
        print("Running setup...")
        
        print(" Connecting to Database...")
        await self.db.connect()
        print(" Connected to database.")

        for ext in self._extensions:
            self.load_extensions(f"solaris.bot.extensions.{ext}")
            print(f" • {ext} extension loaded")

        self.emoji_guild = await self.rest.fetch_guild(Config.HUB_GUILD_ID)
        
        print("Setup complete.")


    async def on_started(self, event: hikari.StartedEvent) -> None:
        print("Running bot...")
        
        if not self.ready.booted:
            heartbeat_latency = (
                self.heartbeat_latency * 1_000
            )
            print(f" Connected to Discord (latency: {heartbeat_latency:,.0f} ms).")

            print(" Readied.")
            self.client_id = self.get_me().id

            self.scheduler.start()
            print(f" Scheduler started ({len(self.scheduler.get_jobs()):,} job(s)).")

            await self.db.sync()
            self.ready.synced = True
            print(" Synchronised database.")

            self.ready.booted = True
            print(" Bot booted. Don't use CTRL+C to shut the bot down!")


        await self.presence.set()

        print("Bot Ready!")


    async def on_stopping(self, event: hikari.StoppingEvent) -> None:

        print("Shutting down...")

        self.scheduler.shutdown()
        print(" Shut down scheduler.")

        await self.db.close()
        print(" Closed database connection.")

        hub = self.get_plugin("Hub")

        if (sc := hub.d.stdout_channel) is not None:
            await sc.send(f"{self.info} Solaris is now shutting down. (Version {self.version})")

        print(" Closing connection to Discord...")


    async def on_shard_connected(self, event: hikari.ShardConnectedEvent) -> None:
        print(f"Bot resumed at ({dt.datetime.now()}) Shard Count: {event.shard.shard_count} with Shard ID: {event.shard.id}")


    async def on_shard_disconnected(self, event: hikari.ShardDisconnectedEvent) -> None:
        print(f"Bot disconnected at ({dt.datetime.now()}) Shard Count: {event.shard.shard_count} with Shard ID: {event.shard.id}")


    @property
    def guild_count(self):
        return len(self.cache.get_guilds_view())

    @property
    def user_count(self):
        return len(self.cache.get_members_view())

    @property
    def command_count(self):
        commands = []
        for ext in self._extensions:
            for cmd in self.get_plugin(ext.title()).all_commands:
                commands.append(cmd)
        return len(commands)

    @property
    def admin_invite(self):
        return utils.oauth_url(self.client_id, permissions=hikari.Permissions.ADMINISTRATOR)

    @property
    def non_admin_invite(self):
        return utils.oauth_url(
            self.client_id,
            permissions=(
                hikari.Permissions.MANAGE_ROLES
                | hikari.Permissions.MANAGE_CHANNELS
                | hikari.Permissions.KICK_MEMBERS
                | hikari.Permissions.BAN_MEMBERS
                | hikari.Permissions.MANAGE_NICKNAMES
                | hikari.Permissions.SEND_MESSAGES
                | hikari.Permissions.MANAGE_MESSAGES
                | hikari.Permissions.EMBED_LINKS
                | hikari.Permissions.READ_MESSAGE_HISTORY
                | hikari.Permissions.USE_EXTERNAL_EMOJIS
                | hikari.Permissions.ADD_REACTIONS
            ),
        )

    @property
    def info(self):
        return self.emoji_guild.get_emoji(Config.INFO_EMOJI_ID).mention

    @property
    def tick(self):
        return self.emoji_guild.get_emoji(Config.ACCEPT_EMOJI_ID).mention

    @property
    def cross(self):
        return self.emoji_guild.get_emoji(Config.CANCEL_EMOJI_ID).mention

    @staticmethod
    def generate_id():
        return hex(int(time.time() * 1e7))[2:]

    async def grab_user(self, arg):
        try:
            return self.cache.get_user(arg)
        except (ValueError, hikari.NotFoundError):
            return None

    async def grab_channel(self, arg):
        try:
            return self.cache.get_guild_channel(arg)
        except (ValueError, hikari.NotFoundError):
            return None

    async def grab_guild(self, arg):
        try:
            return self.cache.get_guild(arg)
        except (ValueError, hikari.NotFoundError):
            return None
