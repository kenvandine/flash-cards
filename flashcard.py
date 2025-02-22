import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio

class FlashCard(Adw.ExpanderRow):
    def __init__(self):
        super().__init__()
        self.term = ""
        self.definition = ""
        self.add_css_class("term")
        self.set_title(f"<b>Open Flash Card File</b>")
        self.set_subtitle(f"")
        self.connect("notify::expanded", self.on_expander_toggled)

    def update(self):
        print("FlashCard: update")
        self.set_title(f"<b>{self.term}</b>")
        self.set_subtitle("Tap to show")

    def on_expander_toggled(self, card, gparam):
        if card.get_expanded():
            card.set_subtitle(f"<b>{self.definition}</b>")
        else:
            card.set_subtitle("Tap to show")
