from pulsectl import Pulse, connect_to_cli
from pynput.keyboard import Listener, Key # i don't want to do this trough xlib. fuck u
import time
import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)


# pulse = Pulse()

class pulseaudiostuff():
    def __init__(self):
        logging.debug("Initing %s", self.__class__.__name__)
        self.pulse = Pulse()
        self.barecmd = connect_to_cli()

        default_sink_name = self.pulse.server_info().default_sink_name
        self.default_sink_info = self.pulse.get_sink_by_name(default_sink_name)

        out_sink_name = "game-out"
        # music + mic
        self.out_sink_module_id = self.pulse.module_load("module-null-sink",
                                                         'sink_name=' + out_sink_name)
        self.out_sink_info = self.pulse.get_sink_by_name(out_sink_name)

        MP_sink_name = "Media-player"
        # that is our main sink. send your media here
        # everything that comes in is being copied to game sink and default sink
        self.MP_sink_module_id = self.pulse.module_load("module-combine-sink",
                                                        'sink_name=' + MP_sink_name +
                                                        ' slaves=' + str(self.out_sink_info.index) +
                                                        ',' + str(self.default_sink_info.index))
        self.MP_sink_info = self.pulse.get_sink_by_name(MP_sink_name)

        # Get stream media -> speakers
        # TODO: this is also gay but it is somehow possible to retreve all inputs for sink. (sink_input_list(sinkIndex))
        for stream in self.pulse.sink_input_list():
            if stream.owner_module == self.MP_sink_module_id:
                if stream.sink == self.default_sink_info.index:
                    self.sound2speakers = stream
                elif stream.sink == self.out_sink_info.index:
                    self.sound2game = stream

        # send mic stream to game sink. (btw rip 20 ms)
        self.loopback_module_id = self.pulse.module_load("module-loopback",
                                                         'sink=' + str(
                                                             self.out_sink_info.index) + ' latency_msec=20 source_dont_move=true sink_dont_move=true')

        # Get stream mic -> game
        # TODO: this is also gay but it is somehow possible to retreve all inputs for sink. (sink_input_list(sinkIndex))
        for stream in self.pulse.sink_input_list():
            if stream.sink == self.out_sink_info.index and stream.owner_module == self.loopback_module_id:
                self.mic2game = stream

        # TODO: combine sink sets volume to earrape because reasons?
        hell = self.sound2speakers.volume
        hell.value_flat = 0.5
        self.pulse.volume_set(self.sound2speakers, hell)
        hell.value_flat = 1.0
        self.pulse.volume_set(self.sound2game, hell)

        # TODO: change names of sinks.
        # https://gitlab.freedesktop.org/pulseaudio/pulseaudio/-/issues/615
        # self.barecmd.write(
        #     'update-sink-proplist ' + str(self.out_sink_info.index) + ' device.description="Game media player out"')
        # self.barecmd.write(
        #     'update-sink-proplist ' + str(self.MP_sink_info.index) + ' device.description="Game media player sink"')

        self.pulse.sink_default_set(self.default_sink_info)

        logging.debug("%s class loaded", self.__class__.__name__)
        logging.info("out sink module id: %d", self.out_sink_module_id)
        logging.info("MP sink module id: %d", self.MP_sink_module_id)
        logging.info("loopback module id: %d", self.loopback_module_id)

    def __del__(self):
        self.pulse.module_unload(self.loopback_module_id)
        self.pulse.module_unload(self.out_sink_module_id)
        self.pulse.module_unload(self.MP_sink_module_id)
        logging.debug("%s class unloaded", self.__class__.__name__)

    def printstuff(self):
        print('csgo launch options: "pacmd set-default-source ' + self.out_sink_info.name + '.monitor"')


def on_release2(key):
    print("on_release2 Key pressed " + str(key))
    pass


def on_release(key):
    print("on_release Key released " + str(key))
    pass


if __name__ == '__main__':
    with Listener(on_release=on_release) as listener:
        time.sleep(5)
        listener.stop()
        # listener.join()
        print("hello")
        listener = Listener(on_release=on_release2)
        listener.run()
        print("1")
        listener.join()
        print("2")
