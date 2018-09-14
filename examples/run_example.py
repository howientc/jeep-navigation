#!/usr/bin/python3
#  -*- coding: utf-8 -*-
"""
Runs the example. Sets the python path first in case PYTHONPATH isn't correct
"""
import sys
sys.path.extend(['.', './src', './tests', './examples'])
# noinspection PyPep8
from examples.plot_path import PlotPathExample

if __name__ == '__main__':
    example = PlotPathExample()
    example.run()
