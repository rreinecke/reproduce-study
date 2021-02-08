'''
Reads in raw data and processes it to a pandas data-frame for plotting and evaluation.
'''

# Where to read the data from
raw_data_path = "TestData"
# Strip unnecessary variables
clean = True
# Print summary to console?
debug = True


# Imports
import pandas as pd
import os
sl = os.path.sep


def process():
    data = pd.read_csv(raw_data_path + sl + "data_test_plane.csv", sep=";")
    val = pd.read_csv(raw_data_path + sl + "values_test.csv", sep=";", encoding = "ISO-8859-1")
    var = pd.read_csv(raw_data_path + sl + "variables_test.csv", sep=";", encoding = "ISO-8859-1")

    # stripping away data that is not necessary for the plots and targeted analysis
    if clean:
        data.drop(['CASE', 'SERIAL', 'REF', 'MODE', 'STARTED', 'MAILSENT', 'LASTDATA', 'FINISHED', 'Q_VIEWER', 'LASTPAGE', 'MAXPAGE', 'MISSING', 'MISSREL', 'TIME_RSI'], axis=1)
        var.drop(['TYPE', 'INPUT', 'QUESTION'], axis=1)
    if debug:
        print(data.head)
        print(val.head)
        print(var.head)

    try:
        os.mkdir("tmp")
    except OSError as error:
        if debug:
            print("tmp already exists")

    if debug:
        print("Writing test data to temp frames ...")
    data.to_feather("tmp" + sl + "__data.feather")
    val.to_feather("tmp" + sl + "__val.feather")
    var.to_feather("tmp" + sl + "__var.feather")

process()

