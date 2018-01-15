##import numpy as np
##import matplotlib.pyplot as plt
##import matplotlib.animation as animation
##
##fig = plt.figure()
##ax = fig.add_subplot(111)
##line, = ax.plot(np.random.rand(10))
##ax.set_ylim(0, 1)
##
##def update(data):
##    line.set_ydata(data)
##    return line,
##
##def data_gen():
##    while True: yield np.random.rand(10)
##
##ani = animation.FuncAnimation(fig, update, data_gen, interval=100)
##plt.show()


##"""
##A simple example of an animated plot
##"""
##import numpy as np
##import matplotlib.pyplot as plt
##import matplotlib.animation as animation
##
##fig = plt.figure()
##ax = fig.add_subplot(111)
##
##x = np.arange(0, 2*np.pi, 0.01)        # x-array
##line, = ax.plot(x, np.sin(x))
##
##def animate(i):
##    line.set_ydata(np.sin(x+i/10.0))  # update the data
##    return line,
##
###Init only required for blitting to give a clean slate.
##def init():
##    line.set_ydata(np.ma.array(x, mask=True))
##    return line,
##
##ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
##    interval=25, blit=True)
##plt.show()


##
### For detailed comments on animation and the techniqes used here, see
### the wiki entry http://www.scipy.org/Cookbook/Matplotlib/Animations
##
##import os
##import sys
##
###import matplotlib
###matplotlib.use('Qt4Agg')
##from matplotlib.figure import Figure
##from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
##
##from PyQt4 import QtCore, QtGui
##
##ITERS = 1000
##
##import numpy as np
##import time
##
##class BlitQT(FigureCanvas):
##
##    def __init__(self):
##        FigureCanvas.__init__(self, Figure())
##
##        self.ax = self.figure.add_subplot(111)
##        self.ax.grid()
##        self.draw()
##
##        self.old_size = self.ax.bbox.width, self.ax.bbox.height
##        self.ax_background = self.copy_from_bbox(self.ax.bbox)
##        self.cnt = 0
##
##        self.x = np.arange(0,2*np.pi,0.01)
##        self.sin_line, = self.ax.plot(self.x, np.sin(self.x), animated=True)
##        self.cos_line, = self.ax.plot(self.x, np.cos(self.x), animated=True)
##        self.draw()
##
##        self.tstart = time.time()
##        self.startTimer(10)
##
##    def timerEvent(self, evt):
##        current_size = self.ax.bbox.width, self.ax.bbox.height
##        if self.old_size != current_size:
##            self.old_size = current_size
##            self.ax.clear()
##            self.ax.grid()
##            self.draw()
##            self.ax_background = self.copy_from_bbox(self.ax.bbox)
##
##        self.restore_region(self.ax_background)
##
##        # update the data
##        self.sin_line.set_ydata(np.sin(self.x+self.cnt/10.0))
##        self.cos_line.set_ydata(np.cos(self.x+self.cnt/10.0))
##        # just draw the animated artist
##        self.ax.draw_artist(self.sin_line)
##        self.ax.draw_artist(self.cos_line)
##        # just redraw the axes rectangle
##        self.blit(self.ax.bbox)
##
##        if self.cnt == 0:
##            # TODO: this shouldn't be necessary, but if it is excluded the
##            # canvas outside the axes is not initially painted.
##            self.draw()
##        if self.cnt==ITERS:
##            # print the timing info and quit
##            print ('FPS:' + ITERS/(time.time()-self.tstart))
##            sys.exit()
##        else:
##            self.cnt += 1
##
##app = QtGui.QApplication(sys.argv)
##widget = BlitQT()
##widget.show()
##
##sys.exit(app.exec_())



##
##"""
##Emulate an oscilloscope.  Requires the animation API introduced in
##matplotlib 1.0 SVN.
##"""
##import matplotlib
##import numpy as np
##from matplotlib.lines import Line2D
##import matplotlib.pyplot as plt
##import matplotlib.animation as animation
##
##class Scope:
##    def __init__(self, ax, maxt=2, dt=0.02):
##        self.ax = ax
##        self.dt = dt
##        self.maxt = maxt
##        self.tdata = [0]
##        self.ydata = [0]
##        self.line = Line2D(self.tdata, self.ydata)
##        self.ax.add_line(self.line)
##        self.ax.set_ylim(-.1, 1.1)
##        self.ax.set_xlim(0, self.maxt)
##
##    def update(self, y):
##        lastt = self.tdata[-1]
##        if lastt > self.tdata[0] + self.maxt: # reset the arrays
##            self.tdata = [self.tdata[-1]]
##            self.ydata = [self.ydata[-1]]
##            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
##            self.ax.figure.canvas.draw()
##
##        t = self.tdata[-1] + self.dt
##        self.tdata.append(t)
##        self.ydata.append(y)
##        self.line.set_data(self.tdata, self.ydata)
##        return self.line,
##
##
##def emitter(p=0.03):
##    'return a random value with probability p, else 0'
##    while True:
##        v = np.random.rand(1)
##        if v > p:
##            yield 0.
##        else:
##            yield np.random.rand(1)
##
##fig = plt.figure()
##ax = fig.add_subplot(111)
##scope = Scope(ax)
##
### pass a generator in "emitter" to produce data for the update func
##ani = animation.FuncAnimation(fig, scope.update, emitter, interval=10,
##    blit=True)
##
##
##plt.show()


import matplotlib.pyplot as plt
import matplotlib.animation as animation

random_list = [10,3,5,4,9,1,6,7,2,8]

def bubble_sort():
    data = random_list
    for i in range(len(data)-1):
        for j in range(i, len(data)-1):
            a, b = data[j], data[j+1]
            if a > b:
                data[j], data[j+1] = b, a
                yield data

fig = plt.figure()
ax = fig.add_subplot(111)
def update(data):
    ax.clear()
    ax.hlines(range(len(data)), 0, data, 'red')
    ax.set_ylim(-0.5, 9.5)
update(random_list)

ani = animation.FuncAnimation(fig, update, bubble_sort, interval=250)
plt.show()
