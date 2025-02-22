# MIT License

# Copyright (c) 2023 Vlad Krupinski <mrvladus@yandex.ru>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
from gi.repository import GLib
from __main__ import VERSION


class Markup:
    """Class for useful markup functions"""

    @classmethod
    def is_escaped(self, text: str) -> bool:
        if (
            "&amp;" in text
            or "&lt;" in text
            or "&gt;" in text
            or "&#39;" in text
            or "&apos;" in text
        ):
            return True
        else:
            return False

    @classmethod
    def escape(self, text: str) -> str:
        return GLib.markup_escape_text(text)

    @classmethod
    def unescape(self, text: str) -> str:
        new_text = text
        new_text = new_text.replace("&amp;", "&")
        new_text = new_text.replace("&lt;", "<")
        new_text = new_text.replace("&gt;", ">")
        new_text = new_text.replace("&#39;", "'")
        new_text = new_text.replace("&apos;", "'")
        return new_text

    @classmethod
    def is_crosslined(self, text: str) -> bool:
        if text.startswith("<s>") and text.endswith("</s>"):
            return True
        else:
            return False

    @classmethod
    def add_crossline(self, text: str):
        return f"<s>{text}</s>"

    @classmethod
    def rm_crossline(self, text: str):
        return text.replace("<s>", "").replace("</s>", "")

    @classmethod
    def find_url(self, text: str):
        """Convert urls to markup. Make sure to escape text before calling."""
        arr = text.split(" ")
        new_str = []
        for i in arr:
            if i.startswith("http://") or i.startswith("https://"):
                new_str.append(f'<a href="{i}">{i}</a>')
            else:
                new_str.append(i)
        return " ".join(new_str)

    @classmethod
    def remove_url(self, text: str):
        if "<a href=" in text:
            return text.split('"')[1]
        else:
            return text


class UserData:
    """Class for accessing data file with user tasks"""

    data_dir = GLib.get_user_data_dir() + "/list"
    default_data = {
        "version": VERSION,
        "tasks": [],
    }

    # Create data dir and data.json file
    @classmethod
    def init(self):
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        if not os.path.exists(self.data_dir + "/data.json"):
            with open(self.data_dir + "/data.json", "w+") as f:
                json.dump(self.default_data, f)
        self.convert()

    # Load user data from json
    @classmethod
    def get(self):
        if not os.path.exists(self.data_dir + "/data.json"):
            self.init()
        with open(self.data_dir + "/data.json", "r") as f:
            data = json.load(f)
            return data

    # Save user data to json
    @classmethod
    def set(self, data: dict):
        with open(self.data_dir + "/data.json", "w") as f:
            json.dump(data, f)

    # Port tasks from older versions (for updates)
    @classmethod
    def convert(self):
        data = self.get()
        ver = data["version"]
        if ver.startswith("44.4") or ver.startswith("44.3"):
            new_data = self.default_data
            old_tasks = data["todos"]
            for task in old_tasks:
                new_sub_tasks = []
                for sub in old_tasks[task]["sub"]:
                    new_text = Markup.unescape(sub)
                    new_text = Markup.remove_url(new_text)
                    new_sub_tasks.append(
                        {
                            "text": Markup.rm_crossline(new_text),
                            "completed": True if Markup.is_crosslined(sub) else False,
                        }
                    )
                new_data["tasks"].append(
                    {
                        "text": Markup.rm_crossline(task),
                        "sub": new_sub_tasks,
                        "color": old_tasks[task]["color"],
                        "completed": True if Markup.is_crosslined(task) else False,
                    }
                )
            UserData.set(new_data)
