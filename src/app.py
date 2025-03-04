import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, GLib
import random
import os
import json
from about import show_about_dialog
from flashcard import FlashCard
from editcard import EditCard
import gettext

locales_dir = os.path.join(os.environ.get("SNAP"), "usr/share/locale")
gettext.bindtextdomain('flash-cards', locales_dir)
gettext.textdomain('flash-cards')
_ = gettext.gettext

class FlashCardsApp(Adw.Application):
    def __init__(self):
        super().__init__()
        self.connect("activate", self.on_activate)
        self.deck_title = ""
        self.data = {}
        self.flash_cards = {}
        self.term, self.definition = "", ""
        self.is_fullscreen = False
        self.history_file = os.path.join(self.get_cache_dir(), "history.json")
        self.history = self.load_history()
        self.edit = False

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
        self.title_label = Gtk.Label(label="Flash Cards")
        header_bar.set_title_widget(self.title_label)
        self.window.set_titlebar(header_bar)

        # Create and connect the file picker button
        open_button = Gtk.Button(label=_("Open Flash Cards File"))
        open_button.connect("clicked", self.on_open_file_clicked)
        open_button.set_visible(len(self.flash_cards) > 0)
        header_bar.pack_start(open_button)

        self.save_button = Gtk.Button(label=_("Save"))
        self.save_button.connect("clicked", self.on_save_file_clicked)
        self.save_button.set_visible(False)
        header_bar.pack_start(self.save_button)

        menu_button = Gtk.MenuButton()
        menu_model = Gio.Menu()
        menu_model.append(_("New"), "app.new")
        menu_model.append(_("Open"), "app.open")
        menu_model.append(_("Edit"), "app.edit")
        menu_model.append(_("About"), "app.about")
        menu_button.set_menu_model(menu_model)
        header_bar.pack_end(menu_button)

        self.next_button = Gtk.Button(label=_("Next"))
        self.next_button.connect("clicked", self.on_next)
        header_bar.pack_end(self.next_button)

        self.prev_button = Gtk.Button(label=_("Previous"))
        self.prev_button.connect("clicked", self.on_prev)
        header_bar.pack_end(self.prev_button)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.window.set_child(self.box)

        self.history_list = Adw.ExpanderRow(title=_("Recent Decks"))
        self.box.append(self.history_list)

        # Wrap recent items in a content box
        self.recent_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.history_list.add_row(self.recent_box)

        self.load_history_list()

        if self.edit:
            self.deck_title_label = Gtk.Entry(text=self.deck_title)
            self.deck_title_label.set_placeholder_text("Deck Title")
            self.deck_title_label.connect("changed", self.on_deck_title_changed)
        else:
            self.deck_title_label = Gtk.Box()
        self.deck_title_label.add_css_class("decktitle")
        self.box.append(self.deck_title_label)

        if self.edit:
            self.card = EditCard()
        else:
            self.card = FlashCard(term=self.term, definition=self.definition)


        self.box.append(self.card)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.button_box.set_visible(self.edit)
        delete_button = Gtk.Button(label=_("Delete"))
        delete_button.connect("clicked", self.on_delete_clicked)
        new_button = Gtk.Button(label=_("New"))
        new_button.connect("clicked", self.new_card)
        self.button_box.append(delete_button)
        self.button_box.append(new_button)
        self.box.append(self.button_box)

        # Connect key press events to navigate between flash cards
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_press)
        self.window.add_controller(key_controller)

        if len(self.history) > 0:
            item = self.history[0]
            title = list(item.keys())[0]
            file_path = item[title]
            self.load_flash_cards(file_path)

        self.window.present()

    def on_deck_title_changed(self, entry):
        self.deck_title = entry.get_text()
        self.title_label.set_label(f"Flash Cards - {self.deck_title}")

    # Add item from model
    def new_card(self, button):
        global current_index
        self.save_card(current_index)
        current_index = len(self.flash_cards) + 1
        self.card.term = ""
        self.card.definition = ""
        self.card.flipped = False
        self.card.update()

    # Delete item from model
    def on_delete_clicked(self, button):
        term = self.card.term_entry.get_text()
        if term in self.flash_cards.keys():
            del self.flash_cards[term]
        self.on_prev(None)

    # Save edited item in model
    def save_card(self, index=None):
        print(f"save_card {index}")
        term = self.card.term_entry.get_text()
        buffer = self.card.definition_view.get_buffer()
        definition = buffer.get_text(buffer.get_start_iter(),
                                     buffer.get_end_iter(),
                                     False)
        if index is None or index > len(self.flash_cards) or len(self.flash_cards) == 0:
            self.flash_cards[term] = definition
        else:
            # Replace key and value at index
            cards_list = list(self.flash_cards.items())
            cards_list[index] = (term, definition)
            self.flash_cards = dict(cards_list)

    def create_actions(self):
        action = Gio.SimpleAction.new("new", None)
        action.connect("activate", self.on_new_file_clicked)
        self.add_action(action)

        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", self.on_open_file_clicked)
        self.add_action(action)

        self.edit_action = Gio.SimpleAction.new_stateful("edit", None, GLib.Variant.new_boolean(False))
        self.edit_action.connect("change-state", self.on_edit_mode)
        self.add_action(self.edit_action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

    def on_edit_mode(self, action, param):
        print("Edit Mode")
        self.edit = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(self.edit))
        term = self.card.term
        definition = self.card.definition
        self.box.remove(self.card)
        self.box.remove(self.deck_title_label)
        if self.edit:
            self.card = EditCard()
            self.save_button.set_visible(True)
            self.deck_title_label = Gtk.Entry(text=self.deck_title)
            self.deck_title_label.set_placeholder_text("Deck Title")
            self.deck_title_label.connect("changed", self.on_deck_title_changed)
            self.deck_title_label.add_css_class("decktitle")
        else:
            self.card = FlashCard(term=self.term, definition=self.definition)
            self.save_button.set_visible(False)
            self.deck_title_label = Gtk.Box()
        self.card.term, self.card.definition = term, definition
        self.card.flipped = False
        self.card.update()
        self.box.insert_child_after(self.deck_title_label, self.history_list)
        self.box.insert_child_after(self.card, self.deck_title_label)
        self.button_box.set_visible(self.edit)

    def on_about(self, action, param):
        win = self.get_active_window()
        show_about_dialog(win)

    def on_next(self, button):
        if self.flash_cards:
            global current_index
            if self.edit:
                # In edit mode, save card on navigation
                if current_index <= len(self.flash_cards):
                    self.save_card(current_index)
                else:
                    self.save_card(None)
            if len(self.flash_cards) > 0:
                current_index = (current_index + 1) % len(list(self.flash_cards.items()))
                self.card.term, self.card.definition = list(self.flash_cards.items())[current_index]
        else:
            self.card.term, self.card.definition = "", ""
        self.card.flipped = False
        self.card.update()

    def on_prev(self, button):
        if self.flash_cards:
            global current_index
            if self.edit:
                # In edit mode, save card on navigation
                if current_index <= len(self.flash_cards):
                    self.save_card(current_index)
                else:
                    self.save_card(None)
            if len(self.flash_cards) > 0:
                current_index = (current_index - 1) % len(list(self.flash_cards.items()))
                self.card.term, self.card.definition = list(self.flash_cards.items())[current_index]
            else:
                self.card.term, self.card.definition = "", ""
            self.card.flipped = False
            self.card.update()

    def on_key_press(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Right:
            self.on_next(None)
        elif keyval == Gdk.KEY_Left:
            self.on_prev(None)
        elif keyval == Gdk.KEY_space:
            if not self.edit:
                self.card.flip(None)
        elif keyval == Gdk.KEY_F11:
            if self.is_fullscreen:
                self.window.unfullscreen()
            else:
                self.window.fullscreen()
            self.is_fullscreen = not self.is_fullscreen
        return True

    def on_new_file_clicked(self, action, param):
        self.edit = True
        self.edit_action.set_state(GLib.Variant.new_boolean(self.edit))
        self.flash_cards = {}
        global current_index
        current_index = 0
        self.box.remove(self.card)
        self.box.remove(self.deck_title_label)
        self.card = EditCard()
        self.deck_title_label = Gtk.Entry(text=self.deck_title)
        self.deck_title_label.set_placeholder_text("Deck Title")
        self.deck_title_label.connect("changed", self.on_deck_title_changed)
        self.save_button.set_visible(True)
        self.card.term, self.card.definition = "", ""
        self.card.flipped = False
        self.card.update()
        self.box.insert_child_after(self.deck_title_label, self.history_list)
        self.box.insert_child_after(self.card, self.deck_title_label)
        self.button_box.set_visible(self.edit)

    def on_open_file_clicked(self, action, param):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_modal(True)
        file_dialog.set_title("Open Flash Card File")
        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.json")
        file_filter.set_name("JSON files")
        
        # Set the filter to the dialog
        file_dialog.set_default_filter(file_filter)

        # Set the initial folder to the Documents directory
        documents_folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_folder:
            file_dialog.set_initial_folder(Gio.File.new_for_path(documents_folder))

        file_dialog.open(self.window, None, self.on_file_chosen)

    def on_file_chosen(self, file_dialog, result):
        file = file_dialog.open_finish(result)
        file_path = file.get_path()
        self.load_flash_cards(file_path)

    def on_save_file_clicked(self, button):
        global current_index
        self.save_card(current_index)
        file_dialog = Gtk.FileDialog()
        file_dialog.set_modal(True)
        file_dialog.set_title("Save Flash Card File")

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.json")
        file_filter.set_name("JSON files")

        # Set the filter to the dialog
        file_dialog.set_default_filter(file_filter)
        filter_list_store = Gio.ListStore.new(Gtk.FileFilter)
        filter_list_store.append(file_filter)

        # Set the filter for the file dialog
        file_dialog.set_filters(filter_list_store)
        file_dialog.set_initial_name("untitled.json")

        # Set the initial folder to the Documents directory
        documents_folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if documents_folder:
            file_dialog.set_initial_folder(Gio.File.new_for_path(documents_folder))

        file_dialog.save(self.window, None, self.on_save_file_chosen)

    def on_save_file_chosen(self, file_dialog, result):
        file = file_dialog.save_finish(result)
        file_path = file.get_path()
        self.add_to_history(self.deck_title, file_path)
        with open(file_path, "w") as f:
            self.data = {}
            self.data[self.deck_title] = self.flash_cards
            json.dump(self.data, f, indent=4)
        self.load_flash_cards(file_path)

    def load_flash_cards(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.data = json.load(file)
                if self.data:
                    self.deck_title = list(self.data.items())[0][0]
                    if self.edit:
                        self.deck_title_label.set_text(self.deck_title)
                    self.title_label.set_label(f"Flash Cards - {self.deck_title}")
                    self.flash_cards = self.data[self.deck_title]
                    self.add_to_history(self.deck_title, file_path)
                    global current_index
                    current_index = 0
                    if len(self.flash_cards) > 0:
                        self.card.term, self.card.definition = list(self.flash_cards.items())[current_index]
                        self.card.flipped = False
                        self.card.update()
        except Exception as e:
            print(f"Failed to load flash cards: {e}")

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                return json.load(file)
        if os.environ.get("SNAP_USER_COMMON"):
            sample_file = os.path.join(os.environ["SNAP_USER_COMMON"], "sample.json")
            return [{"Sample": sample_file}]
        return []

    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.history, file)

    def add_to_history(self, title, file_path):
        if {title: file_path} in self.history:
            self.history.remove({title: file_path})
        self.history.insert(0, {title: file_path})
        self.save_history()
        self.load_history_list()

    def load_history_list(self):
        # Remove all existing rows
        for row in list(self.recent_box):
            self.recent_box.remove(row)

        # Add new rows
        if len(self.history) > 0:
            for item in self.history:
                title = list(item.keys())[0]
                file_path = item[title]
                row = Adw.ActionRow(title=title, subtitle=os.path.basename(file_path), activatable=True)
                # Add a Gtk.GestureClick to handle the click event
                gesture = Gtk.GestureClick()
                gesture.connect("pressed", self.on_recent_selected, title, file_path)
                row.add_controller(gesture)
                self.recent_box.append(row)

    def on_recent_selected(self, gesture, n_press, x, y, title, file_path):
        self.load_flash_cards(file_path)
        if not self.edit:
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

