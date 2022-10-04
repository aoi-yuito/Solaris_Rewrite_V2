# Blue Brain - A Discord bot designed to make your server a safer and better place.
# Copyright (C) 2020  Sarker Istiyak Mahmud

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

# Sarker Istiyak Mahmud
# kiyotaka.ayanokouji.ehou@gmail.com

from pathlib import Path

from toml import loads

from solaris.config import Config

# Dependant on above imports.
from solaris.bot import Bot

__version__ = loads(open(Path(__name__).resolve().parents[0] / "pyproject.toml").read())["tool"]["poetry"]["version"]
