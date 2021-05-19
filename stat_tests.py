import pandas as pd
import plot_all as pa
from scipy import stats

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
       
    with open('h4.tex', 'w+') as f:
        f.write("Established researchers {}".format(ids_old.size))
        
        f.write("\n")
        f.write("Young researchers {}".format(ids_y.size))
        
        f.write("\n")
        f.write("Mean agreement to reproducibility without don't know {}\n".format(rep['O101_01'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among Y {}\n".format(r_y['O101_01'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among O {}\n".format(r_o['O101_01'].mean()))
        
        f.write("\n")
        f.write("Median agreement to reproducibility {}\n".format(rep['O101_01'].median()))
        
        f.write("\n")
        f.write("Median agreement among Y {}\n".format(r_y['O101_01'].median()))
 
        f.write("\n")
        f.write("Median agreement among O {}\n".format(r_o['O101_01'].median()))
        if p < alpha:
            f.write("Career has no normal distribution\n")
        else:
            f.write("Career is possibly normaly distributed\n") 
        f.write("\n")
        f.write("No statistical test possible, samples of Prof. to low to do a proper Wilcoxon or even t-test\n")

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

    with open('h5.tex', 'w+') as f:
        f.write("\n")
        f.write("!Inlcude don't know Mean workflow: {}, code documentation : {}, code complexity: {}, input data not available: {}, code availability: {}, written language: {}\n".format(df['O103_01'].mean(),df['O103_02'].mean(),df['O103_03'].mean(),df['O103_04'].mean(),df['O103_05'].mean(),df['O103_06'].mean()))
        
        f.write("\n") 
        f.write("Main reason: Input data. 2: code availability, 3: workflow, 4: documentation, 5: complexity\n")

        f.write("\n")
        f.write("Mean agreement code complexity without don't know {}\n".format(rep['O103_03'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among Y {}\n".format(r_y['O103_03'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among O {}\n".format(r_o['O103_03'].mean()))
        
        f.write("\n")
        f.write("Median agreement {}\n".format(rep['O103_03'].median()))
        
        f.write("\n")
        f.write("Median agreement among Y {}\n".format(r_y['O103_03'].median()))
 
        f.write("\n")
        f.write("Median agreement among O {}\n".format(r_o['O103_03'].median()))


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

    with open('h14.tex', 'w+') as f:
        f.write("\n")
        f.write("Mean agreement my own research is reproducible {}\n".format(rep['O101_03'].mean()))
        
        f.write("\n")
        f.write("Mean agreement among Y {}\n".format(r_y['O101_03'].mean()))
        
        f.write("\n")        
        f.write("Mean agreement among O {}\n".format(r_o['O101_03'].mean()))
        
        f.write("\n")
        f.write("Median agreement {}\n".format(rep['O101_03'].median()))
        
        f.write("\n")
        f.write("Median agreement among Y {}\n".format(r_y['O101_03'].median()))
 
        f.write("\n")
        f.write("Median agreement among O {}\n".format(r_o['O101_03'].median()))

def h16(data):
    '''
    Description vs implementation
    '''
    df = data["data"]
    with open('h16.tex', 'w+') as f:
        f.write("\n")
        f.write("Mean agreement description is same as implementation (including don't know) {}\n".format(df['O101_17'].mean())) 

def run_all():
    data = pa.read_data()
    h4(data)
    h5(data)
    h14(data)
    h16(data)

run_all()
