# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 10:59:17 2022

@author: user
"""

import pandas as pd
import re 
import regex
#%%
def txt_to_text(txt_path):
    f = open(txt_path, 'r',encoding='UTF-8')
    text=f.read()
    f.close()
    return text;
def text_eliminate_http(text):
    #results = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=:]*', re.S) 
    #text=re.sub(r'^https?:\/\/.*[\r\n]*', '',text, flags=re.MULTILINE)
    text=re.sub(r'http\S+', '', text)
    #text = re.sub(results,"",text )
    return text
def text_to_sentences(text):
    cur_str=""
    sentences=[]
    for  char in text:
        if char in ".。；\n":#indicate end
            if len(cur_str)>0:
                sentences.append(cur_str)
            cur_str=""
        elif char in "()「」（）":    #no meaning
            continue
        else:
            cur_str+=char
    return sentences
def remove_content_in_paranthese(text):
    ret=""
    i=0
    while i <len(text):
        if text[i] in "(（":
            i+=1
            while not(text[i] in")）"):
                i+=1
            while(text[i] in")）"): #to elimate double paranthese
                i+=1
            if i>= len(text):
                break
        ret+=text[i]
        i+=1
        
    return ret
def clear_small(sentences,threshold):
    tmp=[]
    for s in sentences:
        if len(s)<threshold:
            continue
        else :
            tmp.append(s)
    return tmp
def csv_to_data(path,label,d_http=True,d_parenthess=False,drop_list=None,d_small=6,max_size=500):
    df=pd.read_csv(path)
    if drop_list!=None:
        df=df.drop(index=drop_list)
        
    data=pd.DataFrame(columns=["sentence","label"])
    cur_series=df.iloc[:,1]
    
    for cur_text in cur_series:
        if d_http:
            cur_text=text_eliminate_http(cur_text)
        if d_parenthess:
            cur_text=remove_content_in_paranthese(cur_text)
        cur_sentences=text_to_sentences(cur_text)
        cur_sentences=clear_small(cur_sentences,d_small)
        cur_labels=[label]*len(cur_sentences)
        data_cur=pd.DataFrame({"sentence":cur_sentences,"label":cur_labels})
        data=data.append(data_cur,ignore_index=True)
    return data[:max_size]
#%%
data=pd.DataFrame(columns=["sentence","label"])
#series=["西方極樂園","絕命律師","怪奇物語","絕命毒師","獵魔士","黑鏡","魷魚遊戲","黑袍糾察隊"]
novels=["詭秘之主","驚悚樂園","大奉打更人","鬥破蒼穹","仙逆","琥珀之劍","全職高手","修真聊天群"]
#%%
data_train=pd.DataFrame(columns=["sentence","label"])
for novel in novels:
    cur_text=txt_to_text(novel+".txt")
    cur_sentences=text_to_sentences(cur_text)
    cur_sentences=clear_small(cur_sentences,6)
    cur_labels=[novel]*len(cur_sentences)
    data_cur=pd.DataFrame({"sentence":cur_sentences,"label":cur_labels})
    data_train=pd.concat([data_train,data_cur],ignore_index=True)
data_train.to_csv("novels8_data.csv", index=False)
#%%
print(data_train[15555:15565])
#%%
"""
#沙丘ptt
data_cur=csv_to_data("沙丘.csv", "沙丘")
data=data.append(data_cur,ignore_index=True)
#%%
data_cur=csv_to_data("返校.csv", "返校")
data=data.append(data_cur,ignore_index=True)
data_cur=csv_to_data("刻在你心底的名字.csv", "刻在你心底的名字")
data=data.append(data_cur,ignore_index=True)
data_cur=csv_to_data("一級玩家.csv", "一級玩家")
data=data.append(data_cur,ignore_index=True)
data_cur=csv_to_data("我的少女時代.csv", "我的少女時代")
data=data.append(data_cur,ignore_index=True)
data_cur=csv_to_data("天能.csv", "天能")
data=data.append(data_cur,ignore_index=True)
"""
for novel in novels:
    data_cur=csv_to_data(novel+".csv", novel)
    data=data.append(data_cur,ignore_index=True)
data.to_csv("novels8_val.csv", index=False)
