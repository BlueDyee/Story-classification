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
#series=["怪奇物語","絕命毒師","獵魔士","黑鏡","魷魚遊戲","西方極樂園","絕命律師","黑袍糾察隊"]
animes=["鬼滅之刃","間諜家家酒","五等分的新娘","出租女友","進擊的巨人","咒術迴戰","無職轉生","Re從零開始的異世界生活"]
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
for anime in animes:
    data_cur=csv_to_data(anime+".csv", anime)
    data=data.append(data_cur,ignore_index=True)
data.to_csv("animes8_data.csv", index=False)
#%%
#for val
import torch
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
# Initialize drivers
ner_driver = CkipNerChunker(model="bert-base") #細分專有名詞,(pos只會歸類成Nb)
ner_driver = CkipNerChunker(device=0)
#%%
total_dict={}
for anime in animes:
    cur_text=txt_to_text(anime+".txt")
    ner=ner_driver([cur_text])#[] is necessary
    
    #build dict
    PERSONS=[]
    for token in ner[0]:
        if token[1]=="PERSON":
            PERSONS.append(token[0])
    PERSONS=set(PERSONS)
    print(anime,":",PERSONS)
    first_list=[]
    second_list=[]
    replace_dict1={}
    replace_dict2={}
    replace_dict3={}
    cur=65
    for word in PERSONS:
        if len(word)==1:
            first_list.append(word)
            replace_dict1[word]=""
        else:
            second_list.append(word) 
            replace_dict2[word]="人物"+chr(cur)
            replace_dict3[word]="某人"
            cur+=1
    total_dict[anime]=(replace_dict1,replace_dict2,replace_dict3)
    torch.cuda.empty_cache()
#%%
#custom adjust
#total_dict["血觀音"][1].pop("玉珮")

#%%
"""
data_replace=pd.DataFrame(columns=["sentence","label"])
for sentence,label in zip(data["sentence"],data["label"]):
    for name,anony in total_dict[label][1].items(): #先換長字(姓+名or 名)再換短字(姓)
        sentence=sentence.replace(name,anony)
    for name,anony in total_dict[label][0].items():
        sentence=sentence.replace(name,anony)
    data_cur=pd.DataFrame({"sentence":sentence,"label":label},index=[0])
    #data_replace=data_replace.append(data_cur,ignore_index=True)
    data_replace=pd.concat([data_replace,data_cur],ignore_index=True)
data_replace.to_csv("series8_data_replace.csv", index=False)
"""
#%%
data_replace2=pd.DataFrame(columns=["sentence","label"])
for sentence,label in zip(data["sentence"],data["label"]):
    for name,anony in total_dict[label][2].items(): #先換長字(姓+名or 名)再換短字(姓)
        sentence=sentence.replace(name,anony)
    for name,anony in total_dict[label][0].items():
        sentence=sentence.replace(name,anony)
    data_cur=pd.DataFrame({"sentence":sentence,"label":label},index=[0])
    #data_replace=data_replace.append(data_cur,ignore_index=True)
    data_replace2=pd.concat([data_replace2,data_cur],ignore_index=True)
data_replace2.to_csv("animes8_data_replace2.csv", index=False)
#%%
val=pd.DataFrame(columns=["sentence","label"])
for anime in animes:
    cur_text=txt_to_text(anime+".txt")
    cur_sentences=text_to_sentences(cur_text)
    cur_sentences=clear_small(cur_sentences,6)
    cur_labels=[anime]*len(cur_sentences)
    data_cur=pd.DataFrame({"sentence":cur_sentences,"label":cur_labels})
    val=pd.concat([val,data_cur],ignore_index=True)
val.to_csv("animes8_val.csv", index=False)
#%%
val_replace=pd.DataFrame(columns=["sentence","label"])

for sentence,label in zip(val["sentence"],val["label"]):
    for name,anony in total_dict[label][1].items(): #先換長字(姓+名or 名)再換短字(姓)
        sentence=sentence.replace(name,anony)
    for name,anony in total_dict[label][0].items():
        sentence=sentence.replace(name,anony)
    data_cur=pd.DataFrame({"sentence":sentence,"label":label},index=[0])
    #total_data=total_data.append(data_cur,ignore_index=True)
    val_replace=pd.concat([val_replace,data_cur],ignore_index=True)
val_replace.to_csv("animes8_val_replace.csv", index=False)
#%%
total_data=pd.concat([data_replace2,val],ignore_index=True)
total_data.to_csv("animes8_total.csv", index=False)
#%%
"""
#augmen
data_augment=pd.DataFrame(columns=["sentence","label"])
for sentence,label in zip(data["sentence"],data["label"]):
    sentence1=sentence
    sentence2=sentence
    for name,anony in total_dict[label][2].items(): #先換長字(姓+名or 名)再換短字(姓)
        sentence2=sentence2.replace(name,anony)
    for name,anony in total_dict[label][1].items(): #先換長字(姓+名or 名)再換短字(姓)
        sentence1=sentence1.replace(name,anony)
    for name,anony in total_dict[label][0].items():
        sentence1=sentence1.replace(name,anony)
        sentence2=sentence2.replace(name,anony)
    data_cur=pd.DataFrame({"sentence":[sentence1,sentence2],"label":[label,label]})
    #data_replace=data_replace.append(data_cur,ignore_index=True)
    data_augment=pd.concat([data_augment,data_cur],ignore_index=True)
data_augment.to_csv("series8_data_augment.csv", index=False)
#%%
"""