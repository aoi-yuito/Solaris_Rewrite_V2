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

import typing as t

import hikari
import lightbulb
from lightbulb import commands

from solaris import Config
from solaris.utils import ERROR_ICON, LOADING_ICON, SUCCESS_ICON, checks, menu, modules


class SetupMenu(menu.SelectionMenu):
    def __init__(module, ctx):
        pagemap = {
            "header": "Setup Wizard",
            "title": "Hello!",
            "description": "Welcome to the Solaris' first time setup! You need to run this before you can use most of Solaris' commands, but you only ever need to run once.\n\nIn order to operate effectively in your server, Solaris needs to create a few things:",
            "thumbnail": ctx.bot.get_me().avatar_url,
            "fields": (
                (
                    "A log channel",
                    "This will be called `solaris-logs` and will be placed directly under the channel you run the setup in. This channel is what Solaris will use to communicate important information to you, so it is recommended you only allow server moderators access to it. You will be able to change what Solaris uses as the log channel later.",
                    False,
                ),
                (
                    "An admin role",
                    "This will be called `Solaris Administrator` and will be placed at the bottom of the role hierarchy. This role does not provide members any additional access to the server, but does allow them to use Solaris' configuration commands. Server administrators do not need this role to configure Solaris. You will be able to change what Solaris uses as the admin role later.",
                    False,
                ),
                (
                    "Ready?",
                    f"If you are ready to run the setup, select {ctx.bot.tick}. To exit the setup without changing anything select {ctx.bot.cross}.",
                    False,
                ),
            ),
        }
        super().__init__(ctx, [str(Config.ACCEPT_EMOJI_ID), str(Config.CANCEL_EMOJI_ID)], pagemap, timeout=120.0)

    async def start(module):
        r = await super().start()

        if r == "confirm":
            pagemap = {
                "header": "Setup Wizard",
                "description": "Please wait... This should only take a few seconds.",
                "thumbnail": LOADING_ICON,
            }
            await module.switch(pagemap, remove_all_reactions=True)
            await module.run()
        elif r == "cancel":
            await module.stop()

    async def run(module):
        if not await modules.retrieve.system__logchannel(module.bot, module.ctx.guild_id):
            perm = lightbulb.utils.permissions_for(
                await module.bot.rest.fetch_member(
                    module.ctx.guild_id,
                    module.bot.get_me().id
                )
            )
            permi = []
            perm1 = hikari.PermissionOverwrite(
                id=module.ctx.guild_id,
                type=hikari.PermissionOverwriteType.ROLE,
                allow=hikari.Permissions.NONE,
                deny=(
                    hikari.Permissions.SEND_MESSAGES|
                    hikari.Permissions.READ_MESSAGE_HISTORY|
                    hikari.Permissions.VIEW_CHANNEL
                )
            )
            permi.append(perm1)
            perm2 = hikari.PermissionOverwrite(
                id=module.bot.get_me().id,
                type=hikari.PermissionOverwriteType.MEMBER,
                allow=(
                    hikari.Permissions.SEND_MESSAGES|
                    hikari.Permissions.READ_MESSAGE_HISTORY|
                    hikari.Permissions.VIEW_CHANNEL|
                    hikari.Permissions.ADD_REACTIONS|
                    hikari.Permissions.ATTACH_FILES|
                    hikari.Permissions.EMBED_LINKS|
                    hikari.Permissions.USE_APPLICATION_COMMANDS|
                    hikari.Permissions.USE_EXTERNAL_EMOJIS|
                    hikari.Permissions.USE_EXTERNAL_STICKERS|
                    hikari.Permissions.SEND_MESSAGES_IN_THREADS
                ),
                deny=hikari.Permissions.NONE
            )
            permi.append(perm2)
            
            if perm.MANAGE_CHANNELS:
                lc = await module.ctx.get_guild().create_text_channel(
                    name="solaris-logs",
                    category=module.ctx.get_channel().parent_id,
                    position=module.ctx.get_channel().position,
                    permission_overwrites=permi,
                    topic=f"Log output for {module.ctx.bot.get_me().mention}",
                    reason="Needed for Solaris log output.",
                )
                await module.bot.db.execute(
                    "UPDATE system SET DefaultLogChannelID = ?, LogChannelID = ? WHERE GuildID = ?",
                    lc.id,
                    lc.id,
                    module.ctx.guild_id,
                )
                await lc.send(f"{module.bot.tick} The log channel has been created and set to {lc.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": "The log channel could not be created as Solaris does not have the Manage Channels permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await module.switch(pagemap)
                return
        
        if not await modules.retrieve.system__adminrole(module.bot, module.ctx.guild_id):
            perm = lightbulb.utils.permissions_for(
                await module.bot.rest.fetch_member(
                    module.ctx.guild_id,
                    module.bot.get_me().id
                )
            )
            
            if perm.MANAGE_ROLES:
                ar = await module.bot.rest.create_role(
                    guild=module.ctx.guild_id,
                    name="Solaris Administrator",
                    permissions=hikari.Permissions(value=0),
                    reason="Needed for Solaris configuration.",
                )
                await module.bot.db.execute(
                    "UPDATE system SET DefaultAdminRoleID = ?, AdminRoleID = ? WHERE GuildID = ?",
                    ar.id,
                    ar.id,
                    module.ctx.guild_id,
                )
                perm3 = hikari.PermissionOverwrite(
                	id=ar.id,
                	type=hikari.PermissionOverwriteType.ROLE,
                	allow=(
                    	hikari.Permissions.SEND_MESSAGES|
                    	hikari.Permissions.READ_MESSAGE_HISTORY|
                    	hikari.Permissions.VIEW_CHANNEL|
                    	hikari.Permissions.CHANGE_NICKNAME|
                    	hikari.Permissions.CREATE_PUBLIC_THREADS|
                    	hikari.Permissions.MODERATE_MEMBERS|
                    	hikari.Permissions.MUTE_MEMBERS|
                    	hikari.Permissions.MENTION_ROLES|
                    	hikari.Permissions.MANAGE_NICKNAMES|
                    	hikari.Permissions.MANAGE_CHANNELS|
                    	hikari.Permissions.DEAFEN_MEMBERS|
                    	hikari.Permissions.MANAGE_ROLES|
                    	hikari.Permissions.MANAGE_EMOJIS_AND_STICKERS|
                    	hikari.Permissions.MANAGE_GUILD|
                    	hikari.Permissions.ADD_REACTIONS|
                    	hikari.Permissions.ATTACH_FILES|
                    	hikari.Permissions.EMBED_LINKS|
                    	hikari.Permissions.USE_APPLICATION_COMMANDS|
                    	hikari.Permissions.USE_EXTERNAL_EMOJIS|
                    	hikari.Permissions.USE_EXTERNAL_STICKERS|
                    	hikari.Permissions.SEND_MESSAGES_IN_THREADS
                	),
                	deny=hikari.Permissions.NONE
            	)
                permi.append(perm3)
                await lc.edit(permission_overwrites=permi)
                await lc.send(f"{module.bot.tick} The admin role has been created and set to {ar.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": "The admin role could not be created as Solaris does not have the Manage Roles permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await module.switch(pagemap)
                return

        await module.complete()

    async def configure_modules(module):
        await module.complete()

    async def complete(module):
        pagemap = {
            "header": "Setup",
            "title": "First time setup complete",
            "description": "Congratulations - the first time setup has been completed! You can now use all of Solaris' commands, and activate all of Solaris' modules.\n\nEnjoy using Solaris!",
            "thumbnail": SUCCESS_ICON,
        }
        await modules.config._system__runfts(module.ctx, module.ctx.get_channel(), 1)
        await module.switch(pagemap, remove_all_reactions=True)


module = lightbulb.plugins.Plugin(
    name="Modules",
    description="Configure, activate, and deactivate Solaris modules.",
    include_datastore=True
)


@module.listener(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent):
    if not module.bot.ready.booted:
        module.bot.ready.up(module)

    module.d.configurable: bool = False
    module.d.image = "https://cdn.discordapp.com/attachments/991572493267636275/991585172925452338/module.png"


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_not_run())
@lightbulb.add_checks(checks.guild_is_not_discord_bot_list())
@lightbulb.command(name="setup", description="Runs the first time setup.")
@lightbulb.implements(commands.prefix.PrefixCommand)
async def setup_command(ctx: lightbulb.context.base.Context) -> None:
    await SetupMenu(ctx).start()


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command(name="config", aliases=["set"], description="Configures Solaris; use `help config` to bring up a special help menu.")
@lightbulb.implements(commands.prefix.PrefixCommandGroup)
async def config_group(ctx: lightbulb.context.base.Context):
    cmds = []
    prefix = await ctx.bot.prefix(ctx.guild_id)
    cmds_list = sorted(ctx.command.subcommands.values(), key=lambda c: c.name)
    for cmd in cmds_list:
        if cmd not in cmds:
            cmds.append(cmd)

    await ctx.respond(
        embed=ctx.bot.embed.build(
            ctx=ctx,
            header="Config",
            thumbnail="https://cdn.discordapp.com/attachments/991572493267636275/991585569647906836/config.png",
            description="There are a few different config methods you can use.",
            fields=(
                *(
                    (
                        cmd.name.title(),
                        f"{cmd.description} For more infomation, use `{prefix}help config {cmd.name}`",
                        False,
                    )
                    for cmd in cmds
                ),
            ),
        )
    )


@config_group.child()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="target", description="Name of the channels to set.", type=hikari.GuildChannel, required=True)
@lightbulb.option(name="attr", description="Name of the attribute to configure.", type=str, required=True)
@lightbulb.option(name="module", description="Name of the module to configure.", type=str, required=True)
@lightbulb.command(name="channels", aliases=["ch"], description="Configures channels of the specified module.")
@lightbulb.implements(commands.PrefixSubCommand)
async def config_channels_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_") or ctx.options.attr.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module or attribute you are trying to access is non-configurable.")
    elif "channel" in ctx.options.attr or "channels" in ctx.options.attr:
        if (func := getattr(modules.config, f"{ctx.options.module}__{ctx.options.attr}", None)) is not None:
            await func(ctx, ctx.get_channel(), ctx.options.target)
        else:
            await ctx.respond(f"{ctx.bot.cross} Invalid module or attribute.")
    else:
        await ctx.respond(f"{ctx.bot.cross} The attribute you are trying to access is not related to channel objects.")


@config_group.child()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="targets", description="Name of the roles to set.", type=hikari.Role, modifier=lightbulb.commands.base.OptionModifier.GREEDY, required=True)
@lightbulb.option(name="attr", description="Name of the attribute to configure.", type=str, required=True)
@lightbulb.option(name="module", description="Name of the module to configure.", type=str, required=True)
@lightbulb.command(name="roles", aliases=["r"], description="Configures roles of the specified module.")
@lightbulb.implements(commands.PrefixSubCommand)
async def config_roles_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_") or ctx.options.attr.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module or attribute you are trying to access is non-configurable.")
    elif "role" in ctx.options.attr or "roles" in ctx.options.attr:
        if (func := getattr(modules.config, f"{ctx.options.module}__{ctx.options.attr}", None)) is not None:
            await func(ctx, ctx.get_channel(), ctx.options.targets)
        else:
            await ctx.respond(f"{ctx.bot.cross} Invalid module or attribute.")
    else:
        await ctx.respond(f"{ctx.bot.cross} The attribute you are trying to access is not related to role objects.")


@config_group.child()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="value", description="The integer value to set.", type=int, required=True)
@lightbulb.option(name="attr", description="Name of the attribute to configure.", type=str, required=True)
@lightbulb.option(name="module", description="Name of the module to configure.", type=str, required=True)
@lightbulb.command(name="integer", aliases=["i"], description="Configures integer of the specified module.")
@lightbulb.implements(commands.PrefixSubCommand)
async def config_integer_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_") or ctx.options.attr.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module or attribute you are trying to access is non-configurable.")
    elif "points" in ctx.options.attr or "updates" in ctx.options.attr or "strikes" in ctx.options.attr or "timeout" in ctx.options.attr or "active" in ctx.options.attr or "status" in ctx.options.attr:        
        if (func := getattr(modules.config, f"{ctx.options.module}__{ctx.options.attr}", None)) is not None:
            await func(ctx, ctx.get_channel(), ctx.options.value)
        else:
            await ctx.respond(f"{ctx.bot.cross} Invalid module or attribute.")
    else:
        await ctx.respond(f"{ctx.bot.cross} The attribute you are trying to access is not related to integer objects.")


@config_group.child()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="text", description="The string or text or message to set.", type=str, required=True, modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option(name="attr", description="Name of the attribute to configure.", type=str, required=True)
@lightbulb.option(name="module", description="Name of the module to configure.", type=str, required=True)
@lightbulb.command(name="string", aliases=["s"], description="Configures string of the specified module.")
@lightbulb.implements(commands.PrefixSubCommand)
async def config_string_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_") or ctx.options.attr.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module or attribute you are trying to access is non-configurable.")
    elif "message" in ctx.options.attr or "prefix" in ctx.options.attr or "text" in ctx.options.attr:
        if (func := getattr(modules.config, f"{ctx.options.module}__{ctx.options.attr}", None)) is not None:
            await func(ctx, ctx.get_channel(), ctx.options.text)
        else:
            await ctx.respond(f"{ctx.bot.cross} Invalid module or attribute.")
    else:
        await ctx.respond(f"{ctx.bot.cross} The attribute you are trying to access is not related to string objects.")


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="attr", description="Name of the attribute to retrieve.", type=str)
@lightbulb.option(name="module", description="Name of the module to retrieve.", type=str)
@lightbulb.command(name="retrieve", aliases=["get"], description="Retrieves attribute information for a module. Note that the output is raw.")
@lightbulb.implements(commands.prefix.PrefixCommand)
async def retrieve_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_") or ctx.options.attr.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module or attribute you are trying to access is non-configurable.")
    elif (func := getattr(modules.retrieve, f"{ctx.options.module}__{ctx.options.attr}", None)) is not None:
        v = await func(ctx.bot, ctx.get_guild().id)
        value = getattr(v, "mention", v)
        await ctx.respond(f"{ctx.bot.info} Value of {ctx.options.attr}: {value}")
    else:
        await ctx.respond(f"{ctx.bot.cross} Invalid module or attribute.")


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.log_channel_is_set())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="module", description="Name of the module to activate.", type=str)
@lightbulb.command(name="activate", aliases=["enable"], description="Activates a module.")
@lightbulb.implements(commands.prefix.PrefixCommand)
async def activate_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module you are trying to access is non-configurable.")
    elif (func := getattr(modules.activate, ctx.options.module, None)) is not None:
        await func(ctx)
    else:
        await ctx.respond(f"{ctx.bot.cross} That module either does not exist, or can not be activated.")


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.log_channel_is_set())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="module", description="Name of the module to retrieve.", type=str)
@lightbulb.command(name="deactivate", aliases=["disable"], description="Deactivates a module.")
@lightbulb.implements(commands.prefix.PrefixCommand)
async def deactivate_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module you are trying to access is non-configurable.")
    elif (func := getattr(modules.deactivate, ctx.options.module, None)) is not None:
        await func(ctx)
    else:
        await ctx.respond(f"{ctx.bot.cross} That module either does not exist, or can not be deactivated.")


@module.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(checks.bot_is_ready())
@lightbulb.add_checks(checks.log_channel_is_set())
@lightbulb.add_checks(checks.author_can_configure())
@lightbulb.add_checks(checks.first_time_setup_has_run())
@lightbulb.option(name="module", description="Name of the module to retrieve.", type=str)
@lightbulb.command(name="restart", description="Restarts a module. This is a shortcut command which calls `deactivate` then `activate`.")
@lightbulb.implements(commands.prefix.PrefixCommand)
async def restart_command(ctx: lightbulb.context.base.Context) -> None:
    if ctx.options.module.startswith("_"):
        await ctx.respond(f"{ctx.bot.cross} The module you are trying to access is non-configurable.")
    elif (dfunc := getattr(modules.deactivate, ctx.options.module, None)) is not None and (
        afunc := getattr(modules.activate, ctx.options.module, None)
    ) is not None:
        await dfunc(ctx)
        await afunc(ctx)
    else:
        await ctx.respond(f"{ctx.bot.cross} That module either does not exist, or can not be restarted.")


def load(bot) -> None:
    bot.add_plugin(module)

def unload(bot) -> None:
    bot.remove_plugin(module)
