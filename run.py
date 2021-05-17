#!/usr/bin/env python3
# -*- coding: utf-8 -*-


### Runs the whole processing pipeline ###

import process_data as data
import plot_all as plots
import stat_tests as tests
import os

if __name__ == '__main__':
   data.process()
   plots.all()
   tests.run_all()
   print("Creating latex report from figures")
   os.system("cd report && ./build.sh")
