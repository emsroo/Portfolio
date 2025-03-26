import serial
import time
import csv
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import numpy as np

ser = serial.Serial("COM9")
ser.flushInput()

plot_window = 20
y_var = np.array(np.zeros([plot_window]))

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(y_var)
fig.canvas.manager.set_window_title('Glucose Measurement')
ax.set_ylabel('Current [uA]')
ax.set_xlabel('Time [s]')
while True:
    try:
        ser_bytes = ser.readline()
        ser_decode = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        temperature = ser_decode.split(",")[0]
        current = ser_decode.split(",")[1]
        ax.set_title(f'Glucose Variation at T = {temperature}°C')
        try:
            decoded_bytes = float(current)
            print(decoded_bytes)
        except:
            continue
        with open("test_data.csv","a") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow([time.time(),decoded_bytes])
        y_var = np.append(y_var,decoded_bytes)
        y_var = y_var[1:plot_window+1]
        line.set_ydata(y_var)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        
        fig.canvas.flush_events()
        time.sleep(1)
    except:
        print("Keyboard Interrupt")
        break