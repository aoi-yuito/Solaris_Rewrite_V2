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

# Ethan Henderson
# parafoxia@carberra.xyz

from os import getenv
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class Config:
    try:
        # Load production token.
        with open(getenv("TOKEN", "")) as f:
            token = f.read()
    except FileNotFoundError:
        # Load development token.
        token = getenv("TOKEN", "")

    TOKEN: Final = token
    DEFAULT_PREFIX: Final = getenv("DEFAULT_PREFIX", ">>")
    HUB_GUILD_ID: Final = int(getenv("HUB_GUILD_ID", ""))
    HUB_COMMANDS_CHANNEL_ID: Final = int(getenv("HUB_COMMANDS_CHANNEL_ID", ""))
    HUB_RELAY_CHANNEL_ID: Final = int(getenv("HUB_RELAY_CHANNEL_ID", ""))
    HUB_STDOUT_CHANNEL_ID: Final = int(getenv("HUB_STDOUT_CHANNEL_ID", ""))
    
    WOLFRAM_API_KEY: Final = getenv("WOLFRAM_API_KEY", "")
    WOLFRAM_USER_LIMIT_DAY: Final = int(getenv("WOLFRAM_USER_LIMIT_DAY", ""))
    WOLFRAM_GUILD_LIMIT_DAY: Final = int(getenv("WOLFRAM_GUILD_LIMIT_DAY", ""))
        
    SUPPORT_GUILD_ID: Final = int(getenv("SUPPORT_GUILD_ID", ""))
    SUPPORT_ROLE_ID: Final = int(getenv("SUPPORT_ROLE_ID", ""))
    
    ACCEPT_EMOJI_ID: Final = int(getenv("ACCEPT_EMOJI_ID", ""))
    CANCEL_EMOJI_ID: Final = int(getenv("CANCEL_EMOJI_ID", ""))
    INFO_EMOJI_ID: Final = int(getenv("INFO_EMOJI_ID", ""))
    EXIT_EMOJI_ID: Final = int(getenv("EXIT_EMOJI_ID", ""))
    
    OPTION1_EMOJI_ID: Final = int(getenv("OPTION1_EMOJI_ID", ""))
    OPTION2_EMOJI_ID: Final = int(getenv("OPTION2_EMOJI_ID", ""))
    OPTION3_EMOJI_ID: Final = int(getenv("OPTION3_EMOJI_ID", ""))
    OPTION4_EMOJI_ID: Final = int(getenv("OPTION4_EMOJI_ID", ""))
    OPTION5_EMOJI_ID: Final = int(getenv("OPTION5_EMOJI_ID", ""))
    OPTION6_EMOJI_ID: Final = int(getenv("OPTION6_EMOJI_ID", ""))
    OPTION7_EMOJI_ID: Final = int(getenv("OPTION7_EMOJI_ID", ""))
    OPTION8_EMOJI_ID: Final = int(getenv("OPTION8_EMOJI_ID", ""))
    OPTION9_EMOJI_ID: Final = int(getenv("OPTION9_EMOJI_ID", ""))
    
    PAGE_BACK_EMOJI_ID: Final = int(getenv("PAGE_BACK_EMOJI_ID", ""))
    PAGE_NEXT_EMOJI_ID: Final = int(getenv("PAGE_NEXT_EMOJI_ID", ""))
    
    STEP_BACK_EMOJI_ID: Final = int(getenv("STEP_BACK_EMOJI_ID", ""))
    STEP_NEXT_EMOJI_ID: Final = int(getenv("STEP_NEXT_EMOJI_ID", ""))
