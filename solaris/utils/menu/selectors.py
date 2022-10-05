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
from datetime import timedelta
from asyncio import TimeoutError

from solaris import Config
from solaris.utils import chron


class Selector:
    def __init__(self, menu, selection, *, timeout=300.0, auto_exit=True, check=None):
        self.menu = menu
        self.timeout = timeout
        self.auto_exit = auto_exit
        self.check = check or self._default_check

        self._base_selection = selection

    @property
    def selection(self):
        return self._base_selection

    @selection.setter
    def selection(self, value):
        self._base_selection = value

    def _default_check(self, reaction):
        return (
            reaction.message_id == self.menu.message.id
            and reaction.user_id == self.menu.ctx.author.id
            and reaction.emoji_name in self.selection
        )

    async def _serve(self):
        await self.menu.message.remove_all_reactions()
        emoji = await self.menu.bot.rest.fetch_guild(Config.HUB_GUILD_ID)

        for e in self.selection:
            await self.menu.message.add_reaction(emoji.get_emoji(int(e)))

    async def response(self):
        await self._serve()

        def predicate(event: hikari.ReactionAddEvent) -> bool:
            return event.user_id == self.menu.ctx.author.id and event.message_id == self.menu.message.id

        try:
            reaction = await self.menu.bot.wait_for(hikari.ReactionAddEvent, timeout=self.timeout, predicate=predicate)
        except TimeoutError:
            await self.menu.timeout(chron.long_delta(timedelta(seconds=self.timeout)))
        else:
            if (r := reaction.emoji_name) == "exit" and self.auto_exit:
                await self.menu.stop()
            else:
                return r
        

    def __repr__(self):
        return (
            f"<Selector"
            f" timeout={self.timeout!r}"
            f" auto_exit={self.auto_exit!r}"
            f" check={self.check!r}"
            f" menu={self.menu!r}>"
        )


class NumericalSelector(Selector):
    def __init__(self, menu, iterable, *, timeout=300.0, auto_exit=True, check=None):
        super().__init__(menu, [str(Config.EXIT_EMOJI_ID)], timeout=timeout, auto_exit=auto_exit, check=check)

        self.iterable = iterable
        self.max_page = (len(iterable) // 9) + 1
        self.pages = [{} for i in range(self.max_page)]

        self._selection = []
        self._last_selection = []
        self._page = 0

        for i, obj in enumerate(iterable):
            self.pages[i // 9].update({f"option{(i % 9) + 1}": obj})

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        self._last_selection = self._selection
        self._selection = value

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = max(0, min(value, self.max_page - 1))

    @property
    def last_selection(self):
        return self._last_selection

    @property
    def page_info(self):
        return f"Page {self.page + 1:,} of {self.max_page:,}"

    @property
    async def table(self):
        emoji_dic = {
            "option1": Config.OPTION1_EMOJI_ID,
            "option2": Config.OPTION2_EMOJI_ID,
            "option3": Config.OPTION3_EMOJI_ID,
            "option4": Config.OPTION4_EMOJI_ID,
            "option5": Config.OPTION5_EMOJI_ID,
            "option6": Config.OPTION6_EMOJI_ID,
            "option7": Config.OPTION7_EMOJI_ID,
            "option8": Config.OPTION8_EMOJI_ID,
            "option9": Config.OPTION9_EMOJI_ID

        }
        emoji = await self.menu.bot.rest.fetch_guild(Config.HUB_GUILD_ID)
        return "\n".join(f"{emoji.get_emoji(emoji_dic[k]).mention} {v}" for k, v in self.pages[self.page].items())

    def set_selection(self):
        s = self._base_selection.copy()
        insert_point = 0
        options = [
            Config.OPTION1_EMOJI_ID, 
            Config.OPTION2_EMOJI_ID, 
            Config.OPTION3_EMOJI_ID, 
            Config.OPTION4_EMOJI_ID, 
            Config.OPTION5_EMOJI_ID, 
            Config.OPTION6_EMOJI_ID, 
            Config.OPTION7_EMOJI_ID, 
            Config.OPTION8_EMOJI_ID, 
            Config.OPTION9_EMOJI_ID
        ]

        if len(self.pages) > 1:
            if self.page != 0:
                s.insert(0, str(Config.PAGE_BACK_EMOJI_ID))
                s.insert(0, str(Config.STEP_BACK_EMOJI_ID))
                insert_point += 2

            if self.page != self.max_page - 1:
                s.insert(insert_point, str(Config.STEP_NEXT_EMOJI_ID))
                s.insert(insert_point, str(Config.PAGE_NEXT_EMOJI_ID))
        for i in range(len(self.pages[self.page])):
            s.insert(i + insert_point, options[i])

        self.selection = s

    async def response(self):
        self.set_selection()

        if self.selection != self.last_selection:
            await self._serve()
 
        def predicate(event: hikari.ReactionAddEvent) -> bool:
            return event.user_id == self.menu.ctx.author.id and event.message_id == self.menu.message.id

        try:
            reaction = await self.menu.bot.wait_for(hikari.ReactionAddEvent, timeout=self.timeout, predicate=predicate)
        except TimeoutError:
            await self.menu.timeout(chron.long_delta(timedelta(seconds=self.timeout)))
        else:
            if (r := reaction.emoji_name) == "exit":
                if self.auto_exit:
                    await self.menu.stop()
                return
            elif r == "stepback":
                self.page = 0
            elif r == "pageback":
                self.page -= 1
            elif r == "pagenext":
                self.page += 1
            elif r == "stepnext":
                self.page = self.max_page
            else:
                return self.pages[self.page][r]

            await self.menu.switch(reaction.emoji_name, reaction.emoji_id)
            return await self.response()

    def __repr__(self):
        return (
            f"<NumericalSelector"
            f" page={self.page!r}"
            f" max_page={self.max_page!r}"
            f" timeout={self.timeout!r}"
            f" auto_exit={self.auto_exit!r}"
            f" check={self.check!r}"
            f" menu={self.menu!r}>"
        )


class PageControls(Selector):
    def __init__(self, menu, pagemaps, *, timeout=300.0, auto_exit=True, check=None):
        super().__init__(menu, [str(Config.EXIT_EMOJI_ID)], timeout=timeout, auto_exit=auto_exit, check=check)

        self.pagemaps = pagemaps
        self.max_page = len(pagemaps)

        self._selection = []
        self._last_selection = []
        self._page = 0

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        self._last_selection = self._selection
        self._selection = value

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = max(0, min(value, self.max_page - 1))

    @property
    def last_selection(self):
        return self._last_selection

    @property
    def page_info(self):
        return f"Page {self.page + 1:,} of {self.max_page:,}"

    def set_selection(self):
        s = self._base_selection.copy()
        insert_point = 0

        if len(self.pagemaps) > 1:
            if self.page != 0:
                s.insert(0, str(Config.PAGE_BACK_EMOJI_ID))
                s.insert(0, str(Config.STEP_BACK_EMOJI_ID))
                insert_point += 2

            if self.page != self.max_page - 1:
                s.insert(insert_point, str(Config.STEP_NEXT_EMOJI_ID))
                s.insert(insert_point, str(Config.PAGE_NEXT_EMOJI_ID))

        self.selection = s

    async def response(self):
        self.set_selection()

        if self.selection != self.last_selection:
            await self._serve()

        def predicate(event: hikari.ReactionAddEvent) -> bool:
            return event.user_id == self.menu.ctx.author.id and event.message_id == self.menu.message.id

        try:
            reaction = await self.menu.bot.wait_for(hikari.ReactionAddEvent, timeout=self.timeout, predicate=predicate)
        except TimeoutError:
            await self.menu.timeout(chron.long_delta(timedelta(seconds=self.timeout)))
        else:
            if (r := reaction.emoji_name) == "exit":
                if self.auto_exit:
                    await self.menu.stop()
                return
            elif r == "stepback":
                self.page = 0
            elif r == "pageback":
                self.page -= 1
            elif r == "pagenext":
                self.page += 1
            elif r == "stepnext":
                self.page = self.max_page

            await self.menu.switch(reaction.emoji_name, reaction.emoji_id)
            return await self.response()

    def __repr__(self):
        return (
            f"<NumericalSelector"
            f" page={self.page!r}"
            f" max_page={self.max_page!r}"
            f" timeout={self.timeout!r}"
            f" auto_exit={self.auto_exit!r}"
            f" check={self.check!r}"
            f" menu={self.menu!r}>"
        )