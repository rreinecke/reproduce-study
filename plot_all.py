import seaborn as sns
import pandas as pd

import os
sl = os.path.sep

d_path= "figs" 

try:
    os.mkdir(d_path)
except OSError as error:
    pass

def read_data():
    df_d = pd.read_feather("tmp" + sl + "__data.feather") 
    df_val = pd.read_feather("tmp" + sl + "__val.feather") 
    df_var = pd.read_feather("tmp" + sl + "__var.feather")
    return {"data":df_d, "values": df_val, "variables": df_var}

def p_demo(data):
    '''
    Plot Demographics
    '''

    qs = ['DM01','DM02_01','DM05','DM06']
    names = {'DM01':"Career stage",'DM02_01':"Experience",'DM05':"Field of research",'DM06':"Scale"}   

    d = data['data'][qs]
    #iterate questions of catergory and plot box for each
    for q in qs:
        date = d[q].copy().to_frame()
        # What should the Y-axis say?
        date["Variable"] = names[q]
        
        # Get the full answer text
        an = data['values']
        an = an[an['VAR'] == q]
        #RESPONSE MEANING
        # TODO

        ax = sns.boxplot(y = "Variable", x=q, data=date, orient="h")
        ax.figure.savefig(d_path + sl + q + ".png")
        ax.figure.clf()

def all():
    data = read_data()
    p_demo(data)

all()
