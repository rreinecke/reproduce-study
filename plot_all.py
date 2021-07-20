import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
sl = os.path.sep
import mpl_toolkits.axisartist as axisartist

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
            t = pd.CategoricalDtype(categories=['Student (BA/MA)', 'PhD candidate', 'Postdoc', 'Group leader',
                'Associate professor', 'Full professor', 'Scientific staff', 'Other (scientific)', 'Other (non-scientific)'], ordered=True)
            date['sort'] = pd.Series(date[names[q]], dtype=t)
            date.sort_values(by=['sort'],inplace=True)

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
        ax = sns.histplot(x=names[q], data=date, discrete=True, fill=False, stat="count")

        sns.despine(trim=True, offset=2);
        plt.xticks(rotation=-45, fontsize = 8, ha="left", rotation_mode="anchor")
        plt.subplots_adjust(bottom=.3)
        ax.set_ylabel("N")

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
                            {' Most published science in my field is reproducible.': 'Most published science in my field is reproducible',
                             ' In general, reproducibility is a major problem in my field.': 'Reproducibility is a major problem in my field',
                             ' I believe that we are jeopardizing the trust in our results due to a lack of reproducibility.': 'A lack of reproducibility is jepoardizing the trust in our results',
                             ' My own scientific work is reproducible.': 'My own scientific work is reproducible',
                             ' I am able to comprehend research code of other researchers in my field.': 'I comprehend research code of others',
                             " I don't need to understand the code of other models; good documentation is sufficient for reproducibility.": 'For reproducibility it is not necessary to understand code;\n documentation is sufficient',
                             ' I would be able to teach practices and skills for reproducible science.': 'I can teach reproducible science skills and practices',
                             ' I would like to make my scientific work more reproducible, but I don?t have the resources.': "I lack of resources for own improvement on reproducibility",
                             " I would like to make my scientific work more reproducible, but I don't know how.": "I lack of knowledge for own improvment on reproducibilty",
                             ' I am able to write scientific code.': 'I am able to write scientific code',
                             ' I am able to write research code that is well structured and documented.': 'I am able to write well structured and documented code',
                             ' Description vs. implementation': 'Description of algorithm is equal \n to its code implementation'
                            }
            })

        # calculate the percentage of dont know answers (-1)
        valid_answers_n = df[df.value > 0].groupby('variable').count()
        dontknow_answers_n = df[df.value < 0].groupby('variable').count()
        answers_n_categories = pd.merge(valid_answers_n.value, dontknow_answers_n.value, how="outer",
                                        left_index=True, right_index=True).fillna(0)
        dont_know_ratio = answers_n_categories.value_y / answers_n_categories.value_x
        
        if q == "O103":
            df = df.replace({'variable': 
                {" because their workflow is poorly documented.": "Worflow is poorly documented",
                " because their code is poorly documented.": "Code is poorly documented",
                " because their code is too complex.": "Code is too complex",
                " because their input data is not openly available.": "Input data is not availble",
                " because the software/code is not openly available.": "Code is not available",
                " because the code is written in a language that I wasn?t taught/don?t usually use.": "Code is written \n in a language I don't know"
                }
                })


        if q == "O102": 
            plt.figure(figsize=(12,4))
            plt.yticks(fontsize = 8)
            df["Answer"] = df["value"].map({1:"Yes", 2:"No"})
            c = df["variable"].unique()
            for a in c:
                v = df[df["variable"] == a]["Answer"]
                print(v.value_counts())
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
            continue

        if q == "S201":
            d_tmp = df[df["variable"] == " Funding opportunities"]
            print("Mean of S201: {}".format(d_tmp[d_tmp.value > 0]["value"].mean()))
            df = df.replace({'variable':
                {
                    " University / institutional guidelines or best practices for reproducible research": "Institutional reproducibility guidelines",
                    " University / institutional guidelines or best practices for licensing and open source": "Institutional Open Source guidelines"
                }})


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
    #category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[1]-1)) 
    category_colors = sns.color_palette("RdYlGn", as_cmap=True)(np.linspace(0, 1, data.shape[1]-1))
    # add gray to the colors
    category_colors = np.vstack((category_colors, [0.91, 0.91, 0.91, 1.]))

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.invert_yaxis()
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=.9, label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'dimgrey'
        percents = widths / data_cum[:, -1]
        percentlabels = ['{:.0%}'.format(x) for x in percents]
        ax.bar_label(rects, labels=percentlabels, label_type='center', color=text_color, fontsize='smaller')

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1), loc='lower left', fontsize='small')
    
    ax.set_xlabel("N")
    sns.despine(trim=True, offset=2)
    plt.tight_layout()

    ax.spines['left'].set_visible(False)
    plt.tick_params(left=False)

    ax.figure.savefig(d_path + sl + q + ".png", dpi=200)
    ax.figure.clf()
    return fig, ax



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
            n = len(d)
            print("I develop software every day: {}%".format(d[d[q] == 'Every day'].count() / n * 100))
            print("I develop multiple times a week: {}%".format(d[d[q] == 'Multiple times per week'].count() / n * 100))
        if q == "S113":
            t = pd.CategoricalDtype(categories=['1 day', '1 week', '2-4 weeks', 'up to a year', 'more than a year', 'Does not apply to me'], ordered=True)
            d['sort'] = pd.Series(d[q], dtype=t)
            d.sort_values(by=['sort'],inplace=True)
            
            print("Time to train a student more than year: {}%".format(d[d[q] == 'more than a year'].count() / n * 100))
            print("Time to train a student up to a year: {}%".format(d[d[q] == 'up to a year'].count() / n * 100))


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

    '''
    !! Some of these questions contain multiple possible answers. Counts of total selected answers may add up to more than the number of participants!
    '''

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
                print("Percentage of none license usage: {}".format( df[df[q] == "None"]['val'] / len(d["S111s"]) * 100))

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
                

                n = len(d_counts)
                
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))

                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

                print("Percentage of people that know GNU: {}".format(df[df[q] == ' GNU General Public License (GPL)']['val'] / n * 100))
                print("Percentage of people that do not know any: {}".format(df[df[q] == "I don't know them at all"]['val'] / n * 100))
                print("Percentage of people that heard of them: {}".format(df[df[q] == "I have heard of them"]['val'] / n * 100))

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
                
                n = len(d_counts)
                
                d_counts.columns = [w.replace("Programming Languages:", "") for w in res.values()]
                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))

                ans.append("None of the above")
                val.append(count_occur(d, "S101", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

                print("Percentage of Python users: {}".format(df[df[q] == ' Python']['val'] / n * 100))
                print("Percentage of R users: {}".format(df[df[q] == ' R']['val'] / n * 100))
            
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
                

                n = len(d_counts)
                

                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("None of the above")
                val.append(count_occur(d, "S104", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

                print("Percentage of OO knowledge: {}".format(df[df[q] == ' Object-oriented programming']['val'] / n * 100))
                print("No knowledge at all: {}".format(df[df[q] == 'None of the above']['val'] / n * 100))
                print("Pair programming: {}".format(df[df[q] == ' Pair programming']['val'] / n * 100))
                print("Test-driven: {}".format(df[df[q] == ' Test-driven development']['val'] / n * 100))
                print("Automated tests: {}".format(df[df[q] == ' Automated Testing']['val'] / n * 100))

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
                

                n = len(d_counts)

                # iterate possible answers and print number selected
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                
                ans.append("None of the above")
                val.append(count_occur(d, "S105", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)

                print("Percentage of tools none : {}".format(df[df[q] == 'None of the above']['val'] / n * 100))
                print("Percentage of version control: {}".format(df[df[q] == ' Version control such as Git, SVC or similar']['val'] / n * 100))
                print("Percentage of autodocs: {}".format(df[df[q] == ' Automated documentation such as Docstrings or similar']['val'] / n * 100))

            if q == "S106":
                ans = []
                val = []
                # selected = 2, not selected = 1
                # S106 _01-06
                res = get_label(data, q, 6, " Training methods:")
                d_counts = d.drop(['S106'], axis=1)
                d_counts.columns = [w.replace("Training methods:", "") for w in res.values()]
                n = len(d_counts)
                # iterate possible answers and print number selected 
                for label in d_counts.columns:
                    ans.append(label)
                    val.append(count_occur(d_counts, label, 2))
                ans.append("I'm not able to write my own code")
                val.append(count_occur(d, "S106", -1))
                answers = {q: ans, 'val': val}
                df = pd.DataFrame(answers)
                print("Percentage of autodidacts: {}".format(df[df[q] == ' Self-taught /autodidact']['val'] / n * 100))

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
                
                n = len(d_counts)
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

                print("Percentage of funding as reason: {}".format(df[df[q] == ' Funding']['val'] / n * 100))
                print("Percentage of complexity as reason: {}".format(df[df[q] == ' Complexity (code too complex, not enough documentation)']['val'] / n * 100))
                print("Percentage of license as reason: {}".format(df[df[q] == ' Licence (too complex to understand which to pick or restricted by university/intitution)']['val'] / n * 100))
                print("Percentage of competition as reason: {}".format(df[df[q] == ' Competition (fear to lose lead on other groups)']['val'] / n * 100))
                print("Percentage other reasons: {}".format(df[df[q] == ' Other']['val'] / n * 100))
                print("Percentage of publish everything as OS: {}".format(df[df[q] == 'I publish all my code as open source']['val'] / n * 100))

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

#all()
