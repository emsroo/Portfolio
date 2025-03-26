from datetime import datetime
import sys, serial, serial.tools.list_ports, warnings
from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QThread, pyqtSignal, pyqtSlot, QTimer
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.uic import loadUi
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import numpy as np
import random

matplotlib.use("QT5Agg")
#Port Detection START
# ports = [
#     p.device
#     for p in serial.tools.list_ports.comports()
#     if 'USB' in p.description
# ]
# 
# if not ports:
#     raise IOError("There is no device exist on serial port!")
# 
# if len(ports) > 1:
#     warnings.warn('Connected....')

# ser = serial.Serial(ports[0],9600)
ports = ['COM9']
ser = serial.Serial(ports[0],230400)
#Port Detection END

# MULTI-THREADING

class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(str,float,float)
    updGraph = pyqtSignal(float)

    @pyqtSlot()
    def __init__(self):
        super(Worker, self).__init__()
        self.working = True

    prev_current = 0
    counter =0
    max_value =False
    startup = True
    glucose = 0
    
    def work(self):

        while self.working:
            line = ser.readline().decode('utf-8')
            if self.startup ==True:
                time.sleep(3)
                self.startup = False
            if len(line) < 5:
                continue
            temperature = float(line.split(",")[0])
            current = float(line.split(",")[1])
            
            if (current < self.prev_current or self.max_value == True) and (self.prev_current > 0.1E-6):
                self.max_value = True
                self.counter+=1
            else:
                self.prev_current = current

            if self.counter == 20:
                self.glucose =((current*1E6)+0.2294)/0.3665
                line = f"{temperature}, {self.glucose} g/100ml"
                self.prev_current = current
                time.sleep(0.1)
                self.intReady.emit(line, temperature, self.glucose)
                self.max_value = False
                self.counter = 0
            else:
                line = f"{temperature}, {current}"
                time.sleep(0.1)
                self.intReady.emit(line, temperature, self.glucose)

            self.updGraph.emit(current)


        self.finished.emit()

    
class qt(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        loadUi('qt.ui', self)
        self.thread = None
        self.worker = None
        self.pushButton.clicked.connect(self.start_loop)
        self.label_11.setText(ports[0])
        self.plot_window = 20
        
        self.start = 0
        self.y_var = np.array(np.zeros([self.plot_window]))
        self.x_var = np.array(np.zeros([self.plot_window]))
        self.MplWidget.setContentsMargins(1, 1, 1, 1)
        # self.MplWidget.canvas.axes = None

    def loop_finished(self):
        print('Loop Finished')

    def start_loop(self):

        self.worker = Worker()   # a new worker to perform those tasks
        self.thread = QThread()  # a new thread to run our background tasks in
        self.worker.moveToThread(self.thread)  # move the worker into the thread, do this first before connecting the signals

        self.thread.started.connect(self.worker.work) # begin our worker object's loop when the thread starts running

        self.worker.intReady.connect(self.onIntReady)
        self.worker.updGraph.connect(self.update_graph)
        self.pushButton_2.clicked.connect(self.stop_loop)      # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)       # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)         # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion

        self.thread.start()

    def stop_loop(self):
        self.worker.working = False

    def onIntReady(self, i, temp, glucose):
        self.textEdit_3.append("{}".format(i))
        self.lcdGlucose.display(glucose)
        self.lcdTemperature.display(temp)
        print(i)

    # Save the settings
    def on_pushButton_4_clicked(self):
        if self.x != 0:
            self.textEdit.setText('Settings Saved!')
        else:
            self.textEdit.setText('Please enter port and speed!')

    # TXT Save
    def on_pushButton_5_clicked(self):
        now = datetime.now()
        date_time = now.strftime("%m-%d-%Y_%H%M%S")
        print("date and time:",date_time)
        beverage_id = self.textEdit_4.toPlainText()
        with open(f'Glucose_{beverage_id}_{date_time}.txt', 'w') as f:
            my_text = self.textEdit_3.toPlainText()
            f.write(my_text)

    def on_pushButton_2_clicked(self):
        self.textEdit.setText('Stopped! Please click CONNECT...')

    def on_pushButton_clicked(self):

        self.completed = 0
        while self.completed < 100:
            self.completed += 0.001
            self.progressBar.setValue(self.completed)
        self.textEdit.setText('Data Gathering...')
        self.label_5.setText("CONNECTED!")
        self.label_5.setStyleSheet('color: green')
        x = 1
        self.textEdit_3.setText("Temperature(C), Current(uA)")

    def on_pushButton_3_clicked(self):
        # Send data from serial port:
        mytext = self.textEdit_2.toPlainText()
        ser.write(mytext.encode())

    def update_graph(self, current):
        #if self.MplWidget.canvas.axes is None:
        #    self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.subplots()
        fs = 500
        f = random.randint(1, 100)
        ts = 1/fs
        length_of_signal = 20
        t = np.linspace(self.start,1,length_of_signal)
        self.x_var = np.append(self.x_var,self.start)
        self.y_var = np.append(self.y_var,current)
        #self.y_var = self.y_var[1:self.plot_window+1]
        #self.MplWidget.canvas.axes.set_ydata(self.y_var)
        #cosinus_signal = np.cos(2*np.pi*f*t)

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(self.x_var, self.y_var)
        self.MplWidget.canvas.axes.set_ylabel('Current [uA]')
        self.MplWidget.canvas.axes.set_xlabel('Time [s]')
        self.MplWidget.canvas.axes.set_title('Current SIGNAL')
        self.MplWidget.canvas.draw()

        self.MplWidget.canvas.flush_events()
        self.start +=1        

def run():
    app = QApplication(sys.argv)
    widget = qt()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
