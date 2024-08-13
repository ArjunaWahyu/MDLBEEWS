import sys
import socketio
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
import time
import random
import obspy
import numpy as np

class SocketIOClient(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()

        @self.sio.event
        def connect():
            print('Connection established')

        @self.sio.event
        def disconnect():
            print('Disconnected from server')

        @self.sio.on('waves-data')
        def on_message(data):
            # self.data_received.emit(data)
            trace = self.interpolate(data)
            data['data'] = trace.data
            data['sampling_rate'] = trace.stats.sampling_rate
            data['delta'] = trace.stats.delta
            data['npts'] = trace.stats.npts
            data['calib'] = trace.stats.calib
            data['data_quality'] = trace.stats.dataquality
            data['num_samples'] = trace.stats.numsamples
            data['sample_cnt'] = trace.stats.samplecnt
            data['sample_type'] = trace.stats.sampletype
            self.data_received.emit(data)

    def interpolate(self, data):
        trace = obspy.Trace(np.array(data['data']))
        trace.stats.network = data['network']
        trace.stats.station = data['station']
        trace.stats.location = data['location']
        trace.stats.channel = data['channel']
        trace.stats.starttime = obspy.UTCDateTime(data['start_time'])
        trace.stats.sampling_rate = data['sampling_rate']
        trace.stats.delta = data['delta']
        trace.stats.npts = data['npts']
        trace.stats.calib = data['calib']
        trace.stats.dataquality = data['data_quality']
        trace.stats.numsamples = data['num_samples']
        trace.stats.samplecnt = data['sample_cnt']
        trace.stats.sampletype = data['sample_type']

        # interpolate to 20 Hz
        trace.interpolate(sampling_rate=20)

        return trace

    def run(self):
        self.sio.connect('http://localhost:3333')
        self.sio.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seismic Wave Dashboard")
        self.resize(800, 600)
        self.data = {}
        self.socketIOClient = SocketIOClient()
        self.socketIOClient.data_received.connect(self.update_data)
        self.socketIOClient.start()
        self.count = 0

        # Setup the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add a scroll area to handle multiple plots
        self.scroll_area = QScrollArea(self.central_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.plot_data = {}
        self.plot_widgets = {}

    def update_data(self, data):
        key = f"{data['station']}-{data['channel']}"
        if key not in self.data:
            # if self.count <= 100 and data['sampling_rate'] >= 10 and data['channel'].endswith('Z'):
            if data['sampling_rate'] >= 10 and data['channel'].endswith('Z'):
                self.add_data(data)
                self.count += 1
                print('Count:', self.count)
        else:
            # if data['start_time'] > self.data[key]['end_time'] + self.data[key]['delta']*2:
            if data['start_time'] - self.data[key]['end_time'] > data['delta']*2:
                gap = data['start_time'] - self.data[key]['end_time']
                print(f"[{key}]\tGap: {gap}")

                # If the gap is too large, delete plot
                if gap > 20:
                    self.delete_plot(data)
                    return

                # Calculate the number of missing samples
                missing_samples = int(gap * self.data[key]['sampling_rate'])
                # print(f'Missing samples: {missing_samples}\t time :{gap}')

                # average the data
                avg = sum(self.data[key]['data']) / len(self.data[key]['data'])

                # Fill the missing samples with zeros
                # self.data[key]['data'] += [0] * missing_samples
                self.data[key]['data'] += [avg] * missing_samples

                # # Update the end time of the existing data
                # self.data[key]['end_time'] = data['start_time']
            
            # Append the new data to the existing data
            self.data[key]['data'] += list(data['data'])
            self.data[key]['end_time'] = data['end_time']

            # if data length is greater than 1 minute, remove earlier 5 minutes data
            if len(self.data[key]['data'])/self.data[key]['sampling_rate'] > 360:
                self.data[key]['data'] = self.data[key]['data'][int(60*self.data[key]['sampling_rate']):]
                self.data[key]['start_time'] = self.data[key]['start_time'] + 60
                print(f"Cutting data: {key}")

            # update x-axis
            self.data[key]['x'] = [self.data[key]['start_time'] + i*self.data[key]['delta'] for i in range(len(self.data[key]['data']))]
            self.data[key]['x'] = list(range(-len(self.data[key]['data']), 0, 1))
            # Update plot
            self.plot_update(data)

    def add_data(self, data):
        key = f"{data['station']}-{data['channel']}"
        # x = [data['start_time'] + i*data['delta'] for i in range(len(data['data']))]
        x = list(range(-len(data['data']), 0, 1))
        self.data[key] = {
            'network': data['network'],
            'station': data['station'],
            'location': data['location'],
            'channel': data['channel'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'sampling_rate': data['sampling_rate'],
            'delta': data['delta'],
            'npts': data['npts'],
            'calib': data['calib'],
            'data_quality': data['data_quality'],
            'num_samples': data['num_samples'],
            'sample_cnt': data['sample_cnt'],
            'sample_type': data['sample_type'],
            'data_provider_time': data['data_provider_time'],
            'data': list(data['data']),
            'x': x
        }
        self.add_plot(data)
        # time.sleep(0.01)

    def add_plot(self, data):
        key = f"{data['station']}-{data['channel']}"
        plot = pg.PlotWidget()
        plot.setTitle(f"{data['station']} - {data['channel']} - {data['sampling_rate']}Hz")
        plot.setLabel('left', 'Amplitude')
        # plot.setLabel('bottom', 'Time')
        plot.showGrid(x=True, y=True)
        # create x-axis with start time, len and delta
        # plot_data = pg.PlotDataItem(data=self.data[key]['data'])
        plot_data = pg.PlotDataItem(x=self.data[key]['x'], y=self.data[key]['data'])
        random_number = random.randint(0, 255)
        color = pg.intColor(random_number)
        plot_data.setPen(color)
        plot.addItem(plot_data)
        plot.setXRange(-300*data['sampling_rate'], 0)
        self.plot_data[key] = plot_data

        # Create a QWidget container for the plot
        plot_container = QWidget()
        plot_layout = QVBoxLayout()
        plot_container.setLayout(plot_layout)
        plot_layout.addWidget(plot)
        self.plot_widgets[key] = plot_container

        self.scroll_layout.addWidget(plot_container)

    def plot_update(self, data):
        key = f"{data['station']}-{data['channel']}"
        if key in self.plot_data:
            # self.plot_data[key].setData(self.data[key]['data'])
            self.plot_data[key].setData(x=self.data[key]['x'], y=self.data[key]['data'])
            # set range y-axis with min and max value
            max_val = max(self.data[key]['data'])
            min_val = min(self.data[key]['data'])
            # diff = max_val - min_val
            # self.plot_data[key].getViewBox().setYRange(min_val-diff, max_val+diff, padding=0)
            self.plot_data[key].getViewBox().setYRange(min_val, max_val, padding=0)

    def delete_plot(self, data):
        key = f"{data['station']}-{data['channel']}"
        if key in self.plot_widgets:
            self.scroll_layout.removeWidget(self.plot_widgets[key])
            self.plot_widgets[key].deleteLater()
            del self.plot_widgets[key]
            del self.plot_data[key]
            # del self.data[key]
            self.data.pop(key)
            # Decrement the count
            self.count -= 1
            print(f"Deleted plot: {key}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())


# import sys
# import socketio
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea
# from PyQt5.QtCore import QThread, pyqtSignal
# from vispy import app, scene
# import numpy as np

# class SocketIOClient(QThread):
#     data_received = pyqtSignal(dict)

#     def __init__(self):
#         super().__init__()
#         self.sio = socketio.Client()

#         @self.sio.event
#         def connect():
#             print('Connection established')

#         @self.sio.event
#         def disconnect():
#             print('Disconnected from server')

#         @self.sio.on('waves-data')
#         def on_message(data):
#             self.data_received.emit(data)

#     def run(self):
#         self.sio.connect('http://localhost:3333')
#         self.sio.wait()

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Seismic Wave Dashboard")
#         self.resize(800, 600)
#         self.data = {}
#         self.socketIOClient = SocketIOClient()
#         self.socketIOClient.data_received.connect(self.update_data)
#         self.socketIOClient.start()
#         self.count = 0

#         # Setup the main widget and layout
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout = QVBoxLayout(self.central_widget)
        
#         # Add a scroll area to handle multiple plots
#         self.scroll_area = QScrollArea(self.central_widget)
#         self.scroll_area.setWidgetResizable(True)
#         self.layout.addWidget(self.scroll_area)
        
#         self.scroll_widget = QWidget()
#         self.scroll_layout = QVBoxLayout(self.scroll_widget)
#         self.scroll_area.setWidget(self.scroll_widget)
        
#         self.plot_data = {}
#         self.plot_widgets = {}

#     def update_data(self, data):
#         key = f"{data['station']}-{data['channel']}"
#         if key not in self.data:
#             if self.count <= 20:
#                 self.add_data(data)
#                 self.count += 1
#         else:
#             if data['start_time'] > self.data[key]['end_time'] + self.data[key]['delta']:
#                 gap = data['start_time'] - self.data[key]['end_time']

#                 # If the gap is too large, delete plot
#                 if gap > 30:
#                     self.delete_plot(data)
#                     return

#                 # Calculate the number of missing samples
#                 missing_samples = int(gap * self.data[key]['sampling_rate'])
#                 print(f'Missing samples: {missing_samples}\t time :{gap}')

#                 # Fill the missing samples with zeros
#                 self.data[key]['data'] += [0] * missing_samples

#                 # Update the end time of the existing data
#                 self.data[key]['end_time'] = data['start_time']
            
#             # Append the new data to the existing data
#             self.data[key]['data'] += list(data['data'])
#             self.data[key]['end_time'] = data['end_time']

#         # Update plot
#         self.plot_update(data)

#     def add_data(self, data):
#         key = f"{data['station']}-{data['channel']}"
#         self.data[key] = {
#             'network': data['network'],
#             'station': data['station'],
#             'location': data['location'],
#             'channel': data['channel'],
#             'start_time': data['start_time'],
#             'end_time': data['end_time'],
#             'sampling_rate': data['sampling_rate'],
#             'delta': data['delta'],
#             'npts': data['npts'],
#             'calib': data['calib'],
#             'data_quality': data['data_quality'],
#             'num_samples': data['num_samples'],
#             'sample_cnt': data['sample_cnt'],
#             'sample_type': data['sample_type'],
#             'data_provider_time': data['data_provider_time'],
#             'data': list(data['data'])
#         }
#         self.add_plot(data)

#     def add_plot(self, data):
#         key = f"{data['station']}-{data['channel']}"

#         # Create a VisPy canvas
#         canvas = scene.SceneCanvas(keys='interactive', show=True)
#         view = canvas.central_widget.add_view()
        
#         # Set up a grid in the view
#         grid = scene.visuals.GridLines(color='gray')
#         view.add(grid)
        
#         # Prepare the data
#         plot_data_array = np.array(self.data[key]['data'])
#         if len(plot_data_array.shape) == 1:
#             plot_data_array = np.column_stack((np.arange(len(plot_data_array)), plot_data_array))

#         # Add a plot to the view
#         plot_data = scene.visuals.Line(pos=plot_data_array, parent=view.scene)
#         view.camera = 'panzoom'

#         # Store the plot
#         self.plot_data[key] = plot_data

#         # Create a QWidget container for the canvas
#         plot_container = QWidget()
#         plot_layout = QVBoxLayout()
#         plot_container.setLayout(plot_layout)
#         plot_layout.addWidget(canvas.native)
#         self.plot_widgets[key] = plot_container

#         self.scroll_layout.addWidget(plot_container)

#     def delete_plot(self, data):
#         key = f"{data['station']}-{data['channel']}"
#         if key in self.plot_widgets:
#             self.scroll_layout.removeWidget(self.plot_widgets[key])
#             self.plot_widgets[key].deleteLater()
#             del self.plot_widgets[key]
#             del self.plot_data[key]
#             # Decrement the count
#             self.count -= 1
#             print(f"Deleted plot: {key}")

#     def plot_update(self, data):
#         key = f"{data['station']}-{data['channel']}"
#         if key in self.plot_data:
#             plot_data_array = np.array(self.data[key]['data'])
#             if len(plot_data_array.shape) == 1:
#                 plot_data_array = np.column_stack((np.arange(len(plot_data_array)), plot_data_array))
#             self.plot_data[key].set_data(pos=plot_data_array)

# if __name__ == '__main__':
#     appQt = QApplication(sys.argv)
#     main_win = MainWindow()
#     main_win.show()
#     appQt.exec_()