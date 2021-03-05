import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

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

def get_full_response(data, question):
    '''
    Returns a dict that maps answer codes to answers
    '''
    an = data['values']
    an = an[an['VAR'] == question].sort_values(by='RESPONSE')
    return dict(zip(an['RESPONSE'], an['MEANING']))


def p_demo(data):
    '''
    Plot Demographics
    '''

    # FIXME Y DM02_01 ?
    names = {'DM01':"Career stage",'DM02_01':"Experience",'DM05':"Field of research",'DM06':"Scale"}   

    d = data['data'][names.keys()]
    #iterate questions of catergory and plot for each
    for q in names.keys():
        date = d[q].copy().to_frame().sort_values(by=q)

        # What should the axis say?
        date.columns = [names[q]]
        
        # Get the full answer text instead of only a number
        res = get_full_response(data,q)
        date[names[q]] = date[names[q]].map(res)

        ax = sns.histplot(x=names[q], data=date, discrete=True)
        plt.xticks(rotation=90, fontsize =5)
        plt.subplots_adjust(bottom=.4)

        ax.figure.savefig(d_path + sl + q + ".png", dpi=150)
        ax.figure.clf()

def p_opinion(data):
    '''
    Plot Opinions
    '''

    # TODO answers are _X but without logical order
    #"O101_01";"O101_02";"O101_12";"O101_03";"O101_04";"O101_16";"O101_05";"O101_15";"O101_06";"O101_07";"O101_08";"O101_17";
    
    names = {'O102':"Reproduce?",'O101':"Agreement",'O103':"Reasons"}   

    d = data['data'][names.keys()]
    #iterate questions of catergory and plot box for each
    for q in names.keys():
        date = d[q].copy().to_frame()
        # What should the Y-axis say?
        date["Variable"] = names[q]
        
        # Get the full answer text
        an = data['values']
        an = an[an['VAR'] == q]
        #RESPONSE MEANING
        date = date.merge(an, left_on=q, right_on='RESPONSE')
        
        ax = sns.boxplot(y="Variable", x=q, data=date, orient="h")
        ax.set_xticklabels(date["MEANING"],rotation=60)
        ax.figure.savefig(d_path + sl + q + ".png")
        ax.figure.clf()

def p_self(data):
    '''
    Plot Self-assemssment
    '''


    d = data['data'][names.keys()]
    #iterate questions of catergory and plot box for each
    for q in names.keys():
        date = d[q].copy().to_frame()
        # What should the Y-axis say?
        date["Variable"] = names[q]
        
        # Get the full answer text
        an = data['values']
        an = an[an['VAR'] == q]
        #RESPONSE MEANING
        date = date.merge(an, left_on=q, right_on='RESPONSE')
        
        ax = sns.boxplot(y="Variable", x=q, data=date, orient="h")
        ax.set_xticklabels(date["MEANING"],rotation=60)
        ax.figure.savefig(d_path + sl + q + ".png")
        ax.figure.clf()


def all():
    data = read_data()
    p_demo(data)
    #TODO implement
    #p_opinion(data)
    #p_self(data)

all()
