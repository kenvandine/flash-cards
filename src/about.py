import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio
import os
import gettext

_ = gettext.gettext

def show_about_dialog(parent):
    about_dialog = Gtk.AboutDialog.new()
    about_dialog.set_transient_for(parent)
    about_dialog.set_program_name("Flash Cards")
    about_dialog.set_version("0.1")
    about_dialog.set_comments(_("A Flash Card viewer and editor"))
    about_dialog.set_authors(["Ken VanDine"])
    icon_path = os.path.dirname(os.path.realpath(__file__)) + "/icon.png"
    icon_file = Gio.File.new_for_path(icon_path)
    icon_texture = Gdk.Texture.new_from_file(icon_file)
    about_dialog.set_logo(icon_texture)
    about_dialog.show()

