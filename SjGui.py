import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore
import PyQt5.QtWidgets as QtW

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtW.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(QtW.QMainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.main_widget = QtW.QWidget(self)
        self.setCentralWidget(self.canvas)


        l = QtW.QVBoxLayout(self.main_widget)  

       # Snippet 3
        x = QtW.QHBoxLayout()         # self.main_widget) # new
        b1 = QtW.QPushButton("Test1") # new
        b2 = QtW.QPushButton("Test2") # new
        x.addWidget(b1)                     # new   + b1
        x.addWidget(b2)                     # new   + b2

        l.addLayout(x) 


        n_data = 50
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.xdata, self.ydata, 'r')
        # Trigger the canvas to update and redraw.
        self.canvas.draw()


app = QtW.QApplication(sys.argv)
w = MainWindow()
w.setWindowTitle("Glucose Measurements")
app.exec_()
