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

from hikari import Embed

from datetime import datetime

from solaris.utils import DEFAULT_EMBED_COLOUR


class EmbedConstructor:
    def __init__(self, bot):
        self.bot = bot

    def build(self, **kwargs):
        ctx = kwargs.get("ctx")

        embed = Embed(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            colour=(
                kwargs.get("colour")
                or (ctx.member.get_top_role().color if ctx and ctx.member.get_top_role().color else None)
                or DEFAULT_EMBED_COLOUR
            ),
            timestamp=datetime.now().astimezone(),
        )

        embed.set_author(name=kwargs.get("header", "Blue Brain"))
        embed.set_footer(
            text=kwargs.get("footer", f"Invoked by {ctx.author.username}" if ctx else r"\o/"),
            icon=ctx.author.avatar_url if ctx else self.bot.get_me().avatar_url,
        )

        if thumbnail := kwargs.get("thumbnail"):
            embed.set_thumbnail(thumbnail)

        if image := kwargs.get("image"):
            embed.set_image(image)

        for name, value, inline in kwargs.get("fields", ()):
            embed.add_field(name=name, value=value, inline=inline)

        return embed