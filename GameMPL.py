#!/usr/bin/python3
# Game media player linux / GameMPL
# Version 0.2
# (c) 2020 acuifex GameMPL@acuifex.ru

import PulseAudio
import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk


class Window:
    def __init__(self):
        self.PA_stuff = PulseAudio.pulseaudiostuff()
        logging.debug("Initing %s", self.__class__.__name__)
        gladeFile = "Window.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

        self.windowObj = self.builder.get_object("Window")
        self.windowObj.show()
        gtk.main()

    def onClose(self, widget, event):
        logging.debug("Unloading %s", self.__class__.__name__)
        del self.PA_stuff
        gtk.main_quit()

    def onFormatValue(self, widget, value):
        return "{:.3f}%".format(value * 100)

    def onSound2gameChangeValue(self, widget):
        stream = self.PA_stuff.sound2game.volume # TODO: probably should create new volume values.
        stream.value_flat = widget.get_value()
        self.PA_stuff.pulse.volume_set(self.PA_stuff.sound2game, stream)

    def onSound2speakersChangeValue(self, widget):
        stream = self.PA_stuff.sound2speakers.volume
        stream.value_flat = widget.get_value()
        self.PA_stuff.pulse.volume_set(self.PA_stuff.sound2speakers, stream)

    def onMic2gameChangeValue(self, widget):
        stream = self.PA_stuff.mic2game.volume
        stream.value_flat = widget.get_value()
        self.PA_stuff.pulse.volume_set(self.PA_stuff.mic2game, stream)

    def onSound2gameMute(self, widget):
        self.PA_stuff.pulse.mute(self.PA_stuff.sound2game, widget.get_active())

    def onSound2speakersMute(self, widget):
        self.PA_stuff.pulse.mute(self.PA_stuff.sound2speakers, widget.get_active())

    def onMic2gameMute(self, widget):
        self.PA_stuff.pulse.mute(self.PA_stuff.mic2game, widget.get_active())


if __name__ == '__main__':
    w = Window()
