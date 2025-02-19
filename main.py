import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio
import random
import os
import json

class FlashCardsApp(Adw.Application):
    def __init__(self):
        super().__init__()
        self.connect("activate", self.on_activate)
        self.flash_cards = {}
        self.term, self.definition = "", ""
        self.is_fullscreen = False

        # Set Adwaita dark theme preference using Adw.StyleManager
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        # Apply CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.dirname(os.path.realpath(__file__)) + '/css/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app, title="Flash Cards")
        self.window.set_default_size(1024, 800)

        # Create HeaderBar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        title_label = Gtk.Label(label="Flash Cards")
        header_bar.set_title_widget(title_label)
        self.window.set_titlebar(header_bar)

        # Create and connect the file picker button
        file_picker_button = Gtk.Button(label="Open Flash Cards File")
        file_picker_button.connect("clicked", self.on_open_file_clicked)
        header_bar.pack_start(file_picker_button)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.on_next_button_clicked)
        header_bar.pack_end(self.next_button)

        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.on_prev_button_clicked)
        header_bar.pack_end(self.prev_button)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.window.set_child(self.box)

        self.expander_row = Adw.ExpanderRow()
        self.expander_row.add_css_class("term")
        self.expander_row.set_title(f"<b>Open Flash Card File</b>")
        self.expander_row.set_subtitle(f"")
        self.expander_row.connect("notify::expanded", self.on_expander_toggled)
        self.box.append(self.expander_row)

        # Connect key press events to navigate between flash cards
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_press)
        self.window.add_controller(key_controller)

        self.window.present()

    def on_expander_toggled(self, expander_row, gparam):
        if expander_row.get_expanded():
            expander_row.set_subtitle(f"<b>{self.definition}</b>")
        else:
            expander_row.set_subtitle("Tap to show")

    def on_next_button_clicked(self, button):
        if self.flash_cards:
            self.expander_row.set_expanded(False)
            global current_index
            current_index = (current_index + 1) % len(self.flash_cards)
            self.term, self.definition = list(self.flash_cards.items())[current_index]
            self.expander_row.set_title(f"<b>{self.term}</b>")
            self.expander_row.set_subtitle("Tap to show")

    def on_prev_button_clicked(self, button):
        if self.flash_cards:
            self.expander_row.set_expanded(False)
            global current_index
            current_index = (current_index - 1) % len(self.flash_cards)
            self.term, self.definition = list(self.flash_cards.items())[current_index]
            self.expander_row.set_title(f"<b>{self.term}</b>")
            self.expander_row.set_subtitle("Tap to show")

    def on_key_press(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Right:
            self.on_next_button_clicked(None)
        elif keyval == Gdk.KEY_Left:
            self.on_prev_button_clicked(None)
        elif keyval == Gdk.KEY_space:
            self.expander_row.set_expanded(not self.expander_row.get_expanded())
        elif keyval == Gdk.KEY_F11:
            if self.is_fullscreen:
                self.window.unfullscreen()
            else:
                self.window.fullscreen()
            self.is_fullscreen = not self.is_fullscreen
        return True

    def on_open_file_clicked(self, button):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_modal(True)
        file_dialog.set_title("Open Flash Card File")
        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.json")
        file_filter.set_name("JSON files")
        
        # Set the filter to the dialog
        file_dialog.set_default_filter(file_filter)

        file_dialog.open(self.window, None, self.on_file_chosen)

    def on_file_chosen(self, file_dialog, result):
        file = file_dialog.open_finish(result)
        file_path = file.get_path()
        self.load_flash_cards(file_path)

    def load_flash_cards(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.flash_cards = json.load(file)
                if self.flash_cards:
                    global current_index
                    current_index = 0
                    self.term, self.definition = list(self.flash_cards.items())[current_index]
                    self.expander_row.set_title(f"<b>{self.term}</b>")
                    self.on_expander_toggled(self.expander_row, None)
        except Exception as e:
            print(f"Failed to load flash cards: {e}")


if __name__ == "__main__":
    app = FlashCardsApp()
    app.run(None)

