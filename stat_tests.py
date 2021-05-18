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
        f.write("Mean agreement to reproducibility {}\n".format(rep['O101_01'].mean()))
        
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
        f.write("No statistical test possible much to less Prof. to do a proper Wilcoxon or even t-test\n")

def run_all():
    data = pa.read_data()
    h4(data)


#run_all()
