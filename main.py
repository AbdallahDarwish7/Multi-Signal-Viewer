from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
import pyqtgraph as pg
import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import pyedflib
import math


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui.ui', self)

        self.graphicsView1.setXRange(min=-1, max=10)
        self.graphicsView2.setXRange(min=-1, max=10)
        self.graphicsView3.setXRange(min=-1, max=10)
        self.EEG_S = 4

        self.hint.setText("<center><b>Standard mouse interaction:</b><br>Scroll to zoom, Hold and Drag to pan</center>")
        self.pens = [pg.mkPen('r'), pg.mkPen('y'), pg.mkPen('g'), pg.mkPen('b'), pg.mkPen('w')]
        self.disable_btns()

        # Tools
        self.signals = [0, 0, 0, 0, 0]
        self.timers = [0, 0, 0, 0, 0]
        self.xs = [0, 0, 0, 0, 0]
        self.ys = [0, 0, 0, 0, 0]
        self.indices = [-1, -1, -1, -1, -1]
        self.file_ex = [0, 0, 0, 0, 0]

        # Connecting Signals to buttons
        self.add_signal_btn.clicked.connect(self.add_signal)
        self.play_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.channel.activated.connect(self.control_btns)

    def add_signal(self):

        channel_index = self.channel.currentIndex()
        filename = QFileDialog(self).getOpenFileName()
        path = filename[0]
        if self.play_btn.isEnabled() and path != '':
            self.clear()
        self.file_ex[channel_index] = self.get_extention(path)
        if self.file_ex[channel_index] == 'txt':
            data = pd.read_csv(path)
            self.ys[channel_index] = data.values[:, 0]
            self.xs[channel_index] = np.linspace(0, 0.001 * len(self.ys[channel_index]), len(self.ys[channel_index]))
        if self.file_ex[channel_index] == 'csv':
            data = pd.read_csv(path)
            self.ys[channel_index] = data.values[:, 1]
            self.xs[channel_index] = data.values[:, 0]
        if self.file_ex[channel_index] == 'edf':
            data = pyedflib.EdfReader(path)
            data_labels = data.getSignalLabels()
            self.xs[channel_index] = []
            self.ys[channel_index] = []
            for i in range(4):
                self.ys[channel_index].append(data.readSignal(i))
                self.xs[channel_index].append(
                    np.linspace(0, 1 / 160 * self.ys[channel_index][i].size, self.ys[channel_index][i].size))
        self.indices[channel_index] = 0
        if path == '':
            self.disable_btns()
        else:
            self.enable_btns()

        # initializing signal
        if channel_index == 0:
            self.legend1 = self.graphicsView1.addLegend()
            if self.file_ex[0] == 'edf':
                self.signals[0] = [0, 0, 0, 0]
                for i in range(4):
                    self.signals[0][i] = self.graphicsView1.plot(pen=self.pens[i], name=data_labels[i])
            elif self.file_ex[0] == 'txt':
                self.signals[0] = self.graphicsView1.plot(pen=self.pens[0], name='ecg')
            elif self.file_ex[0] == 'csv':
                self.signals[0] = self.graphicsView1.plot(pen=self.pens[0], name='emg')
            self.draw()
        elif channel_index == 1:
            self.legend2 = self.graphicsView2.addLegend()
            if self.file_ex[1] == 'edf':
                self.signals[1] = [0, 0, 0, 0]
                for i in range(self.EEG_S):
                    self.signals[1][i] = self.graphicsView2.plot(pen=self.pens[i], name=data_labels[i])
            elif self.file_ex[1] == 'txt':
                self.signals[1] = self.graphicsView2.plot(pen=self.pens[1], name='ecg')
            elif self.file_ex[1] == 'csv':
                self.signals[1] = self.graphicsView2.plot(pen=self.pens[1], name='emg')
            self.draw()
        elif channel_index == 2:
            self.legend3 = self.graphicsView3.addLegend()
            if self.file_ex[2] == 'edf':
                self.signals[2] = [0, 0, 0, 0]
                for i in range(self.EEG_S):
                    self.signals[2][i] = self.graphicsView3.plot(pen=self.pens[i], name=data_labels[i])
            elif self.file_ex[2] == 'txt':
                self.signals[2] = self.graphicsView3.plot(pen=self.pens[2], name='ecg')
            elif self.file_ex[2] == 'csv':
                self.signals[2] = self.graphicsView3.plot(pen=self.pens[2], name='emg')
            self.draw()

    def get_extention(self, s):
        for i in range(1, len(s)):
            if s[-i] == '.':
                return s[-(i - 1):]

    def draw(self):
        channel_index = self.channel.currentIndex()

        if self.timers[channel_index] != 0:  # if it was played, stop timer
            self.timers[channel_index].stop()

        # Graph settings
        if channel_index == 0:
            if self.file_ex[channel_index] == 'edf':
                self.graphicsView1.setYRange(min=min(self.ys[channel_index][0]), max=max(self.ys[channel_index][0]))
            else:
                self.graphicsView1.setYRange(min=min(self.ys[channel_index]), max=max(self.ys[channel_index]))

            self.graphicsView1.invertX(False)  # if it was inverted for playing, return to its default
            self.graphicsView1.setXRange(min=-1, max=10)
            self.graphicsView1.setLimits(xMin=-math.inf)  # set limits to its default value if there was play

        elif channel_index == 1:
            if self.file_ex[channel_index] == 'edf':
                self.graphicsView2.setYRange(min=min(self.ys[channel_index][0]), max=max(self.ys[channel_index][0]))
            else:
                self.graphicsView2.setYRange(min=min(self.ys[channel_index]), max=max(self.ys[channel_index]))

            self.graphicsView2.invertX(False)  # if it was inverted for playing, return to its default
            self.graphicsView2.setXRange(min=-1, max=10)
            self.graphicsView2.setLimits(xMin=-math.inf)
        elif channel_index == 2:
            if self.file_ex[channel_index] == 'edf':
                self.graphicsView3.setYRange(min=min(self.ys[channel_index][0]), max=max(self.ys[channel_index][0]))
            else:
                self.graphicsView3.setYRange(min=min(self.ys[channel_index]), max=max(self.ys[channel_index]))

            self.graphicsView3.invertX(False)  # if it was inverted for playing, return to its default
            self.graphicsView3.setXRange(min=-1, max=10)
            self.graphicsView3.setLimits(xMin=-math.inf)
            # Sending data
        if self.file_ex[channel_index] == 'edf':
            for i in range(self.EEG_S):
                self.signals[channel_index][i].setData(self.xs[channel_index][i], self.ys[channel_index][i])
                self.signals[channel_index][i].setPos(0, 100 * i)

        else:
            self.signals[channel_index].setPos(0, 0)  # set position to its origin if there was a play
            self.signals[channel_index].setData(self.xs[channel_index], self.ys[channel_index])

        self.indices[channel_index] = 0  # clear play if it was played before show

    def start(self):
        channel_index = self.channel.currentIndex()

        if self.timers[channel_index] == 0:  # if timer wasn't initialized
            self.timers[channel_index] = QtCore.QTimer()
            self.timers[channel_index].setInterval(30)
            self.timers[channel_index].timeout.connect(lambda: self.play(channel_index))

        self.timers[channel_index].start()

    def play(self, channel_index):

        # Graph settings
        if channel_index == 0:
            self.graphicsView1.invertX(True)
            self.graphicsView1.setLimits(xMin=-0.2)
            # print(self.graphicsView1.viewRange())
        elif channel_index == 1:
            self.graphicsView2.invertX(True)
            self.graphicsView2.setLimits(xMin=-0.2)
        elif channel_index == 2:
            self.graphicsView3.invertX(True)
            self.graphicsView3.setLimits(xMin=-0.2)

        # getting size of signal
        if self.file_ex[channel_index] == 'edf':
            n = self.ys[channel_index][0].size
        else:
            n = self.ys[channel_index].size

        index = self.indices[channel_index]

        if index < n:
            if self.file_ex[channel_index] == 'edf':
                for i in range(self.EEG_S):
                    self.signals[channel_index][i].setData(-self.xs[channel_index][i][:index + 1],
                                                           self.ys[channel_index][i][:index + 1])
                    self.signals[channel_index][i].setPos(self.xs[channel_index][i][index], 100 * i)
                self.indices[channel_index] += 20
            else:
                self.signals[channel_index].setData(-self.xs[channel_index][:index + 1],
                                                    self.ys[channel_index][:index + 1])
                self.signals[channel_index].setPos(self.xs[channel_index][index], 0)
                self.indices[channel_index] += 50
        else:
            if self.file_ex[channel_index] == 'edf':
                for i in range(self.EEG_S):
                    self.signals[channel_index][i].setData(-self.xs[channel_index][i], self.ys[channel_index][i])
                    self.signals[channel_index][i].setPos(self.xs[channel_index][i][-1], 100 * i)
            else:
                self.signals[channel_index].setData(-self.xs[channel_index], self.ys[channel_index])
                self.signals[channel_index].setPos(self.xs[channel_index][-1], 0)

            self.timers[channel_index].stop()

    def pause(self):
        channel_index = self.channel.currentIndex()
        self.timers[channel_index].stop()

        # if self.timers[0] != 0:
        #     self.timers[0].stop()
        # if self.timers[1] != 0 :
        #     self.timers[1].stop()
        # if self.timers[2] != 0 :
        #     self.timers[2].stop()

    def clear(self):
        channel_index = self.channel.currentIndex()
        if self.timers[channel_index] != 0:
            self.timers[channel_index].stop()

        if channel_index == 0:
            self.graphicsView1.clear()
            self.legend1.scene().removeItem(self.legend1)
        elif channel_index == 1:
            self.graphicsView2.clear()
            self.legend2.scene().removeItem(self.legend2)
        else:
            self.graphicsView3.clear()
            self.legend3.scene().removeItem(self.legend3)

        # Clear tools
        self.indices[channel_index] = -1
        self.file_ex[channel_index] = 0
        self.xs[channel_index] = 0
        self.ys[channel_index] = 0
        self.disable_btns()

    def control_btns(self, channel_index):  # According to the selected channel
        if self.indices[channel_index] == -1:
            self.disable_btns()
        else:
            self.enable_btns()

    def enable_btns(self):
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)

    def disable_btns(self):
        self.play_btn.setDisabled(True)
        self.pause_btn.setDisabled(True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
