# Solaris - A Discord bot designed to make your server a safer and better place.
# Copyright (C) 2020  Ethan Henderson

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

import re
import hikari
import lightbulb

from solaris.utils import string
from solaris.utils.modules import retrieve

MAX_PREFIX_LEN = 5

MAX_MEMBER_ROLES = 3
MAX_EXCEPTION_ROLES = 3
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MAX_GATETEXT_LEN = 256
MAX_WGTEXT_LEN = 1000
MAX_WGBOTTEXT_LEN = 512

MIN_POINTS = 5
MAX_POINTS = 99
MIN_STRIKES = 1
MAX_STRIKES = 9

MAX_SUPPORT_ROLES = 10
MAX_SUPPORTTEXT_LEN = 256

MIN_RATELIMITPERUSER = 1
MAX_RATELIMITPERUSER = 21600

LINK_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)"
)


def is_url(string: str, *, fullmatch: bool = True) -> bool:
    if fullmatch and LINK_REGEX.fullmatch(string):
        return True
    elif not fullmatch and LINK_REGEX.match(string):
        return True

    return False


async def _system__runfts(ctx, channel, value):
    await ctx.bot.db.execute("UPDATE system SET RunFTS = ? WHERE GuildID = ?", value, channel.guild_id)


async def system__prefix(ctx, channel, value):
    """The server prefix
    The prefix Solaris responds to, aside from mentions. The default is >>."""
    if not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The server prefix must be a string.")
    elif len(value) > MAX_PREFIX_LEN:
        await channel.send(
            f"{ctx.bot.cross} The server prefix must be no longer than `{MAX_PREFIX_LEN}` characters in length."
        )
    else:
        await ctx.bot.db.execute("UPDATE system SET Prefix = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The server prefix has been set to `{value}`.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The server prefix has been set to `{value}`.")


async def system__logchannel(ctx, channel, value):
    """The log channel
    The channel Solaris uses to communicate important information. It is recommended you keep this channel restricted to members of the server's moderation team. Upon selecting a new channel, Solaris will delete the one that was created during the first time setup should it still exist."""

    perm = lightbulb.utils.permissions_in(
        value,
        ctx.bot.cache.get_member(
            ctx.guild_id,
            ctx.bot.get_me().id
        ),
        True
    )
    
    if not isinstance(value, hikari.GuildTextChannel):
        await channel.send(f"{ctx.bot.cross} The log channel must be a Discord text channel in this server.")
    elif not perm.SEND_MESSAGES:
        await channel.send(
            f"{ctx.bot.cross} The given channel can not be used as the log channel as Solaris can not send messages to it."
        )
    else:
        await ctx.bot.db.execute("UPDATE system SET LogChannelID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The log channel has been set to {value.mention}.")
        await value.send(
            (
                f"{ctx.bot.info} This is the new log channel. Solaris will use this channel to communicate with you if needed. "
                "Configuration updates will also be sent here."
            )
        )

        if (
            perm.MANAGE_CHANNELS
            and (dlc := await retrieve.system__defaultlogchannel(ctx.bot, channel.guild_id)) is not None
        ):
            await dlc.delete(reason="Default log channel was overridden.")
            await value.send(f"{ctx.bot.info} The default log channel has been deleted, as it is no longer required.")


async def system__adminrole(ctx, channel, value):
    """The admin role
    The role used to denote which members can configure Solaris. Alongside server administrators, only members with this role can use any of Solaris' configuration commands. Upon selecting a new channel, Solaris will delete the one that was created during the first time setup should it still exist."""

    bot_user = ctx.bot.cache.get_member(ctx.guild_id, ctx.bot.get_me().id)
    perm = lightbulb.utils.permissions_for(bot_user)
    if len(value) > 1:
        return await ctx.respond(f"{ctx.bot.info} You can only set 1 role for System AdminRole.")
    value = value[0]
    
    if not isinstance(value, hikari.Role):
        await channel.send(f"{ctx.bot.cross} The admin role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{ctx.bot.cross} The everyone role can not be used as the admin role.")
    elif value.name == "@here":
        await channel.send(f"{ctx.bot.cross} The here role can not be used as the admin role.")
    elif value.position > bot_user.get_top_role().position:
        await channel.send(
            f"{ctx.bot.cross} The given role can not be used as the admin role as it is above Solaris' top role in the role hierarchy."
        )
    else:
        await ctx.bot.db.execute("UPDATE system SET AdminRoleID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The admin role has been set to {value.mention}.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The admin role has been set to {value.mention}.")

        if (
            perm.MANAGE_ROLES
            and (dar := await retrieve.system__defaultadminrole(ctx.bot, channel.guild_id)) is not None
        ):
            #await dar.delete(reason="Default admin role was overridden.")
            await ctx.bot.rest.delete_role(ctx.guild_id, dar.id)
            lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
            await lc.send(f"{ctx.bot.info} The default admin role has been deleted, as it is no longer required.")


async def gateway__active(ctx, channel, value):
    """The gateway status
    The utility to know wether your gateway module is active or not."""
    await ctx.bot.db.execute("UPDATE gateway SET Active = ? WHERE GuildID = ?", value, channel.guild_id)


async def gateway__ruleschannel(ctx, channel, value):
    """The rules channel
    The channel that the gate message will be sent to when the module is activated. This channel should contain the server rules, and should be the first channel new members see when they enter the server."""

    perm = lightbulb.utils.permissions_in(
        value,
        ctx.bot.cache.get_member(
            ctx.guild_id,
            ctx.bot.get_me().id
        ),
        True
    )

    if await retrieve.gateway__active(ctx.bot, channel.guild_id):
        await channel.send(f"{ctx.bot.cross} This can not be done as the gateway module is currently active.")
    elif not isinstance(value, hikari.GuildTextChannel):
        await channel.send(f"{ctx.bot.cross} The rules channel must be a Discord text channel in this server.")
    elif not (
        perm.SEND_MESSAGES
        and perm.MANAGE_MESSAGES
    ):
        await channel.send(
            f"{ctx.bot.cross} The given channel can not be used as the rules channel as Solaris can not send messages to it or manage exising messages there."
        )
    else:
        await ctx.bot.db.execute("UPDATE gateway SET RulesChannelID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The rules channel has been set to {value.mention}. Make sure this is the first channel new members see when they join."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The rules channel has been set to {value.mention}.")


async def gateway__gatemessage(ctx, channel, value):
    """The gateway message
    The message that Solaris will show when a new member or bot enters your server."""
    if value is not None:
        await ctx.bot.db.execute("UPDATE gateway SET GateMessageID = ? WHERE GuildID = ?", value.id, channel.guild_id)
    else:
        await ctx.bot.db.execute("UPDATE gateway SET GateMessageID = NULL WHERE GuildID = ?", channel.guild_id)


async def gateway__blockingrole(ctx, channel, value):
    """The blocking role
    The role that Solaris will give new members upon entering the server, and remove when they accept the server rules. This role should prohibit access to all but the rules channel, or all but a read-only category."""

    if len(value) > 1:
        return await ctx.respond(f"{ctx.bot.info} You can only set 1 role for Gateway BlockingRole.")
    value = value[0]
    bot_user = ctx.bot.cache.get_member(ctx.guild_id, ctx.bot.get_me().id)

    if await retrieve.gateway__active(ctx.bot, channel.guild_id):
        await channel.send(f"{ctx.bot.cross} This can not be done as the gateway module is currently active.")
    elif not isinstance(value, hikari.Role):
        await channel.send(f"{ctx.bot.cross} The blocking role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{ctx.bot.cross} The everyone role can not be used as the blocking role.")
    elif value.name == "@here":
        await channel.send(f"{ctx.bot.cross} The here role can not be used as the blocking role.")
    elif value.position >= bot_user.get_top_role().position:
        await channel.send(
            f"{ctx.bot.cross} The given role can not be used as the blocking role as it is above Solaris' top role in the role hierarchy."
        )
    else:
        await ctx.bot.db.execute("UPDATE gateway SET BlockingRoleID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The blocking role has been set to {value.mention}. Make sure the permissions are set correctly."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The blocking role has been set to {value.mention}.")


async def gateway__memberroles(ctx, channel, values):
    """The member roles
    The role(s) that Solaris will give members upon accepting the server rules. This is optional, but could be useful if you want members to have specific roles when they join, for example for a levelling system, or to automatically opt them in to server announcements. You can set up to 3 member roles. The roles can be unset at any time by passing no arguments to the command below."""
    values = [values] if not isinstance(values, list) else values

    bot_user = ctx.bot.cache.get_member(ctx.guild_id, ctx.bot.get_me().id)

    if (br := await retrieve.gateway__blockingrole(ctx.bot, channel.guild_id)) is None:
        await channel.send(f"{ctx.bot.cross} You need to set the blocking role before you can set the member roles.")
    elif values[0] is None:
        await ctx.bot.db.execute("UPDATE gateway SET MemberRoleIDs = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The member roles have been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The member roles have been reset.")
    elif len(values) > MAX_MEMBER_ROLES:
        await channel.send(f"{ctx.bot.cross} You can only set up to `{MAX_MEMBER_ROLES}` member roles.")
    elif not all(isinstance(v, hikari.Role) for v in values):
        await channel.send(f"{ctx.bot.cross} All member roles must be Discord roles in this server.")
    elif any(v.name == "@everyone" for v in values):
        await channel.send(f"{ctx.bot.cross} The everyone role can not be used as a member role.")
    elif any(v.name == "@here" for v in values):
        await channel.send(f"{ctx.bot.cross} The here role can not be used as a member role.")
    elif any(v == br for v in values):
        await channel.send(f"{ctx.bot.cross} No member roles can be the same as the blocking role.")
    elif any(v.position > bot_user.get_top_role().position for v in values):
        await channel.send(
            f"{ctx.bot.cross} One or more given roles can not be used as member roles as they are above Solaris' top role in the role hierarchy."
        )
    else:
        await ctx.bot.db.execute(
            "UPDATE gateway SET MemberRoleIDs = ? WHERE GuildID = ?",
            ",".join(f"{v.id}" for v in values),
            channel.guild_id,
        )
        await channel.send(
            f"{ctx.bot.tick} The member roles have been set to {string.list_of([v.mention for v in values])}. Make sure the permissions are set correctly."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The member roles have been set to {string.list_of([v.mention for v in values])}.")


async def gateway__exceptionroles(ctx, channel, values):
    """The exception roles
    The role(s) that, when given to a new member before they accept the server rules, will grant them access to the server. This is optional, but could be useful if you want members to have access upon receiving a premium role, for example, one given by the Patreon bot. You can set up to 3 exception roles. The roles can be unset at any time by passing no arguments to the command below."""
    values = [values] if not isinstance(values, list) else values

    if (br := await retrieve.gateway__blockingrole(ctx.bot, channel.guild_id)) is None:
        await channel.send(f"{ctx.bot.cross} You need to set the blocking role before you can set the exception roles.")
    elif values[0] is None:
        await ctx.bot.db.execute("UPDATE gateway SET ExceptionRoleIDs = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The exception roles have been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The exception roles have been reset.")
    elif len(values) > MAX_EXCEPTION_ROLES:
        await channel.send(f"{ctx.bot.cross} You can only set up to `{MAX_EXCEPTION_ROLES}` exception roles.")
    elif not all(isinstance(v, hikari.Role) for v in values):
        await channel.send(f"{ctx.bot.cross} All exception roles must be Discord roles in this server.")
    elif any(v.name == "@everyone" for v in values):
        await channel.send(f"{ctx.bot.cross} The everyone role can not be used as an exception role.")
    elif any(v.name == "@here" for v in values):
        await channel.send(f"{ctx.bot.cross} The here role can not be used as an exception role.")
    elif any(v == br for v in values):
        await channel.send(f"{ctx.bot.cross} No exception roles can be the same as the blocking role.")
    else:
        await ctx.bot.db.execute(
            "UPDATE gateway SET ExceptionRoleIDs = ? WHERE GuildID = ?",
            ",".join(f"{v.id}" for v in values),
            channel.guild_id,
        )
        await channel.send(
            f"{ctx.bot.tick} The exception roles have been set to {string.list_of([v.mention for v in values])}."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(
            f"{ctx.bot.info} The exception roles have been set to {string.list_of([v.mention for v in values])}."
        )


async def gateway__welcomechannel(ctx, channel, value):
    """The welcome channel
    The channel that Solaris will send welcome messages to upon a member accepting the server rules. If no channel is set, Solaris will not send welcome messages. The channel can be unset at any time by passing no arguments to the command below. Note that Solaris does not send welcome messages in all situations, such as if the member received an exception role."""

    perm = lightbulb.utils.permissions_in(
        value,
        ctx.bot.cache.get_member(
            ctx.guild_id,
            ctx.bot.get_me().id
        ),
        True
    )

    if (rc := await retrieve.gateway__ruleschannel(ctx.bot, channel.guild_id)) is None:
        await channel.send(f"{ctx.bot.cross} You need to set the rules channel before you can set the welcome channel.")
    elif value is None:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeChannelID = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The welcome channel has been reset. Solaris will stop sending welcome messages."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild)
        await lc.send(f"{ctx.bot.info} The welcome channel has been reset.")
    elif not isinstance(value, hikari.GuildTextChannel):
        await channel.send(f"{ctx.bot.cross} The welcome channel must be a Discord text channel in this server.")
    elif value == rc:
        await channel.send(f"{ctx.bot.cross} The welcome channel can not be the same as the rules channel.")
    elif not perm.SEND_MESSAGES:
        await channel.send(
            f"{ctx.bot.cross} The given channel can not be used as the welcome channel as Solaris can not send messages to it."
        )
    else:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeChannelID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The welcome channel has been set to {value.mention}.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The welcome channel has been set to {value.mention}.")


async def gateway__goodbyechannel(ctx, channel, value):
    """The goodbye channel
    The channel that Solaris will send goodbye messages to upon a member leaving the server. If no channel is set, Solaris will not send goodbye messages. The channel can be unset at any time by passing no arguments to the command below. Note that Solaris will only send goodbye messages for members who have accepted the server rules, or members who were in the server before the module was activated."""

    perm = lightbulb.utils.permissions_in(
        value,
        ctx.bot.cache.get_member(
            ctx.guild_id,
            ctx.bot.get_me().id
        ),
        True
    )

    if (rc := await retrieve.gateway__ruleschannel(ctx.bot, channel.guild_id)) is None:
        await channel.send(f"{ctx.bot.cross} You need to set the rules channel before you can set the goodbye channel.")
    elif value is None:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeChannelID = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The goodbye channel has been reset. Solaris will stop sending goodbye messages."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye channel has been reset.")
    elif not isinstance(value, hikari.GuildTextChannel):
        await channel.send(f"{ctx.bot.cross} The goodbye channel must be a Discord text channel in this server.")
    elif value == rc:
        await channel.send(f"{ctx.bot.cross} The goodbye channel can not be the same as the rules channel.")
    elif not perm.SEND_MESSAGES:
        await channel.send(
            f"{ctx.bot.cross} The given channel can not be used as the goodbye channel as Solaris can not send messages to it."
        )
    else:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeChannelID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The goodbye channel has been set to {value.mention}.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye channel has been set to {value.mention}.")


async def gateway__timeout(ctx, channel, value):
    """The gateway timeout
    The amount of time Solaris gives new members to react to the gate message before being kicked. This is set in minutes, and can be set to any value between 1 and 60 inclusive. If no timeout is set, the default is 5 minutes. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET Timeout = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The timeout has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The timeout has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{ctx.bot.cross} The timeout must be an integer number.")
    elif not MIN_TIMEOUT <= value <= MAX_TIMEOUT:
        await channel.send(
            f"{ctx.bot.cross} The timeout must be between `{MIN_TIMEOUT}` and `{MAX_TIMEOUT}` minutes inclusive."
        )
    else:
        await ctx.bot.db.execute("UPDATE gateway SET Timeout = ? WHERE GuildID = ?", value * 60, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The timeout has been set to `{value}` minute(s). This will only apply to members who enter the server from now."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The timeout has been set to `{value}` minute(s).")


async def gateway__gatetext(ctx, channel, value):
    """The gate message text
    The message displayed in the gate message. The message can be up to 250 characters in length, and should **not** contain the server rules. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET GateText = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The gate message text has been reset. The module needs to be restarted for these changes to take effect."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The gate message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The gate message text must be a string.")
    elif len(value) > MAX_GATETEXT_LEN:
        await channel.send(
            f"{ctx.bot.cross} The gate message text must be no longer than `{MAX_GATETEXT_LEN:,}` characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{ctx.bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await ctx.bot.db.execute("UPDATE gateway SET GateText = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The gate message text has been set. The module needs to be restarted for these changes to take effect."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The gate message text has been set to the following: ```\n{value}\n```")


async def gateway__welcometext(ctx, channel, value):
    """The welcome message text
    The message sent to the welcome channel (if set) when a new member accepts the server rules. This message can be up to 1,000 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeText = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The welcome message text has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The welcome message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The welcome message text must be a string.")
    elif len(value) > MAX_WGTEXT_LEN:
        await channel.send(
            f"{ctx.bot.cross} The welcome message text must be no longer than `{MAX_WGTEXT_LEN:,}` characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{ctx.bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeText = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The welcome message text has been set.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The welcome message text has been set to the following: ```\n{value}\n```")


async def gateway__goodbyetext(ctx, channel, value):
    """The goodbye message text
    The message sent to the goodbye channel (if set) when a member leaves the server. This message can be up to 1,000 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeText = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The goodbye message text has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The goodbye message text must be a string.")
    elif len(value) > MAX_WGTEXT_LEN:
        await channel.send(
            f"{ctx.bot.cross} The goodbye message text must be no longer than `{MAX_WGTEXT_LEN:,}` characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{ctx.bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeText = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The goodbye message text has been set.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye message text has been set to the following: ```\n{value}\n```")


async def gateway__welcomebottext(ctx, channel, value):
    """The welcome message text for bots
    The message sent to the welcome channel (if set) when a bot joins the server. This message can be up to 500 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeBotText = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The welcome bot message text has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The welcome bot message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The welcome bot message text must be a string.")
    elif len(value) > MAX_WGBOTTEXT_LEN:
        await channel.send(
            f"{ctx.bot.cross} The welcome bot message text must be no longer than `{MAX_WGBOTTEXT_LEN:,}` characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{ctx.bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await ctx.bot.db.execute("UPDATE gateway SET WelcomeBotText = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The welcome bot message text has been set.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The welcome bot message text has been set to the following: ```\n{value}\n```")


async def gateway__goodbyebottext(ctx, channel, value):
    """The goodbye message text for bots
    The message sent to the goodbye channel (if set) when a bot leaves the server. This message can be up to 500 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeBotText = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The goodbye bot message text has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye bot message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{ctx.bot.cross} The goodbye bot message text must be a string.")
    elif len(value) > MAX_WGBOTTEXT_LEN:
        await channel.send(
            f"{ctx.bot.cross} The goodbye bot message text must be no longer than `{MAX_WGBOTTEXT_LEN:,}` characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{ctx.bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await ctx.bot.db.execute("UPDATE gateway SET GoodbyeBotText = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The goodbye bot message text has been set.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The goodbye bot message text has been set to the following: ```\n{value}\n```")


async def warn__warnrole(ctx, channel, value):
    """The warn role
    The role that members need to have in order to warn other members, typically a moderator or staff role. If this is not set, only server administrators will be able to warn members. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE warn SET WarnRoleID = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The warn role has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The warn role has been reset.")
    elif not isinstance(value, hikari.Role):
        await channel.send(f"{ctx.bot.cross} The warn role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{ctx.bot.cross} The everyone role can not be used as the warn role.")
    elif value.name == "@here":
        await channel.send(f"{ctx.bot.cross} The here role can not be used as the warn role.")
    else:
        await ctx.bot.db.execute("UPDATE warn SET WarnRoleID = ? WHERE GuildID = ?", value.id, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The warn role has been set to {value.mention}.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The warn role has been set to {value.mention}.")


async def warn__maxpoints(ctx, channel, value):
    """The max points total
    The number of points a member needs in total to get banned from a warning. This can be set to any value between 5 and 99 inclusive. If no value is set, the default is 12. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE warn SET MaxPoints = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The max points total has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The max points total has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{ctx.bot.cross} The max points total must be an integer number.")
    elif not MIN_POINTS <= value <= MAX_POINTS:
        await channel.send(
            f"{ctx.bot.cross} The max points total must be between `{MIN_POINTS}` and `{MAX_POINTS}` inclusive."
        )
    else:
        await ctx.bot.db.execute("UPDATE warn SET MaxPoints = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The max points total has been set to `{value}`. Members currently at or exceeding this total will not be retroactively banned."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The max points total has been set to `{value}`.")


async def warn__maxstrikes(ctx, channel, value):
    """The max strikes per offence
    The number of times a member needs to be warned of a particular offence to get banned from a warning. This is per offence, and not a total number of strikes. This can be set to any value between 1 and 9 inclusive. If no value is set, the default is 3. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await ctx.bot.db.execute("UPDATE warn SET MaxStrikes = NULL WHERE GuildID = ?", channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The max strikes per offence has been reset.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The max strikes per offence has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{ctx.bot.cross} The max strikes per offence must be an integer number.")
    elif not MIN_STRIKES <= value <= MAX_STRIKES:
        await channel.send(
            f"{ctx.bot.cross} The max strikes per offence must be between `{MIN_STRIKES}` and `{MAX_STRIKES}` inclusive."
        )
    else:
        await ctx.bot.db.execute("UPDATE warn SET MaxStrikes = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(
            f"{ctx.bot.tick} The max strikes per offence has been set to `{value}`. Members currently at or exceeding this total will not be retroactively banned."
        )
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The max strikes per offence has been set to `{value}`.")


async def warn__retroupdates(ctx, channel, value):
    """Retroactive updates
    Whether to update already instated warns that did not receive a points override with new points values when warn types are modified with the `warntype edit` command. This can be set to either 0 (OFF) or 1 (ON). Defaults to 0 (OFF)."""
    if not isinstance(value, int):
        await channel.send(f"{ctx.bot.cross} The retroactive updates toggle must be an integer number.")
    elif not 0 <= value <= 1:
        await channel.send(f"{ctx.bot.cross} The retroactive updates toggle must be either 0 or 1.")
    else:
        await ctx.bot.db.execute("UPDATE warn SET RetroUpdates = ? WHERE GuildID = ?", value, channel.guild_id)
        await channel.send(f"{ctx.bot.tick} The retroactive updates toggle has been set to `{value}`.")
        lc = await retrieve.log_channel(ctx.bot, channel.guild_id)
        await lc.send(f"{ctx.bot.info} The retroactive updates toggle has been set to `{value}`.")
