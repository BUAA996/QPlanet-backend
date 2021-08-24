import chardet
import codecs
import jieba
import wordcloud
from QPlanet.settings import *
import random
import string

def word_count(s):
	txtlist = jieba.lcut(s)
	dic = {}
	for word in txtlist:
		if len(word)>1 and word not in STOPWORDS:
			dic[word] = dic.get(word, 0) + 1
	
	items = list(dic.items())
	items.sort(key=lambda x: x[1], reverse=True)
	word = []
	count = []
	for i in range(min(10, len(items))):
		word.append(items[i][0])
		count.append(items[i][1])
	return word,count

def draw_wordcloud(s):
	w = wordcloud.WordCloud(width=1000,
                        height=700,
                        background_color='white',
						stopwords=STOPWORDS)
	txtlist = jieba.lcut(s)
	ss = " ".join(txtlist)
	w.generate(ss)

	name = ''.join(random.sample(string.ascii_letters + string.digits, 12))
	w.to_file('img/'+name+'.png')
	return IMG_URL+'img/'+name+'.png'