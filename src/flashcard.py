import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Pango

class FlashCard(Adw.Bin):
    def __init__(self, term="", definition=""):
        super().__init__()
        self.term = term
        self.definition = definition
        self.flipped = False
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.flip)
        box.add_controller(gesture)

        self.term_label = Gtk.Label(label=self.term)
        self.term_label.add_css_class("term")
        box.append(self.term_label)

        self.front_revealer = Gtk.Revealer()
        self.front_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.front_revealer.set_transition_duration(2000)

        self.back_revealer = Gtk.Revealer()
        self.back_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.back_revealer.set_transition_duration(2000)

        self.front_label = Gtk.Label(label="Tap to Show")
        self.front_label.add_css_class("definition")
        self.back_label = Gtk.Label(label=self.definition)
        self.back_label.add_css_class("definition")
        self.back_label.set_wrap(True)
        self.back_label.set_wrap_mode(Pango.WrapMode.WORD)
        self.back_label.set_halign(Gtk.Align.CENTER)
        self.front_revealer.set_child(self.front_label)
        self.back_revealer.set_child(self.back_label)
        self.front_revealer.set_reveal_child(not self.flipped)
        box.append(self.back_revealer)
        box.append(self.front_revealer)

        flip_button = Gtk.Button(label="Flip")
        flip_button.connect("clicked", self.flip)
        box.append(flip_button)
        self.set_child(box)

    def flip(self, button, action=None, param=None, foo=None):
        self.flipped = not self.flipped
        self.back_revealer.set_reveal_child(self.flipped)
        self.front_revealer.set_reveal_child(not self.flipped)

    def update(self):
        print("FlashCard: update")
        # Ensure the definition is hidden first
        self.back_revealer.set_transition_duration(0)
        self.back_revealer.set_reveal_child(self.flipped)
        self.front_revealer.set_reveal_child(not self.flipped)
        self.term_label.set_label(f"{self.term}")
        self.back_label.set_label(f"{self.definition}")
        self.back_revealer.set_transition_duration(2000)
