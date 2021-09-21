import pandas as pd
import json
import os

def json2csv(path, save_path):
    df = pd.DataFrame()
    for file in os.listdir(path):  
        file_path = os.path.join(path, file)
        with open(file_path,'r',encoding='utf-8') as f:
            item = json.load(f)
            row = pd.DataFrame(item,index=[0])
            df = df.append(row,ignore_index=True)
    df = df.set_index('time')
    df.drop(['read','subcomments','comment_url','comment_id'],inplace=True,axis=1)
    df.to_csv(save_path)

df = json2csv('comment\\000983','00983.csv')
