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
d_path = "figs"

# Create a folder if it doesn't exist already
try:
    os.mkdir(d_path)
except OSError as error:
    pass

# We are reading some very long string but still want to display them fully in all plots
pd.set_option('display.max_colwidth', None) 


# String templates to parse them out of the data -> used to explain reproducibility in poll
explanation_s = "|We explicitly exclude the retracing of results by means of using a different modeling environment (including variations in model concept, algorithms, input data or methodology).))"
explanation_a_s = "|We explicitly exclude the retracing of results by means of using a different modeling environment (including variations in model concept, algorithms, input data or methodology).))"
expl_missing_s = "|TODO defintion.))" 
expl_soft_s = "|How the software is used, e.g., input format, configuration options, and example problems.))"


########### Helper methods ###################################

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

def get_all_data(data, q, withCase = False):
    '''
    Collects data from multiple field questions like O101
    '''
    
    date = data['data']
    # find out what fields exist
    col = date.columns.to_list()
    r = [i for i in col if q in i]
    
    # provide the case number as well
    if withCase:
        r.append('CASE')

    return date[r], r 

####################### Plotting #########################


def get_demo(data, q):
    '''
    Preprocessing for plotting demo data
    Also used to use prepared data in test framework
    '''

    #FIXME same dict as in plotting methode -> remove redundancy
    names = {'DM01':"Career stage",'DM02_01':"Years of experience",'DM05':"Scale", 'DM06':"Field of research",'DM07': "Main work task"}
    d = data['data'][names.keys()] # not very efficient -.-
    
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
        date[names[q]] = date[names[q]].str.replace("Field: ","")
    if q == "DM07":
        #FIXME index issue introdcues NAN values
        res = get_label(data, q, 5, " KindOfTask:")
        date[names[q]] = date[names[q]].map(res)
        # shorten answers -> too long to plot properly
        date.loc[date[names[q]] == "KindOfTasks: I conduct research that improves our process understanding by conducting field or lab experiments."] = "Field/Lab work"
        date.loc[date[names[q]] == "KindOfTasks: I conduct research by developing and using computational models."] = "Develop and apply models"
        date.loc[date[names[q]] == "KindOfTasks: I conduct research by applying computational models without building them myself."] = "Apply models"
        date.loc[date[names[q]] == "KindOfTasks: I develop computational models but do not conduct any research."] = "Develop models"
        # No answer for " KindOfTasks: I use results of models in my work (e.g., policy, consultation) but do not conduct any research myself."] = "Consulting" 
        # date.loc[date[names[q]] == " KindOfTasks: I use results of models in my work (e.g., policy, consultation) but do not conduct any research myself."] = "Consulting"
        date.dropna(inplace=True)

    if q == "DM05":
        '''
        Histplot does not support a categorial ordering.
        For some plots we might want to adjust the automatic ordering to make sense.
        '''
        t = pd.CategoricalDtype(categories=['Global', 'Continental', '< Million km²', '< 1000 km²', '< km²', '< m²', '< cm²', 'Mixed', 'Does not apply to me'], ordered=True)
        date['sort'] = pd.Series(date[names[q]], dtype=t)
        date.sort_values(by=['sort'],inplace=True)
     
    return date

def p_demo(data):
    '''
    Plot Demographics
    '''
    #03 was the defintion that was removed, 04 does not exist
    names = {'DM01':"Career stage",'DM02_01':"Years of experience",'DM05':"Scale", 'DM06':"Field of research",'DM07': "Main work task"}

    for q in names.keys():  
        date = get_demo(data,q)
        ax = sns.histplot(x=names[q], data=date, discrete=True, fill=False, stat="probability")

        sns.despine(trim=True, offset=2);
        plt.xticks(rotation=-45, fontsize = 8, ha="left", rotation_mode="anchor")
        plt.subplots_adjust(bottom=.3)
        ax.set_ylabel("%")

        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
        ax.figure.clf()


def get_opinion(data, q, withCase = False):
    '''
    Prepare the data for the opinion plots.
    Also used in the test framework to get the same "clean" data
    '''
    d, cols = get_all_data(data, q, withCase)

    # frame with O101_01 etc. as col and data as row
    if withCase:
        del cols[2]
        df = pd.melt(d, id_vars=['CASE'], value_vars=cols)
    else:
        d.reset_index(level=0, inplace=True)
        df = pd.melt(d, id_vars=['index'], value_vars=cols)

    res = get_label_by_names(data, cols, [" Opinion:", "reasons:", "Reproduce?:", "Helpful Suggestions:", "((", explanation_s, explanation_a_s, expl_missing_s, expl_soft_s])
    df["variable"] = df["variable"].map(res)

    if q == "O101":
        df["variable"] = df["variable"].str.replace("Opinion:","") 
        df["variable"] = df["variable"].str.replace("Implementing an algorithm based on a description from a publication yourself is the same as using the exact software package/original code that was used in that very publication.", "Description vs. implementation")
    if q == "S201":
        df["variable"] = df["variable"].str.replace("Funding opportunities dedicated to reproduciblity  \|For example for a trained programmer to develop reuseable code and workflows.\)\)", "Funding opportunities")
        df["variable"] = df["variable"].str.replace("Reduce the complexity of code  \|For example through the application of established software engeneering concepts and a general improved code quality.\)\)", "Reduction of code complexity")
    return df


def p_opinion(data):
    '''
    Plot Opinions
    '''

    names = {'O101':"Agreement",'O102':"Reproduce?",'O103':"Reasons", 'S201': "Actions"}   
    
    #iterate questions of catergory and plot box for each
    for q in names.keys():
        df = get_opinion(data,q)

        # Figure O101 labels cleaning
        if q == 'O101':
            df = df.replace({'variable':
                            {' Most published science in my field is reproducible.': 'Published science is reproducible',
                             ' In general, reproducibility is a major problem in my field.': 'Reproducibility is a major problem',
                             ' I believe that we are jeopardizing the trust in our results due to a lack of reproducibility.': 'Lack of reproducibility is jepoardizing trust in results',
                             ' My own scientific work is reproducible.': 'My own scientific work is reproducible',
                             ' I am able to comprehend research code of other researchers in my field.': 'I comprehend research code of others',
                             " I don't need to understand the code of other models; good documentation is sufficient for reproducibility.": 'No need for code understanding; documentation is sufficient',
                             ' I would be able to teach practices and skills for reproducible science.': 'I can teach reproducible science skills and practices',
                             ' I would like to make my scientific work more reproducible, but I don?t have the resources.': "Lack of resources for own improvement on reproducibility",
                             " I would like to make my scientific work more reproducible, but I don't know how.": "Lack of knowledge for own improvment on reproducibilty",
                             ' I am able to write scientific code.': 'I am able to write scientific code',
                             ' I am able to write research code that is well structured and documented.': 'I am able to write well structured documented code',
                             ' Description vs. implementation': 'Description of algorithm equal an implementation'
                            }
            })

        # calculate the percentage of dont know answers (-1)
        valid_answers_n = df[df.value > 0].groupby('variable').count()
        dontknow_answers_n = df[df.value < 0].groupby('variable').count()
        answers_n_categories = pd.merge(valid_answers_n.value, dontknow_answers_n.value, how="outer",
                                        left_index=True, right_index=True).fillna(0)
        dont_know_ratio = answers_n_categories.value_y / answers_n_categories.value_x
        
        if q == "O102": 
            plt.figure(figsize=(12,4))
            plt.yticks(fontsize = 8)
            df["Answer"] = df["value"].map({1:"Yes", 2:"No"})
            ax = sns.histplot(y="variable", hue="Answer", data=df, discrete=True, multiple="stack", shrink=.8, linewidth=.8)
            plt.subplots_adjust(left=.5)
            ax.set(ylabel='')
            ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
            ax.figure.clf()

            # Produce an additonal plot that relates answers to fields
            # 1) get the data on fields - CASE is the person that answered the poll
            df_fields = data["data"][['CASE','DM06']]
            res = get_label(data, 'DM06', 11, " Field:")
            df_fields['DM06'] = df_fields['DM06'].map(res)
            df_fields['DM06'] = df_fields['DM06'].str.replace("Field: ","")
            # 2) get O102 with CASE for join
            df = get_opinion(data, q, withCase = True)
            df = df.merge(df_fields, on='CASE')

            #df.groupby('DM06').
            # We need to build our own bar plot here ... no lib supports this properly
            #bar_width = 0.35
            #epsilon = .015
            #line_width = 1
            #opacity = 0.7
            #bar_one_pos = np.arange(len(df['DM06'].unique()))
            #bar_two_pos = bar_one_pos + bar_width

            
            #bar1 = plt.bar(pos_bar_positions, pos_mut_pcts, bar_width,
            #                          color='#ED0020',
            #                          label='HPV+ Mutations')
            #bar2 = plt.bar(pos_bar_positions, pos_cna_pcts, bar_width-epsilon,
            #                          bottom=bar1,
            #                          alpha=opacity,
            #                          color='white',
            #                          edgecolor='#ED0020',
            #                          linewidth=line_width,
            #                          hatch='//',
            #                          label='HPV+ CNA')
            
            #plt.legend(bbox_to_anchor=(1.1, 1.05))  
            #sns.despine()  
            #plt.show()  


            #ax.figure.savefig(d_path + sl + q + '_1' + ".png", dpi=200)
            #ax.figure.clf()
            #exit()
                
            continue

        if q == "S201":
            d_tmp = df[df["variable"] == " Funding opportunities"]
            print("Mean of S201: {}".format(d_tmp[d_tmp.value > 0]["value"].mean()))

        catcounts = df.groupby(['variable', 'value']).count()
        results = {x: [0, 0, 0, 0, 0, 0, 0] for x in df.variable.unique()}
        for ix, value in catcounts.iterrows():
            if ix[1] == -1:
                cat_ix = 6
            else:
                cat_ix = ix[1] -1
            results[ix[0]][cat_ix] = value[0]
        survey(results, q)
        '''ax = sns.boxplot(y="variable", x="value", data=df[df.value > 0], orient="h")

        plt.subplots_adjust(left=.6)
        plt.yticks(fontsize=7)
        ax.set(xlabel='Disagree ↔ Agree', ylabel='')
        ax.set_xticks([-1, 0, 1, 2, 3, 4, 5, 6])
        ax.set_xticklabels(["", "I don't know", "1", "2", "3", "4", "5", "6"])
        # Plot the don't know percentages
        for x in [x.label for x in ax.yaxis.get_major_ticks()]:
            ax.text(0, x.get_position()[1], '{:.1%}'.format(dont_know_ratio[x.get_text()]),
                    ha='center', va='center')
        plt.tight_layout()
        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
        ax.figure.clf()'''

def survey(results, q, category_names=['strongly disagree', 'disagree', 'rather disagree',
                                       'rather agree', 'agree', 'strongly agree', 'dont know']):
    """
    Function taken and modified from https://matplotlib.org/stable/gallery/lines_bars_and_markers/
    horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py

    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    # make disagree negative
    data_cum = (data_cum.transpose() - data_cum[:,2]).transpose()
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[1]-1))
    category_colors = np.vstack((category_colors, [0.91, 0.91, 0.91, 1.]))

    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.invert_yaxis()
    ax1.xaxis.set_visible(False)
    ax1.set_xlim((data_cum[:, 0]- data[:,0 ]).min() - 10, (data_cum[:, -2] + data[:, -1]).max() + 30)

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        # move dont know to right corner
        if i == 6:
            starts = data_cum[:, -2].max() + 20
        height = 0.85
        if q == 'S201':
            height = 0.5
        rects = ax1.barh(labels, widths, left=starts, height=height, label=colname, color=color)

        r, g, b, _ = color
        text_color = 'dimgray'
        #text_color = 'white' if r * g * b < 0.5 else 'dimgray'
        percents = widths / data.sum(axis=1)
        #percentlabels = ['{:.0%}'.format(x) if x >= 0.03 else '' for x in percents]
        percentlabels = ['{:.0%}'.format(x) for x in percents]
        ax1.bar_label(rects, labels=percentlabels, label_type='center', color=text_color, fontsize='smaller')
    
    ax1.legend(ncol=len(category_names), bbox_to_anchor=(0, 1), loc='lower left', fontsize='small')

    #ax1.set_xlabel("N")
    sns.despine(trim=True, offset=2)
    ax1.spines['left'].set_visible(False)
    plt.tick_params(left=False)

    plt.tight_layout()
    ax1.figure.savefig(d_path + sl + q + ".png", dpi=500)
    # ax.figure.clf()
    return fig, ax1



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
        ax.set_ylabel("%")

        plt.tight_layout()
        ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
        ax.figure.clf()

def p_self2(data):
    names = {'S111': "Which licences you use", 'S112': "Licences you know", 'S101': "What languages", 'S104': "Methods and concepts", 'S105': "Tools", 'S203': "What keeps you",'S106': "Learning"}

    def count_occur(data, string, what):
        return data.loc[data[string] == what][string].count()
    
    with open('report/self.tex', 'w+') as f:
        for q in names.keys():
            d, cols = get_all_data(data, q)
        
            if q == "S111":
                f.write("\\textbf{S111}\n")
                f.write("\n")
                #FIXME This could be accieved much more nicely!! with pandas + generic method.. but due to time contrains it is now ugly and repetative for all the following answers sorry! :/
                answers = {q: ["Answer provided", "None", "Don't know"], 'val': [d[d["S111s"] != "none"]['S111s'].count(), count_occur(d,"S111s","none"),  count_occur(d,"S111","-1")]}
                df = pd.DataFrame(answers)
                f.write("What software licences do you use? Results: {} \n".format(d["S111s"].unique()))

            if q == "S112":
                f.write("\\textbf{S112}\n")
                f.write("\n")
                f.write("Which of the licences are you familar with?\n")
                f.write("\n") 
                f.write("Other licences mentioned: {}\n".format(d['S112_08a'].unique()))
                # Currently this does not assess how often an alternative was mentioned
               
                ans = ["I don't know them at all", "I have heard of them"]
                val = [count_occur(d, "S112", -2),  count_occur(d, "S112", -1)]
                
                # selected = 2, not selected = 1
                # S112 _01-08
                res = get_label(data, q, 8, " Licence2:")
                d_counts = d.drop(['S112','S112_08a'], axis=1)
                d_counts.columns = [w.replace("Licence2:", "") for w in res.values()]
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))

                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

            if q == "S101":
                f.write("\\textbf{S101}\n")
                f.write("\n")
                f.write("What kind of programming languages do you mainly use? \n")
                
                f.write("\n")
                #Currently this does not assess how often an alternative was mentioned
                un = d['S101_06a'].unique() # somebody used a & -.- -- bad for latex
                un = un[1:]
                un = [w.replace("&", "and") for w in un]
                f.write("Other languages mentioned: {}\n".format(un))
                
                ans = []
                val = []
                
                # selected = 2, not selected = 1
                # S101 _01-06
                res = get_label(data, q, 6, " Programming Languages:")
                del res[5] # does not exist
                d_counts = d.drop(['S101','S101_06a'], axis=1)
                d_counts.columns = [w.replace("Programming Languages:", "") for w in res.values()]
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))

                ans.append("None of the above")
                val.append(count_occur(d, "S101", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)
            
            if q == "S104":
                f.write("\\textbf{S104}\n")
                f.write("\n")
                f.write("What methods are you applying?\n")
                #Currently this does not assess how often an alternative was mentioned
                f.write("\n")
                f.write("Others mentioned: {}\n".format(d['S104_09a'].unique()))
                
                ans = []
                val = []
                
                # selected = 2, not selected = 1
                # S104 _01-09
                res = get_label(data, q, 9, " Software Development Methods:")
                del res[6] # does not exist
                d_counts = d.drop(['S104','S104_09a'], axis=1)
                d_counts.columns = [w.replace("Software Development Methods:", "") for w in res.values()]
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("None of the above")
                val.append(count_occur(d, "S104", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

            if q == "S105":
                f.write("\\textbf{S105}\n")
                f.write("\n")

                f.write("What tools are you using?\n")
                f.write("\n")
                #Currently this does not assess how often an alternative was mentioned
                f.write("Others mentioned: {}".format(d['S105_04a'].unique()))
                
                ans = []
                val = []
                
                # selected = 2, not selected = 1
                # S105 _01-04
                res = get_label(data, q, 4, " Software Development Tools:")
                d_counts = d.drop(['S105','S105_04a'], axis=1)
                d_counts.columns = [w.replace("Software Development Tools:", "") for w in res.values()]
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("None of the above")
                val.append(count_occur(d, "S105", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

            if q == "S106":
                ans = []
                val = []
                # selected = 2, not selected = 1
                # S106 _01-06
                res = get_label(data, q, 6, " Training methods:")
                d_counts = d.drop(['S106'], axis=1)
                d_counts.columns = [w.replace("Training methods:", "") for w in res.values()]
                # iterate possible answers and print number selected 
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("I'm not able to write my own code")
                val.append(count_occur(d, "S106", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

            if q == "S203":
                f.write("\\textbf{S203}\n")
                f.write("\n")

                f.write("What keeps you from publishing as Open Source?\n\n")
                #Currently this does not assess how often an alternative was mentioned

                f.write("Other reasons mentioned: {}\n\n".format(d['S203_06a'].unique()))
                
                ans = []
                val = []

                # selected = 2, not selected = 1
                # S203 _01-08
                res = get_label(data, q, 9, " Hurdles:")
                del res[9]
                d_counts = d.drop(['S203','S203_06a'], axis=1)
                d_counts.columns = [w.replace("Hurdles:", "") for w in res.values()]
                # iterate possible answers and print number selected 
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("I publish all my code as open source")
                val.append(count_occur(d, "S203", -1))
                ans.append("I don't want to")
                val.append(count_occur(d, "S203", -2))
                ans.append("Does not apply to me")
                val.append(count_occur(d, "S203", -3))
                
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)


            ax = df.plot.bar(x=q, y='val', legend=False)
            plt.xticks(rotation=-45, fontsize = 8, ha="left", rotation_mode="anchor") 
            plt.subplots_adjust(bottom=.2)
            ax.set_ylabel("Count")

            plt.tight_layout()
            ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
            ax.figure.clf()


def all():
    data = read_data()
    p_demo(data)
    p_opinion(data)
    p_self(data)
    p_self2(data)

all()
