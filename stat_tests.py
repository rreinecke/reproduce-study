import pandas as pd
import plot_all as pa
from scipy import stats

def getWithout(key, df):
        # get means without don't know
        return df[df[key] > 0][key].mean()

def h2(data):
    '''
    Are younger scientists more familiar with software licences?
    '''
    df = data["data"]
    # Testing with years of experience
    ids_old = df[df['DM02_01'] > 20]['CASE']
    ids_y = df[df['DM02_01'] <= 20]['CASE']
    
    lic = df[['CASE','S112']]
    lic = lic[lic['S112'] < 0] # get only don't know also counting only heard of
    r_y = lic.merge(ids_y, on='CASE', how='right')
    r_o = lic.merge(ids_old, on='CASE', how='right')
    
    with open('report/h2.tex', 'w+') as f:
        f.write("Younger = less than 20 years of experience. \n\n")
        f.write("Number of younger researchers which do not know about licences: {}\n\n".format(r_y["S112"].count()))
        f.write("Number of established researchers which do not know about licences: {}\n\n".format(r_o["S112"].count()))

def h3(data):
    '''
    Are younger scientists more familiar with methods?
    '''
    df = data["data"]
    # Testing with years of experience
    ids_old = df[df['DM02_01'] > 20]['CASE']
    ids_y = df[df['DM02_01'] <= 20]['CASE']
    
    lic = df[['CASE','S104']]
    lic = lic[lic['S104'] < 0] # get only don't know also counting only heard of
    r_y = lic.merge(ids_y, on='CASE', how='right')
    r_o = lic.merge(ids_old, on='CASE', how='right')
    
    with open('report/h3.tex', 'w+') as f:
        f.write("Younger = less than 20 years of experience. \n\n")
        f.write("Number of younger researchers which do not know about methods: {}\n\n".format(r_y["S104"].count()))
        f.write("Number of established researchers which do not know about methods: {}\n\n".format(r_o["S104"].count()))


def h4(data):
    '''
    On reproducibility
    Do early career researcher differ from senior researchers in their agreement?
    '''
    #Get data on O101 + Career stage
    df = data["data"]
    # CASE = Id of person taking the poll
    # DM01 = career stage, 1-7
    #6	Student (undergraduate, Bachelor/Master or similar)
    #1	Scientific staff
    #2	PhD candidate
    #3	Postdoc
    #4	Group leader / junior professor
    #9	Associate professor
    #5	Full professor
    #7	Other (scientific)
    #8	Other (non-scientific)
   
    # TODO we could also use the experience in their field as indicator
    # Young researchers = 6, 2, 3, 4, 9
    # vs. 5
    ids_old = df[df['DM01'] == 5]['CASE']
    ids_y = df[df['DM01'].isin([6,2,3,4,9])]['CASE']
    
    # O101 _XX, -1 - 6 = Agreement 
    # 1 = strong disagree
    # 6 = strong agree

    rep = df[['CASE','O101_01']]
    rep = rep[rep['O101_01'] >0] # remove don't know
    r_y = rep.merge(ids_y, on='CASE', how='right')
    r_o = rep.merge(ids_old, on='CASE', how='right')
    
    # Testing if the population in field is normal distributed
    k2, p = stats.normaltest(df['DM01'].to_numpy())
    alpha = 1e-3
       
    with open('report/h4.tex', 'w+') as f:
        f.write("Number of established (full Prof.) researchers: {}\n".format(ids_old.size))
        
        f.write("\n")
        f.write("Number of young (Students, PhD candidates, Postdocs, Junior Prof., Associate Prof.) researchers: {}\n".format(ids_y.size))
        
        f.write("\n")
        f.write("Mean agreement to reproducibility: {:2f}\n".format(rep['O101_01'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among young sc.: {:2f}\n".format(r_y['O101_01'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among established sc.: {:2f}\n".format(r_o['O101_01'].mean()))
        
        f.write("\n")
        f.write("Median agreement to reproducibility: {:2f}\n".format(rep['O101_01'].median()))
        
        f.write("\n")
        f.write("Median agreement among young sc.: {:2f}\n".format(r_y['O101_01'].median()))
 
        f.write("\n")
        f.write("Median agreement among established sc.: {:2f}\n".format(r_o['O101_01'].median()))
        if p < alpha:
            f.write("Career has no normal distribution\n")
        else:
            f.write("Career is possibly normaly distributed\n") 
        f.write("\n")
        f.write("No statistical test possible, samples of to low to do a proper Wilcoxon or even t-test\n")

def h5(data):
    '''
    Software has gotten so complex that senior researchers are not able to comprehend it anymore.
    '''
    df = data["data"]
    # CASE = Id of person taking the poll
    # DM01 = career stage, 1-7
    #6	Student (undergraduate, Bachelor/Master or similar)
    #1	Scientific staff
    #2	PhD candidate
    #3	Postdoc
    #4	Group leader / junior professor
    #9	Associate professor
    #5	Full professor
    #7	Other (scientific)
    #8	Other (non-scientific)
    
    # Young researchers = 6, 2, 3, 4, 9
    # vs. 5
    ids_old = df[df['DM01'] == 5]['CASE']
    ids_y = df[df['DM01'].isin([6,2,3,4,9])]['CASE']
    
    # O103 _XX, -1 - 6 = Agreement 
    # 1 = strong disagree
    # 6 = strong agree

    rep = df[['CASE','O103_03']]
    rep = rep[rep['O103_03'] >0] # remove don't know
    r_y = rep.merge(ids_y, on='CASE', how='right')
    r_o = rep.merge(ids_old, on='CASE', how='right')

   

    with open('report/h5.tex', 'w+') as f:
        f.write("\n")
        f.write("All answers (without don't know) -  Mean workflow: {:2f}, code documentation : {:2f}, code complexity: {:2f}, input data not available: {:2f}, code availability: {:2f}, written language: {:2f}\n".format(getWithout('O103_01',df), getWithout('O103_02',df), getWithout('O103_03',df), getWithout('O103_04',df), getWithout('O103_05',df), getWithout('O103_06',df)))
        
        f.write("\n")
        f.write("Thus, the main reason for a lack of reproducibility is: Input data, then 2: code availability, 3: documentation, 4: workflow, 5: code complexity, 6: language\n")

        f.write("\n")
        f.write("Mean agreement code complexity {:2f}\n".format(rep['O103_03'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among young sc.: {:2f}\n".format(r_y['O103_03'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among established sc.: {:2f}\n".format(r_o['O103_03'].mean()))
        
        f.write("\n")
        f.write("Median agreement: {:2f}\n".format(rep['O103_03'].median()))
        
        f.write("\n")
        f.write("Median agreement among young sc.: {:2f}\n".format(r_y['O103_03'].median()))
 
        f.write("\n")
        f.write("Median agreement established sc: {:2f}\n".format(r_o['O103_03'].median()))


def h14(data):
    '''
    Seniors are more sure about their reproducibility
    '''
    df = data["data"]
    # CASE = Id of person taking the poll
    # DM01 = career stage, 1-7
    #6	Student (undergraduate, Bachelor/Master or similar)
    #1	Scientific staff
    #2	PhD candidate
    #3	Postdoc
    #4	Group leader / junior professor
    #9	Associate professor
    #5	Full professor
    #7	Other (scientific)
    #8	Other (non-scientific)
    
    # Young researchers = 6, 2, 3, 4, 9
    # vs. 5
    ids_old = df[df['DM01'] == 5]['CASE']
    ids_y = df[df['DM01'].isin([6,2,3,4,9])]['CASE']
    
    # O103 _XX, -1 - 6 = Agreement 
    # 1 = strong disagree
    # 6 = strong agree

    rep = df[['CASE','O101_03']]
    rep = rep[rep['O101_03'] >0] # remove don't know
    r_y = rep.merge(ids_y, on='CASE', how='right')
    r_o = rep.merge(ids_old, on='CASE', how='right')

    with open('report/h14.tex', 'w+') as f:
        f.write("\n")
        f.write("Mean agreement on: my own research is reproducible: {:2f}\n".format(rep['O101_03'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among young sc.: {:2f}\n".format(r_y['O101_03'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among estbalished sc: {:2f}\n".format(r_o['O101_03'].mean()))
        
        f.write("\n")
        f.write("Median agreement: {:2f}\n".format(rep['O101_03'].median()))
        
        f.write("\n")
        f.write("Median agreement among young sc: {:2f}\n".format(r_y['O101_03'].median()))
 
        f.write("\n")
        f.write("Median agreement among established sc.: {:2f}\n".format(r_o['O101_03'].median()))

def h16(data):
    '''
    Description vs implementation
    '''
    df = data["data"]
    with open('report/h16.tex', 'w+') as f:
        f.write("\n")
        f.write("Mean agreement - description is same as implementation: {:2f}\n".format(getWithout('O101_17',df))) 

def own_vs_other(data):
    df = data['data']
    rep1 = df[df['O101_03'] > 0]['O101_03'] # my own research
    rep2 = df[df['O101_01'] > 0]['O101_01'] # other research
    print("Are the distributions of most is reproducible and mine is reproducible the same?")
    print(stats.ks_2samp(rep1, rep2))
    print(stats.ttest_ind(rep1, rep2, equal_var=False)) # Welche's ttest


def run_all():
    data = pa.read_data()
    h2(data)
    h3(data)
    h4(data)
    h5(data)
    h14(data)
    h16(data)
    own_vs_other(data)

#run_all()
