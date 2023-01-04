import json
import urllib.request as re
from urllib.parse import quote
import bs4
import time
import pandas as pd

title_list = []
content_list = []
#%%
index = 0
# 找前i個page
animes=["鬼滅之刃","間諜家家酒","五等分的新娘","出租女友","進擊的巨人","咒術迴戰","無職轉生","Re從零開始的異世界生活"]
for i in range(50):
    index += 1
    #搜尋的電影名字
    search_name = "Re:0"
    #url = "https://www.ptt.cc/bbs/movie/search?page="+str(index)+"&q="+quote(search_name)
    url = "https://www.ptt.cc/bbs/C_Chat/search?page="+str(index)+"&q="+quote(search_name)
    request=re.Request(url,headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    })
    with re.urlopen(request) as response:
        time.sleep(0.05)
        #data = 整個頁面的html
        data=response.read()

    #找每篇文章的title
    data = bs4.BeautifulSoup(data, "html.parser")
    data = data.find_all('div',class_ = "title" )
    print("page=%d"%i)
    #data = title array
    for i in data:
        #如果文章!=被刪除 然後名字有雷(好雷 壞雷..)就點進去儲存內文
        if i.find('a')!=None:
            
#            if "實況" not in i.find("a").string:
#                continue
            print(i.find("a").string)
            #if i.find('a').string[1] == '雷' or i.find('a').string[2] == '雷':
            content_url = "https://www.ptt.cc"+i.find('a').get('href')
            content_request = re.Request(content_url,headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
            })
            #讀文章內文 
            with re.urlopen(content_request) as response:
                time.sleep(0.05)
                content_data=response.read()
            #把內文除了主要內容其他都刪掉(包括 --防雷--,※※※※,別人的回覆)
            content_data = bs4.BeautifulSoup(content_data, "html.parser")
            content_data = content_data.find('div', id = "main-container").text.split("--")[0]
            content_data = content_data.split("※")[0]
            content_data = content_data.split('\n')[2:]
            temp = []
            #在把內文檢查一遍, 有網址 空行 ~都不要放進內文
            for j in range(len(content_data)):
                if (content_data[j][:5]=="https") or (content_data[j]=="") or (content_data[j][0]=="~"):
                    continue
                else:
                    temp.append(content_data[j])
            #如果內文有東西就把標題跟內文一組放進list
            if temp:
                title_list.append(i.find('a').string)
                content_list.append(''.join(temp)+'。')
#再把list 存進.csv檔
#%%
df = pd.DataFrame(list(zip(title_list, content_list)), columns =['title', 'content']) 
df.to_csv("Re從零開始的異世界生活"+'.csv', encoding='UTF-8',index=False)

