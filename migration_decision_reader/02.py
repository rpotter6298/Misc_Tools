import os
import pandas as pd
import re

#os.chdir("migration_decision_reader")
xlsx_files = [f for f in os.listdir('excel_outputs') if f[-4:] == 'xlsx']
df = pd.DataFrame()
for f in xlsx_files:
    df = pd.concat([df, (pd.read_excel("excel_outputs\\"+f, converters={'decision_no':str}))], ignore_index=True)
## Format Dataframe nice and remove any duplicates
#Ensure all decision numbers are int
df['decision_no'] = df['decision_no'].apply(lambda x: re.sub("[^0-9]", "",x)).astype(int)
### Manual Override
override = pd.read_excel('manual_override.xlsx').to_dict('records')
for n in override:
    df.loc[df['decision_no']==n['decision_no']]=[pd.Series(n)]
df = df.sort_values('date', ascending = False)
# Remove Duplicates
df = df.drop_duplicates()

def writeloop(df):
    name = 'full_collection'
    count_marker = int(0)
    fname = name
    while True:
        try:
            print(str("Writing to " + fname + ".xlsx"))
            df.to_excel(fname+'.xlsx', index=False)
            break
        except Exception as e:
            print(e)
            count_marker=count_marker+1
            fname = name+"_"+str(count_marker)
    print("File written to " + fname + ".xlsx")
    input("Press return to continue." )


writeloop(df)
