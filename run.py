#!/usr/bin/env python3
# -*- coding: utf-8 -*-


### Runs the whole processing pipeline ###

import process_data
import plot_all
import os

if __name__ == '__main__':
   #process_data.process()
   #plot_all.all()
   print("Creating latex report from figures")
   os.system("cd report && ./build.sh")
