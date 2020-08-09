#!/usr/bin/python3
# Game media player linux / GameMPL
# Version 0.1
# (c) 2020 acuifex GameMPL@acuifex.ru

from pulsectl import Pulse, connect_to_cli
# import pulsectl
from pynput.keyboard import Listener, Key
import time
import Xlib
import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
# pulse = Pulse()

class pulseaudiostuff():
    def __init__(self):
        logging.debug("started init")
        self.pulse = Pulse()
        self.barecmd = connect_to_cli()

        default_sink_name = self.pulse.server_info().default_sink_name
        self.default_sink_info = self.pulse.get_sink_by_name(default_sink_name)

        out_sink_name = "game-out"
        # music + mic
        self.out_sink_module_id = self.pulse.module_load("module-null-sink",
                                                         'sink_name=' + out_sink_name)
        self.out_sink_info = self.pulse.get_sink_by_name(out_sink_name)
        # that's very gay but what can you do?
        self.barecmd.write('update-sink-proplist '+str(self.out_sink_info.index)+' device.description="Game media player out"')

        MP_sink_name = "Media-player"
        # that is our main sink. send your media here
        # everything that comes in is being copied to game sink and default sink
        self.MP_sink_module_id = self.pulse.module_load("module-combine-sink",
                                                   'sink_name=' + MP_sink_name +
                                                   ' slaves=' + str(self.out_sink_info.index) +
                                                   ',' + str(self.default_sink_info.index))
        # Get stream media -> speakers
        # TODO: this is also gay but it is somehow possible to retreve all inputs for sink. (sink_input_list(sinkIndex))
        for stream in self.pulse.sink_input_list():
            if stream.sink == self.default_sink_info.index and stream.owner_module == self.MP_sink_module_id:
                self.media2speakers = stream

        # send mic stream to game sink. (btw rip 20 ms)
        self.loopback_module_id = self.pulse.module_load("module-loopback",
                                       'sink=' + str(self.out_sink_info.index) + ' latency_msec=20 source_dont_move=true sink_dont_move=true')

        # Get stream mic -> game
        # TODO: this is also gay but it is somehow possible to retreve all inputs for sink. (sink_input_list(sinkIndex))
        for stream in self.pulse.sink_input_list():
            if stream.sink == self.out_sink_info.index and stream.owner_module == self.loopback_module_id:
                self.mic2game = stream

        self.pulse.sink_default_set(self.default_sink_info)

        logging.debug("%s class loaded", self.__class__.__name__)
        logging.info("out sink module id: %d", self.out_sink_module_id)
        logging.info("MP sink module id: %d", self.MP_sink_module_id)
        logging.info("loopback module id: %d", self.loopback_module_id)

    def __del__(self):
        self.pulse.module_unload(self.out_sink_module_id)
        self.pulse.module_unload(self.MP_sink_module_id)
        self.pulse.module_unload(self.loopback_module_id)
        logging.debug("%s class unloaded", self.__class__.__name__)

    def printstuff(self):
        print('csgo launch options: "pacmd set-default-source ' + self.out_sink_info.name + '.monitor"')


def main():
    # test = pulse.module_load("module-virtual-sink", 'sink_name=test')
    test = pulseaudiostuff()
    x = None
    while (x != "q"):
        print("press q to exit")
        x = input()
        if x[0] == "v":
            volume = float(x[1:])
            stream = test.media2speakers.volume
            stream.value_flat = volume
            test.pulse.volume_set(test.media2speakers, stream)
        if x[0] == "m":
            volume = float(x[1:])
            stream = test.mic2game.volume
            stream.value_flat = volume
            test.pulse.volume_set(test.mic2game, stream)

    del test

def on_press(key):
    print("Key pressed " + str(key))
    pass


def on_release(key):
    print("Key released " + str(key))
    pass

if __name__ == '__main__':
    # with Listener(on_press=on_press, on_release=on_release) as listener:
    #     listener.join()
    main()
