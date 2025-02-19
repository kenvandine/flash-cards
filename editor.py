import gi
import json

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

class FlashCardEditor(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flash Card Editor")
        self.set_default_size(1024, 768)

        self.json_data = {}

        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.set_titlebar(header)

        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", self.on_open)
        header.pack_start(open_button)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save)
        header.pack_end(save_button)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)

        self.box.append(self.grid)

        self.term_entry = Gtk.Entry()
        self.grid.attach(Gtk.Label(label="Term:"), 0, 0, 1, 1)
        self.grid.attach(self.term_entry, 1, 0, 1, 1)

        self.definition_entry = Gtk.Entry()
        self.grid.attach(Gtk.Label(label="Definition:"), 0, 1, 1, 1)
        self.grid.attach(self.definition_entry, 1, 1, 1, 1)

        add_button = Gtk.Button(label="Add/Update")
        add_button.connect("clicked", self.on_add_update)
        self.grid.attach(add_button, 0, 2, 2, 1)

        self.text_view = Gtk.TextView(editable=False)
        self.text_view.set_size_request(1024, 0)
        self.box.append(self.text_view)

        self.set_child(self.box)
        self.update_text_view()

    def on_open(self, button):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_modal(True)
        file_dialog.set_title("Open Flash Card File")
        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.json")
        file_filter.set_name("JSON files")
        
        # Set the filter to the dialog
        file_dialog.set_default_filter(file_filter)

        file_dialog.open(self, None, self.on_open_file_chosen)

    def on_open_file_chosen(self, file_dialog, result):
        file = file_dialog.open_finish(result)
        file_path = file.get_path()
        with open(file_path, "r") as f:
            self.json_data = json.load(f)
        self.update_text_view()

    def on_save(self, button):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_modal(True)
        file_dialog.set_title("Save Flash Card File")

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.json")
        file_filter.set_name("JSON files")

        # Set the filter to the dialog
        file_dialog.set_default_filter(file_filter)

        file_dialog.save(self, None, self.on_save_file_chosen)

    def on_save_file_chosen(self, file_dialog, result):
        file = file_dialog.save_finish(result)
        file_path = file.get_path()
        with open(file_path, "w") as f:
            json.dump(self.json_data, f, indent=4)

    def on_add_update(self, button):
        term = self.term_entry.get_text().strip()
        definition = self.definition_entry.get_text().strip()
        if term and definition:
            self.json_data[term] = definition
            self.update_text_view()

    def update_text_view(self):
        buffer = self.text_view.get_buffer()
        buffer.set_text(json.dumps(self.json_data, indent=4))
