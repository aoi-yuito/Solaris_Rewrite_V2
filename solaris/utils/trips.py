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

import hikari

from solaris.utils.modules import retrieve


async def gateway(okay, reason):
    rc_id, gm_id = (
        await okay.bot.db.record("SELECT RulesChannelID, GateMessageID FROM gateway WHERE GuildID = ?", okay.ctx.guild_id,)
        or [None] * 2
    )
    lc = await retrieve.log_channel(okay.bot, okay.ctx.guild_id)

    try:
        if (rc := okay.bot.cache.get_guild_channel(rc_id)) is not None:
            gm = await okay.bot.rest.fetch_message(rc_id, gm_id)
            await gm.delete()
            await lc.send(f"{okay.bot.info} The gate message was deleted.")
    except (hikari.NotFoundError, hikari.ForbiddenError):
        pass

    await okay.bot.db.execute("DELETE FROM entrants WHERE GuildID = ?", okay.ctx.guild_id)
    await okay.bot.db.execute("UPDATE gateway SET Active = 0, GateMessageID = NULL WHERE GuildID = ?", okay.ctx.guild_id)
    await lc.send(
        f"{okay.bot.cross} The gateway module tripped because {reason}. You will need to fix the problem and re-activate the module to use it again."
    )