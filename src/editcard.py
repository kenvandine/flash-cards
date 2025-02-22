import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio

class EditCard(Adw.Bin):
    def __init__(self):
        super().__init__()
        self.term = "Term"
        self.definition = "Definition"
        self.add_css_class("editterm")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        term_label = Gtk.Label(label="Term")
        term_label.set_halign(Gtk.Align.START)
        definition_label = Gtk.Label(label="Definition")
        definition_label.set_halign(Gtk.Align.START)
        self.term_entry = Gtk.Entry(text=self.term)
        self.term_entry.add_css_class("editterm")

        # Create a Gtk.TextView and set properties for wrapping
        self.definition_view = Gtk.TextView()
        self.definition_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.definition_view.set_vexpand(True)
        self.definition_view.add_css_class("editdefinition")

        box.append(term_label)
        box.append(self.term_entry)
        box.append(definition_label)
        box.append(self.definition_view)
        self.set_child(box)

    def update(self):
        print("EditCard: update")
        self.term_entry.set_text(f"{self.term}")
        self.definition_view.get_buffer().set_text(f"{self.definition}")
