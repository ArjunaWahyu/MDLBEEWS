from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from socketio_client import SocketIOClient

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Real-time Seismic Wave")
        
        self.x_data = list(range(200))
        self.y_data = [0] * 200
        
        self.line, = self.ax.plot(self.x_data, self.y_data)
        
        # Start Socket.IO Client
        self.socketio_client = SocketIOClient(self.update_plot)
        self.socketio_client.start()
        
        self.ani = animation.FuncAnimation(self.figure, self.update_canvas, interval=1000)

    def update_plot(self, x: list, y: list):
        self.x_data = x
        self.y_data = y
        self.update_canvas(None)

    def update_canvas(self, frame):
        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
