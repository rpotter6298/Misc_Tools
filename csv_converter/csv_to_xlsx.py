import pandas as pd
import glob

for csv in glob.glob('**.csv'):
    print (str(csv).split(".")[0])
    pd.read_csv(csv, delimiter=",").to_excel((str(csv).split(".")[0])+".xlsx")