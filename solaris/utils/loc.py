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

import os

from pygount import SourceAnalysis

from solaris.utils import ROOT_DIR


class CodeCounter:
    def __init__(self):
        self.code = 0
        self.docs = 0
        self.empty = 0

    def count(self):
        for subdir, _, files in os.walk(ROOT_DIR / "solaris"):
            for file in (f for f in files if f.endswith(".py")):
                analysis = SourceAnalysis.from_file(f"{subdir}/{file}", "pygount", encoding="utf=8")
                self.code += analysis.code_count
                self.docs += analysis.documentation_count
                self.empty += analysis.empty_count