import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio
import random
import os
import json
from about import show_about_dialog
from editor import FlashCardEditor

class FlashCardsApp(Adw.Application):
    def __init__(self):
        super().__init__()
        self.connect("activate", self.on_activate)
        self.flash_cards = {}
        self.term, self.definition = "", ""
        self.is_fullscreen = False
        self.history_file = os.path.join(self.get_cache_dir(), "history.json")
        self.history = self.load_history()

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

        # Create actions for menu items
        self.create_actions()

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

        menu_button = Gtk.MenuButton()
        menu_model = Gio.Menu()
        menu_model.append("Flash Card Editor", "app.editor")
        menu_model.append("About", "app.about")
        menu_button.set_menu_model(menu_model)
        header_bar.pack_end(menu_button)

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

        self.history_list = Adw.ExpanderRow(title="Recent Decks")
        self.box.append(self.history_list)

        # Wrap recent items in a content box
        self.recent_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.history_list.add_row(self.recent_box)

        self.load_history_list()

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

        if len(self.history) > 0:
            self.load_flash_cards(self.history[0])

        self.window.present()

    def create_actions(self):
        action = Gio.SimpleAction.new("editor", None)
        action.connect("activate", self.on_editor)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

    def on_editor(self, action, param):
        print("Editor Opened")
        editor = FlashCardEditor()
        editor.show()

    def on_about(self, action, param):
        win = self.get_active_window()
        show_about_dialog(win)

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
        self.add_to_history(file_path)
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

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                return json.load(file)
        if os.environ.get("SNAP"):
            sample_file = os.path.join(os.environ["SNAP"], "sample.json")
            return [sample_file]
        return []

    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.history, file)

    def add_to_history(self, file_path):
        if file_path in self.history:
            self.history.remove(file_path)
        self.history.insert(0, file_path)
        self.save_history()
        self.load_history_list()

    def load_history_list(self):
        # Remove all existing rows
        for row in list(self.recent_box):
            self.recent_box.remove(row)

        # Add new rows
        if len(self.history) > 0:
            for file_path in self.history:
                row = Adw.ActionRow(title=os.path.basename(file_path), activatable=True)
                # Add a Gtk.GestureClick to handle the click event
                gesture = Gtk.GestureClick()
                gesture.connect("pressed", self.on_recent_selected, file_path)
                row.add_controller(gesture)
                self.recent_box.append(row)

    def on_recent_selected(self, gesture, n_press, x, y, file_path):
        self.load_flash_cards(file_path)
        self.history_list.set_expanded(False)


    def get_cache_dir(self):
        # Get XDG_CACHE_HOME or fallback to ~/.cache
        cache_dir = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        app_cache_dir = os.path.join(cache_dir, 'flash-cards')
        if not os.path.exists(app_cache_dir):
            os.makedirs(app_cache_dir)
        return app_cache_dir

if __name__ == "__main__":
    app = FlashCardsApp()
    app.run(None)

