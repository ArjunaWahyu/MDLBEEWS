import socketio
import threading

class SocketIOClient(threading.Thread):
    def __init__(self, update_callback):
        threading.Thread.__init__(self)
        self.update_callback = update_callback
        self.sio = socketio.Client()
        self.x_data = []
        self.y_data = []
        # create sets to save station and channel
        self.stations = set()

        @self.sio.event
        def connect():
            print('connection established')

        @self.sio.event
        def disconnect():
            print('disconnected from server')

        @self.sio.on('waves-data')
        def on_message(data):
            print(f'{data["station"]}-{data["channel"]}')
            self.stations.add(f'{data["station"]}-{data["channel"]}')
            if (f'{data["station"]}-{data["channel"]}' == 'PB19-HLE'):
                len_x = len(self.x_data)
                len_new_x = len(data['data'])
                x = list(range(len_x, len_x + len_new_x))
                y = data['data']
                self.x_data += x
                self.y_data += y
                print(f'x: {len(self.x_data)}, y: {len(self.y_data)}')
                self.update_callback(self.x_data, self.y_data)
                # sort stations and keep it set
                self.stations = set(sorted(self.stations))
                print(f'stations: {self.stations}')
                # print len station
                print(f'len stations: {len(self.stations)}')

    def run(self):
        self.sio.connect('http://localhost:3333')
        self.sio.wait()
