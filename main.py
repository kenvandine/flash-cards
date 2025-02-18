import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw
import random
import os

# Sample dictionary for terms and definitions
flash_cards = {
    "Separation of Powers": "A principle of governance in which the executive, legislative, and judicial branches of government are distinct and separate entities.",
    "Checks and Balances": "A system in which each branch of government has the ability to limit the powers of the other branches to prevent any one branch from becoming too powerful.",
    "Federalism": "A political system in which power is divided between a central government and regional governments (states).",
    "Judicial Review": "The power of the courts to declare laws and executive actions unconstitutional.",
    "Bill of Rights": "The first ten amendments to the United States Constitution, which guarantee fundamental rights and freedoms.",
    "Electoral College": "A body of electors established by the United States Constitution, which formally elects the President and Vice President.",
    "Lobbying": "The practice of influencing public policy and decision-making through direct contact with lawmakers and government officials.",
    "Gerrymandering": "The manipulation of electoral district boundaries for political advantage, often to favor one party over another.",
    "Filibuster": "A tactic used in the United States Senate to delay or block legislative action by extending debate.",
    "Supremacy Clause": "A clause in the United States Constitution (Article VI, Clause 2) that establishes the Constitution, federal laws, and treaties as the supreme law of the land."
}

# Convert the dictionary to a list of tuples for easier navigation
flash_card_list = list(flash_cards.items())
current_index = 0

class FlashCardsApp(Adw.Application):
    def __init__(self):
        super().__init__()
        self.connect("activate", self.on_activate)
        self.term, self.definition = flash_card_list[current_index]

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
        self.is_fullscreen = False

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app, title="Flash Cards")
        self.window.set_default_size(1024, 800)

        # Create HeaderBar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        title_label = Gtk.Label(label="Flash Card App")
        header_bar.set_title_widget(title_label)
        self.window.set_titlebar(header_bar)

        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.on_prev_button_clicked)
        header_bar.pack_start(self.prev_button)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.on_next_button_clicked)
        header_bar.pack_end(self.next_button)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.window.set_child(self.box)

        self.expander_row = Adw.ExpanderRow()
        self.expander_row.add_css_class("term")
        self.expander_row.set_title(f"<b>{self.term}</b>")
        self.expander_row.set_subtitle(f"<b>Tap to flip</b>")
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
            expander_row.set_subtitle("Tap to flip")

    def on_next_button_clicked(self, button):
        self.expander_row.set_expanded(False)
        global current_index
        current_index = (current_index + 1) % len(flash_card_list)
        self.term, self.definition = flash_card_list[current_index]
        self.expander_row.set_title(f"<b>{self.term}</b>")
        self.expander_row.set_subtitle("Tap to flip")

    def on_prev_button_clicked(self, button):
        self.expander_row.set_expanded(False)
        global current_index
        current_index = (current_index - 1) % len(flash_card_list)
        self.term, self.definition = flash_card_list[current_index]
        self.expander_row.set_title(f"<b>{self.term}</b>")
        self.expander_row.set_subtitle("Tap to flip")

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


if __name__ == "__main__":
    app = FlashCardsApp()
    app.run(None)

