import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
sl = os.path.sep

'''
Copyright Robert Reinecke

This scripts plots all figures and data shown in a scientific publication.
The first half is a collection of helper functions that are used to process the very diverse data.
'''


# Where should the figure be plotted relative to the script?
d_path= "figs" 

# Create a folder if it doesn't exist already
try:
    os.mkdir(d_path)
except OSError as error:
    pass

# We are reading some very long string but still want to display them fully in all plots
pd.set_option('display.max_colwidth', None) 

def read_data():
    '''
    Reads the preprocessed data from temprory feather files.
    Assumes that pre-processing was applied.
    @return a dicts that stores the 3 data fields that sociy provides
    '''
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

def get_label_by_names(data, qs, toremove):
    '''
    Returns a dict that maps answer codes to answers
    ''' 
    an = data['variables']
    #iterate questions
    d = {}
    for q in qs:
        name = an[an['VAR'] == q]["LABEL"].to_string(index=False)
        if isinstance(toremove, list):
            for rem in toremove:
                name = name.replace(rem,'')
        else:
            name = name.replace(toremove,'')
        d[q] = name
    return d


def p_demo(data):
    '''
    Plot Demographics
    '''
    #03 was the defintion that was removed, 04 does not exist
    names = {'DM01':"Career stage",'DM02_01':"Years of experience",'DM05':"Scale", 'DM06':"Field of research",'DM07': "Main work task"}

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
            if q == "DM01":
                # manual shorten some names -> too long to plot them properly
                date.loc[date[names[q]] == "Student (undergraduate, Bachelor/Master or similar)"] = "Student (BA/MA)"
                date.loc[date[names[q]] == "Group leader / junior professor"] = "Group leader"

        # DM06 and DM07 have labels instead
        if q == "DM06":
            res = get_label(data, q, 11, " Field:")
            date[names[q]] = date[names[q]].map(res)
        if q == "DM07":
            res = get_label(data, q, 5, " KindOfTask:")
            date[names[q]] = date[names[q]].map(res)
            # shorten answers -> too long to plot properly
            date.loc[date[names[q]] == " KindOfTasks: I conduct research that improves our process understanding by conducting field or lab experiments."] = "Field/Lab work"
            date.loc[date[names[q]] == " KindOfTasks: I conduct research by developing and using computational models."] = "Develope and apply models"
            date.loc[date[names[q]] == " KindOfTasks: I conduct research by applying computational models without building them myself."] = "Apply models"
            date.loc[date[names[q]] == " KindOfTasks: I develop computational models but do not conduct any research."] = "Develope models"
            # No answer for " KindOfTasks: I use results of models in my work (e.g., policy, consultation) but do not conduct any research myself."] = "Consulting" 
            # date.loc[date[names[q]] == " KindOfTasks: I use results of models in my work (e.g., policy, consultation) but do not conduct any research myself."] = "Consulting" 
            date[names[q]].dropna(inplace=True) 

        if q == "DM05":
            '''
            Histplot does not support a categorial ordering.
            For some plots we might want to adjust the automatic ordering to make sense.
            '''
            t = pd.CategoricalDtype(categories=['Global', 'Continental', '< Million km²', '< 1000 km²', '< km²', '< m²', '< cm²', 'Mixed', 'Does not apply to me'], ordered=True)
            date['sort'] = pd.Series(date[names[q]], dtype=t)
            date.sort_values(by=['sort'],inplace=True)
        
        ax = sns.histplot(x=names[q], data=date, discrete=True, fill=False, stat="probability")

        sns.despine(trim=True, offset=2);
        plt.xticks(rotation=-45, fontsize = 8, ha="left", rotation_mode="anchor")
        plt.subplots_adjust(bottom=.3)
        #ax.set_ylabel("")

        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
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

explenation_s = "|We explicitly exclude the retracing of results by means of using a different modeling environment (including variations in model concept, algorithms, input data or methodology).))"
explenation_a_s = "|We explicitly exclude the retracing of results by means of using a different modeling environment (including variations in model concept, algorithms, input data or methodology).))"
expl_missing_s = "|TODO defintion.))" 
expl_soft_s = "|How the software is used, e.g., input format, configuration options, and example problems.))"

def p_opinion(data):
    '''
    Plot Opinions
    '''

    names = {'O101':"Agreement",'O102':"Reproduce?",'O103':"Reasons", 'S201': "Actions"}   
    
    #iterate questions of catergory and plot box for each
    for q in names.keys():
        d, cols = get_all_data(data, q)

        # frame with O101_01 etc. as col and data as row
        d.reset_index(level=0, inplace=True) 
        df = pd.melt(d, id_vars=['index'], value_vars=cols)

        res = get_label_by_names(data, cols, [" Opinion:", "reasons:", "Reproduce?:", "Helpful Suggestions:", "((", explenation_s, explenation_a_s, expl_missing_s, expl_soft_s])
        df["variable"] = df["variable"].map(res)


        if q == "O102": 
            plt.figure(figsize=(12,4))
            plt.yticks(fontsize = 8)
            df["Answer"] = df["value"].map({1:"Yes", 2:"No"})
            ax = sns.histplot(y="variable", hue="Answer", data=df, discrete=True, multiple="stack", shrink=.8)
            plt.subplots_adjust(left=.5)
            ax.set(ylabel='')
            ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
            ax.figure.clf()
            continue

        plt.figure(figsize=(12,4))
        ax = sns.boxplot(y="variable", x="value", data=df, orient="h")

        plt.subplots_adjust(left=.6)
        plt.yticks(fontsize = 7)
        ax.set(xlabel='Disagree ↔ Agree', ylabel='')
        plt.tight_layout()
        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
        ax.figure.clf()

def p_self(data):
    '''
    Plot Self-assesments
    '''

    names = {'S103': "Usage of research software", 'S110': "Frequence of research code development", 'S202': 'Ownership of code', 'S113': "Time to train a new student", 'S204': "Community - Full text answer"} 
    
    #iterate questions of catergory and plot box for each
    for q in names.keys():
        d, cols = get_all_data(data, q)

        if q == "S204":
            #just write all the answers to one csv for further processing.
            d.to_csv("S204_answers.csv", index=False)
            continue

        res = get_full_response(data, q)
        d[q] = d[q].map(res)

        #reset figure size
        plt.figure(figsize=(5,4))
    

        # manual shorten some names -> too long to plot them properly
        if q == "S202":
            d.loc[d[q] == "No, all code belongs to the institution I work for"] = "Institute"
            d.loc[d[q] == "No, all code belongs to supervisor"] = "Supervisor"
            d.loc[d[q] == "Don't actually know"] = "I don't know"
            d.loc[d[q] == "Yes, all code belongs to me"] = "Me"


        '''
        Histplot does not support a categorial ordering.
        For some plots we might want to adjust the automatic ordering to make sense.
        Should be made more generic -> currently code repetition
        '''
        if q == "S103":
            t = pd.CategoricalDtype(categories=['Every day', 'Multiple times per week', 'Once a week', 'Once a month', 'Less than once a month', 'I do not use research software in my own research.'], ordered=True)
            d['sort'] = pd.Series(d[q], dtype=t)
            d.sort_values(by=['sort'],inplace=True)
        if q == "S110":
            t = pd.CategoricalDtype(categories=['Every day', 'Multiple times per week', 'Once a week', 'Once a month', 'Less than once a month', 'I used to develop software in the past but not anymore.', 'I do not work on code at all.'], ordered=True)
            d['sort'] = pd.Series(d[q], dtype=t)
            d.sort_values(by=['sort'],inplace=True)
        if q == "S113":
            t = pd.CategoricalDtype(categories=['1 day', '1 week', '2-4 weeks', 'up to a year', 'more than a year', 'Does not apply to me'], ordered=True)
            d['sort'] = pd.Series(d[q], dtype=t)
            d.sort_values(by=['sort'],inplace=True) 


        ax = sns.histplot(x=q, data=d, discrete=True, fill=False, stat="probability")
        sns.despine(trim=True, offset=2);
        plt.xticks(rotation=-45, fontsize = 8, ha="left", rotation_mode="anchor") 
        plt.subplots_adjust(bottom=.2)
       
        ax.set_xlabel(names[q])
        
        plt.tight_layout()
        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
        ax.figure.clf()

def p_self2(data):
    names = {'S111': "Which licences you use", 'S112': "Licences you know", 'S101': "What languages", 'S104': "Methods and concepts", 'S105': "Tools", 'S203': "What keeps you",'S106': "Learning"}

    def count_occur(data, string, what):
        return data.loc[data[string] == what][string].count()
    
    for q in names.keys():
        d, cols = get_all_data(data, q)
        
        if q == "S111":
            print("What licences do you use?")
            print(d["S111s"].unique())
            
        if q == "S112":
            print("Which of the licences are you familar with?")
            un = d['S112_08a'].unique()
            #FIXME currently this does not assess how often an alternative was mentioned
            print("Other licences mentioned: {}".format(un))
            print(d.mean())
            print("GNU is number 4")
            print("Total responses: {}".format(d["S112"].count()))
            counts = {"I dont know them": count_occur(d, "S112", -2), "Only by name": count_occur(d, "S112", -1)}
            print(counts)

        if q == "S101":
            print("What kind of programming languages do you mainly use?")
            un = d['S101_06a'].unique()
            #FIXME currently this does not assess how often an alternative was mentioned
            print("Other languages mentioned: {}".format(un))
            print(d.mean())
            print("03= Python, 04= R")
            print("Total responses: {}".format(d["S101"].count()))
            counts = {"None of the above": count_occur(d, "S101", -1)}
            print(counts)
        
        if q == "S104":
            print("What methods are you applying?")
            un = d['S104_09a'].unique()
            #FIXME currently this does not assess how often an alternative was mentioned
            print("Others mentioned: {}".format(un))
            print(d.mean())
            print("04 = Object oriented")
            print("Total responses: {}".format(d["S104"].count()))
            counts = {"None of the above": count_occur(d, "S104", -1)}
            print(counts)

        if q == "S105":
            print("What tools are you using?")
            un = d['S105_04a'].unique()
            #FIXME currently this does not assess how often an alternative was mentioned
            print("Others mentioned: {}".format(un))
            print(d.mean())
            print("01 = Version control")
            print("Total responses: {}".format(d["S105"].count()))
            counts = {"None of the above": count_occur(d, "S105", -1)}
            print(counts)

        if q == "S106":
            print("Where did you learn to programm?")
            print(d.mean())
            print("...")
            print("Total responses: {}".format(d["S106"].count()))
            counts = {"I'm not able to write my own code": count_occur(d, "S106", -1)}
            print(counts)

        if q == "S203":
            print("What keeps you from Open Source?")
            un = d['S203_06a'].unique()
            #FIXME currently this does not assess how often an alternative was mentioned
            print("Others mentioned: {}".format(un))

            print(d.mean())
            print("...")
            print("Total responses: {}".format(d["S203"].count()))
            counts = {"I publish all my code as open source": count_occur(d, "S203", -1), "I don't want to": count_occur(d, "S203", -2), "Does not apply to me": count_occur(d, "S203", -3)}
            print(counts)



def all():
    data = read_data()
    p_demo(data)
    p_opinion(data)
    p_self(data)
    p_self2(data)

#all()
