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

import hikari
import lightbulb
from lightbulb import commands

import aiofiles
import aiofiles.os
import datetime as dt

import traceback

from solaris.utils import checks, chron, string


system_err = lightbulb.plugins.Plugin(
    name="Error",
    description=None,
    include_datastore=True
)


@system_err.listener(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent):
    if not system_err.bot.ready.booted:
        system_err.bot.ready.up(system_err)

    system_err.d.configurable: bool = False
    system_err.d.image = None
    
    
@system_err.listener(hikari.ExceptionEvent)
async def on_error(event: hikari.ExceptionEvent):
    print(event.failed_event)
    ref = await record_error(event.exception, event.exc_info, event.failed_event)
    hub = system_err.bot.get_plugin("Hub")

    if (sc := hub.d.stdout_channel) is not None:
        await sc.send(f"{system_err.bot.cross} Something went wrong (ref: {ref}).")
        
    try:
        if event.failed_event.context is not None:
            prefix = await event.failed_event.context.bot.prefix(event.failed_event.context.guild_id)
            await event.failed_event.context.respond(
                f"{system_err.bot.cross} Something went wrong (ref: {ref}). Quote this reference in the support server, which you can get a link for by using `{prefix}support`."
            )
    except AttributeError:
        pass

    raise event.exception


@system_err.listener(lightbulb.events.CommandErrorEvent)
async def on_command_error(event: lightbulb.events.CommandErrorEvent):
    prefix = await event.context.bot.prefix(event.context.guild_id)
    if isinstance(event.exception, lightbulb.errors.CommandNotFound):
        pass

    elif hasattr(event.exception, "msg"):
        await event.context.respond(f"{event.context.bot.cross} {event.exception.msg}")

    elif isinstance(event.exception, lightbulb.errors.NotEnoughArguments):
        await event.context.respond(
            f"{event.context.bot.cross} No `{event.exception.missing_options[0].name}` argument was passed, despite being required. Use `{prefix}help {event.context.command.name}` for more information."
        )

    elif isinstance(event.exception, lightbulb.errors.MissingRequiredPermission):
        mp = string.list_of([str(str(perm).replace("_", " ")).title() for perm in event.exception.missing_perms], sep="or")
        await event.context.respond(
            f"{event.context.bot.cross} You do not have the `{mp}` permission(s), which are required to use this command."
        )

    elif isinstance(event.exception, lightbulb.errors.BotMissingRequiredPermission):
        try:
            mp = string.list_of([str(str(perm).replace("_", " ")).title() for perm in event.exception.missing_perms], sep="or")
            await event.context.respond(
                f"{event.context.bot.cross} Solaris does not have the `{mp}` permission(s), which are required to use this command."
            )
        except hikari.ForbiddenError:
            # If Solaris does not have the Send Messages permission
            # (might redirect this to log channel once it's set up).
            pass

    elif isinstance(event.exception, lightbulb.errors.NotOwner):
        await event.context.respond(f"{event.context.bot.cross} That command can only be used by Solaris' owner.")

    elif isinstance(event.exception, lightbulb.errors.OnlyInGuild):
        await event.context.respond(f"{event.context.bot.cross} Solaris does not support command invokations in DMs.")
        
    #elif isinstance(event.exception, checks.FirstTimeSetupNotRun):
        #await event.context.respond(f"{ctx.bot.cross} The first time setup needs to be run before you can do that. Use `{prefix}setup` to do this.")
        
    elif isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
        try:
            if isinstance(event.context.invoked.cooldown_manager.cooldowns.get(event.context.author.id), lightbulb.buckets.UserBucket):
                await event.context.respond(
                    f"{event.context.bot.cross} You can not use that command for another {chron.long_delta(dt.timedelta(seconds=event.exception.retry_after))}.",
                    delete_after=5
                )
        except Exception:
            pass

        try:
            if isinstance(event.context.invoked.cooldown_manager.cooldowns.get(event.context.guild_id), lightbulb.buckets.GuildBucket):
                await event.context.respond(
                    f"{event.context.bot.cross} That command can not be used in this server for another {chron.long_delta(dt.timedelta(seconds=event.exception.retry_after))}.",
                    delete_after=5
                )
        except Exception:
            pass

        try:
            if isinstance(event.context.invoked.cooldown_manager.cooldowns.get(event.context.channel_id), lightbulb.buckets.ChannelBucket):
                await event.context.respond(
                    f"{event.context.bot.cross} That command can not be used in this channel for another {chron.long_delta(dt.timedelta(seconds=event.exception.retry_after))}.",
                    delete_after=5
                )
        except Exception:
            pass

    elif isinstance(event.exception, lightbulb.errors.CheckFailure):
        if not isinstance(event.exception, lightbulb.errors.NotOwner) and not isinstance(event.exception, lightbulb.errors.OnlyInGuild):
            await event.context.respond(
                f"{event.context.bot.cross} There was an unhandled command check error (probably missing privileges). Use `{prefix}help {event.context.command.name}` for more information."
            )

    
    elif (original := getattr(event.exception, "original", None)) is not None:
        if isinstance(original, hikari.HTTPResponseError):
            await event.context.respond(
                f"{event.context.bot.cross} A HTTP exception occurred ({original.status})\n```{original.message}```"
            )
        else:
            raise original

    else:
        raise event.exception


async def record_error(err, exc_info, obj):
    obj = getattr(obj, "message", obj)
    if isinstance(obj, hikari.Message):
        cause = f"{obj.content}\n{obj!r}"
    else:
        cause = f"{obj!r}"

    ref = system_err.bot.generate_id()
    traceback_info = "".join(traceback.format_exception(*exc_info))

    await system_err.bot.db.execute(
        "INSERT INTO errors (Ref, Cause, Traceback) VALUES (?, ?, ?)", ref, cause, str(traceback_info)
    )
    return ref


@system_err.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option(name="ref", description="ID of the error.", type=str)
@lightbulb.command(name="recallerror", aliases=["err"], description=None, hidden=True)
@lightbulb.implements(commands.prefix.PrefixCommand)
async def error_command(ctx: lightbulb.context.base.Context) -> None:
    cause, error_time, traceback = await ctx.bot.db.record(
        "SELECT Cause, ErrorTime, Traceback FROM errors WHERE Ref = ?", ctx.options.ref
    )

    path = f"{ctx.bot._dynamic}/{ctx.options.ref}.txt"
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        text = f"Time of error:\n{error_time}\n\nCause:\n{cause}\n\n{traceback}"
        await f.write(text)

    await ctx.respond(attachment=hikari.File(path))
    await aiofiles.os.remove(path)


def load(bot) -> None:
    bot.add_plugin(system_err)

def unload(bot) -> None:
    bot.remove_plugin(system_err)
