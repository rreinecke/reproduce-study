import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

def get_label(data, question, n, toremove):
    '''
    Returns a dict that maps answer codes to answers
    n: number of fields
    ''' 
    an = data['variables']
    ran = np.arange(1,n+1)
    d = {}
    for i in ran:
        # there is probably an easier way to accieve this
        name = an[an['VAR'] == (question + '_0' + str(i))]["LABEL"].to_string(index=False)
        name = name.replace(toremove,'')
        d[i] = name
    return d


def p_demo(data):
    '''
    Plot Demographics
    '''
    #03 was the defintion that was removed, 04 does not exist
    names = {'DM01':"Career stage",'DM02_01':"Experience",'DM05':"Scale", 'DM06':"Field of research",'DM07': "Task"}

    d = data['data'][names.keys()]
    #iterate questions of catergory and plot for each
    for q in names.keys():
        date = d[q].copy().to_frame().sort_values(by=q)

        # What should the axis say?
        date.columns = [names[q]]

        # Get the full answer text instead of only a number
        if q not in ["DM02_01","DM06", "DM07"]:
            res = get_full_response(data, q)
            date[names[q]] = date[names[q]].map(res)

        # DM06 and DM07 have labels instead
        if q == "DM06":
            res = get_label(data, q, 11, " Field:")
            date[names[q]] = date[names[q]].map(res)
        #if q == "DM07":
        #FIXME not compatible with histplot -> also to long for a plot
        #    res = get_label(data, q, 5, " KindOfTask:")
        #    date[names[q]] = date[names[q]].map(res)

        ax = sns.histplot(x=names[q], data=date, discrete=True)
        plt.xticks(rotation=90, fontsize =5)
        plt.subplots_adjust(bottom=.4)

        ax.figure.savefig(d_path + sl + q + ".png", dpi=150)
        ax.figure.clf()

def get_all_data(data, q):
    '''
    Collects data from multiple field questions like O101
    '''
    
    date = data['data']
    # find out what fields exist
    col = date.columns.to_list()
    r = [i for i in col if q in i]
    
    return date[r], r 



def p_opinion(data):
    '''
    Plot Opinions
    '''

    names = {'O101':"Agreement",'O102':"Reproduce?",'O103':"Reasons"}   
    
    #iterate questions of catergory and ploti box for each
    for q in names.keys():
        d, cols = get_all_data(data, q)
        # frame with O101_01 etc. as col and data as row
        d.reset_index(level=0, inplace=True) 
        df = pd.melt(d, id_vars=['index'], value_vars=cols)

        ax = sns.boxplot(y="variable", x="value", data=df, orient="h")
        #ax.set_xticklabels(date["MEANING"],rotation=60)
        ax.figure.savefig(d_path + sl + q + ".png", dpi=150)
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
    #p_demo(data)
    p_opinion(data)
    #p_self(data)

all()
