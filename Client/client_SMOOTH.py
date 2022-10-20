import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import scipy.signal

# plot class
class AnalogPlot:
  def __init__(self, strPort, maxLen):
      # open serial port
      self.ser = serial.Serial(strPort, 9600)

      # Initialize internal buffer
      self.batchSize = 10
      self.internal_buffer = [0.0]*self.batchSize

      # Initialize buffer to plot
      self.maxLen = maxLen
      self.ax = [0.0]*maxLen

      # Counter for slicing
      self.counterValue = 0
      self.counterOffset = 0

  # update plot
  def update(self, frameNum, a0):
    if self.counterValue < self.batchSize:
      # Fill internal buffer
      try:
        # Read data from serial
        data = float(self.ser.readline())
        # Update inernal buffer
        self.internal_buffer[self.counterValue]=data
        # Update buffer counter
        self.counterValue += 1
      except:
          pass

    elif self.counterValue == self.batchSize:
      # Buffer full -> prepare for plotting
      
      # Do something with the buffer
      filtered_batch = scipy.signal.savgol_filter(self.internal_buffer,7,3)
      
      # Replace batchSize elements in the "official" array
      self.ax[self.counterOffset:self.counterOffset+self.batchSize] = filtered_batch

      # Set data for the new plot
      a0.set_data(range(self.maxLen), self.ax)
      
      # Clean (create new) internal buffer (already used!)
      self.internal_buffer = [0.0]*self.batchSize
      # Set to 0 the internal counter (it's for filling the internal buffer)
      self.counterValue = 0
      
      # Update offset counter (it's for official array slicing)
      self.counterOffset += self.batchSize
    
    # The plot is full, go back to the start
    if self.counterOffset + self.batchSize > self.maxLen:
      self.counterOffset = 0

    return a0,

  # clean up
  def close(self):
      # close serial
      self.ser.flush()
      self.ser.close()

# main() function
def main():
  # create parser
  parser = argparse.ArgumentParser(description="LDR serial")
  # add expected arguments
  parser.add_argument('--port', dest='port', required=True)
  parser.add_argument('--maxLen', dest='maxLen', type=int, default=300)

  # parse args
  args = parser.parse_args()

  strPort = args.port
  maxLen = args.maxLen

  print('reading from serial port %s...' % strPort)

  # plot parameters
  analogPlot = AnalogPlot(strPort, maxLen)

  print('plotting data...')

  # set up animation
  fig = plt.figure()
  ax = plt.axes(xlim=(0, maxLen), ylim=(200, 500))
  a0, = ax.plot([], [])
  anim = animation.FuncAnimation(fig, analogPlot.update,
                                 fargs=(a0,),
                                 interval=10)

  # show plot
  plt.show()

  # clean up
  analogPlot.close()

  print('exiting.')

# call main
if __name__ == '__main__':
  main()
