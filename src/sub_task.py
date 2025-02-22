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

from gi.repository import Gtk
from .utils import UserData, Markup


@Gtk.Template(resource_path="/io/github/mrvladus/List/sub_task.ui")
class SubTask(Gtk.Box):
    __gtype_name__ = "SubTask"

    sub_task_main_box = Gtk.Template.Child()
    sub_task_text = Gtk.Template.Child()
    sub_task_delete_btn = Gtk.Template.Child()
    sub_task_completed_btn = Gtk.Template.Child()
    sub_task_edit_btn = Gtk.Template.Child()
    sub_task_edit_box = Gtk.Template.Child()
    sub_task_edit_entry = Gtk.Template.Child()
    sub_task_move_up_btn = Gtk.Template.Child()
    sub_task_move_down_btn = Gtk.Template.Child()
    sub_task_cancel_edit_btn = Gtk.Template.Child()

    def __init__(self, task: dict, parent):
        super().__init__()
        print("Add sub-task: ", task["text"])
        self.parent = parent
        self.task = task
        # Escape text and find URL's'
        self.text = Markup.escape(self.task["text"])
        self.text = Markup.find_url(self.text)
        # Check if sub-task completed and toggle checkbox
        if self.task["completed"]:
            self.sub_task_completed_btn.props.active = True
        # Set text
        self.sub_task_text.props.label = self.text
        self.update_move_buttons()

    def toggle_edit_box(self):
        self.sub_task_edit_box.props.visible = not self.sub_task_edit_box.props.visible
        self.sub_task_main_box.props.visible = not self.sub_task_main_box.props.visible

    def update_sub_task(self, new_sub_task):
        new_data = UserData.get()
        for task in new_data["tasks"]:
            if task["text"] == self.parent.task["text"]:
                for i, sub in enumerate(task["sub"]):
                    if sub["text"] == self.task["text"]:
                        task["sub"][i] = new_sub_task
                        UserData.set(new_data)
                        # Update parent data
                        self.parent.task["sub"] = task["sub"]
                        return

    def update_move_buttons(self):
        data = UserData.get()
        idx = self.parent.task["sub"].index(self.task)
        length = len(self.parent.task["sub"])
        self.sub_task_move_up_btn.props.sensitive = False if idx == 0 else True
        self.sub_task_move_down_btn.props.sensitive = (
            False if idx == length - 1 else True
        )

    @Gtk.Template.Callback()
    def on_completed_btn_toggled(self, btn):
        if btn.props.active:
            self.task = {"text": self.task["text"], "completed": True}
            self.update_sub_task(self.task)
            self.text = Markup.add_crossline(self.text)
            self.parent.update_statusbar()
        else:
            self.task = {"text": self.task["text"], "completed": False}
            self.update_sub_task(self.task)
            self.text = Markup.rm_crossline(self.text)
            self.parent.update_statusbar()
        self.sub_task_text.props.label = self.text

    @Gtk.Template.Callback()
    def on_sub_task_delete_btn_clicked(self, *args):
        # Remove sub-task data
        new_data = UserData.get()
        for task in new_data["tasks"]:
            if task["text"] == self.parent.task["text"]:
                for sub in task["sub"]:
                    if sub["text"] == self.task["text"]:
                        task["sub"].remove(sub)
                        UserData.set(new_data)
                        # Update parent data
                        self.parent.task["sub"] = task["sub"]
                        self.parent.update_statusbar()
                        break
                break
        # Remove sub-task widget
        self.parent.sub_tasks.remove(self)

    @Gtk.Template.Callback()
    def on_sub_task_edit_btn_clicked(self, *args):
        self.toggle_edit_box()
        # Set entry text and select it
        self.sub_task_edit_entry.get_buffer().props.text = self.task["text"]
        self.sub_task_edit_entry.select_region(0, len(self.task["text"]))
        self.sub_task_edit_entry.grab_focus()

    @Gtk.Template.Callback()
    def on_sub_task_cancel_edit_btn_clicked(self, _):
        self.toggle_edit_box()

    @Gtk.Template.Callback()
    def on_sub_task_edit(self, entry):
        old_text = self.task["text"]
        new_text = entry.get_buffer().props.text
        # Return if text the same or empty
        if new_text == old_text or new_text == "":
            return
        # Return if sub-task exists
        new_data = UserData.get()
        for task in new_data["tasks"]:
            if task["text"] == self.parent.task["text"]:
                # Return if sub-task exists
                for sub in task["sub"]:
                    if sub["text"] == new_text:
                        return
                # Set new data
                print(f"Change sub-task: '{old_text}' to '{new_text}'")
                self.task = {"text": new_text, "completed": False}
                for i, sub in enumerate(task["sub"]):
                    if sub["text"] == old_text:
                        task["sub"][i] = self.task
                        UserData.set(new_data)
                        # Update parent data
                        self.parent.task["sub"] = task["sub"]
                        self.parent.update_statusbar()
                        break
                break
        # Escape text and find URL's'
        self.text = Markup.escape(self.task["text"])
        self.text = Markup.find_url(self.text)
        # Check if text crosslined and toggle checkbox
        self.sub_task_completed_btn.props.active = False
        # Set text
        self.sub_task_text.props.label = self.text
        self.toggle_edit_box()

    @Gtk.Template.Callback()
    def on_sub_task_move_up_btn_clicked(self, btn):
        if self.parent.task["sub"].index(self.task) == 0:
            return
        print(f"""Move task "{self.task['text']}" up""")
        # Move widget
        self.parent.sub_tasks.reorder_child_after(self.get_prev_sibling(), self)
        # Update data
        new_data = UserData.get()
        task_idx = new_data["tasks"].index(self.parent.task)
        sub_idx = new_data["tasks"][task_idx]["sub"].index(self.task)
        (
            new_data["tasks"][task_idx]["sub"][sub_idx - 1],
            new_data["tasks"][task_idx]["sub"][sub_idx],
        ) = (
            new_data["tasks"][task_idx]["sub"][sub_idx],
            new_data["tasks"][task_idx]["sub"][sub_idx - 1],
        )
        UserData.set(new_data)
        # Update parent task
        self.parent.task["sub"] = new_data["tasks"][task_idx]["sub"]
        # Update buttons
        self.update_move_buttons()
        self.get_next_sibling().update_move_buttons()

    @Gtk.Template.Callback()
    def on_sub_task_move_down_btn_clicked(self, btn):
        if self.parent.task["sub"].index(self.task) + 1 == len(self.parent.task["sub"]):
            return
        print(f"""Move task "{self.task['text']}" down""")
        # Move widget
        self.parent.sub_tasks.reorder_child_after(self, self.get_next_sibling())
        # Update data
        new_data = UserData.get()
        task_idx = new_data["tasks"].index(self.parent.task)
        sub_idx = new_data["tasks"][task_idx]["sub"].index(self.task)
        (
            new_data["tasks"][task_idx]["sub"][sub_idx + 1],
            new_data["tasks"][task_idx]["sub"][sub_idx],
        ) = (
            new_data["tasks"][task_idx]["sub"][sub_idx],
            new_data["tasks"][task_idx]["sub"][sub_idx + 1],
        )
        UserData.set(new_data)
        # Update parent task
        self.parent.task["sub"] = new_data["tasks"][task_idx]["sub"]
        # Update buttons
        self.update_move_buttons()
        self.get_prev_sibling().update_move_buttons()
