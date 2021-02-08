#!/usr/bin/env python3
# -*- coding: utf-8 -*-


### Runs the whole processing pipeline ###

import process_data
import plot_all

if __name__ == '__main__':
   process_data.process()
   plot_all.all()
