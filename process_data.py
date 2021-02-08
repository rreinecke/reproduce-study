'''
Reads in raw data and processes it to a pandas data-frame for plotting and evaluation.
'''

raw_data_path = "TestData"

import pandas as pd
import os
sl = os.path.sep

data = pd.read_csv(raw_data_path + sl + "data_test_plane.csv", sep=";")
val = pd.read_csv(raw_data_path + sl + "values_test.csv", sep=";", encoding = "ISO-8859-1")
var = pd.read_csv(raw_data_path + sl + "variables_test.csv", sep=";", encoding = "ISO-8859-1")


print(data.head)
print(val.head)
print(var.head)


