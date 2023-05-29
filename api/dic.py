# Mecab이 제일 빠르긴 한데 로컬에서 설치하기 빡세니까 Okt 사용
from konlpy.tag import Okt
import pandas as pd
import os

# csv load
#df_department = cache.get('department_data.csv', encoding = 'utf-8') # 학과정보
#df_sju = cache.get('sju_data.csv', encoding = 'utf-8') # 세종대 정보
#df_curri = cache.get('curriculum_16_23.csv', encoding = 'utf-8') # 학번 별 커리큘럼

# csv load
df_department = pd.read_csv(os.getenv("SJU_DEPARTMENT_DATA_CSV_PATH"), encoding = 'utf-8') # 학과정보
df_sju = pd.read_csv(os.getenv("SJU_DATA_CSV_PATH"), encoding = 'utf-8') # 세종대 정보
df_curri = pd.read_csv(os.getenv("SJU_CURRICULUM_16_23_CSV_PATH"), encoding = 'utf-8') # 학번 별 커리큘럼
df_pf = pd.read_csv(os.getenv("SJU_PROFESSOR_DATA_CSV_PATH"), encoding = 'utf-8') # 교수진 정보


# 모델 embedding data load
#em_department = cache.get('department_data.pt')
#em_sju = cache.get('sju_data.pt')
#em_curri = cache.get('curriculum_16_23.pt')

import torch
# 모델 embedding data load
em_department = torch.load(os.getenv("SJU_DEPARTMENT_DATA_PATH"))
em_sju = torch.load(os.getenv("SJU_DATA_PATH"))
em_curri = torch.load(os.getenv("SJU_CURRICULUM_16_23_PATH"))
em_pf = torch.load(os.getenv("SJU_PROFESSOR_DATA_PATH"))

# sentence_transformers local 사용 제한으로 인한 유사도 선언
from numpy import dot
from numpy.linalg import norm

def cos_sim(A, B):
        return dot(A, B)/(norm(A)*norm(B))

depart_word_dic = df_department['intent'].values.tolist()
depart_word_dic = list(set(depart_word_dic))

query_word_dic = df_sju['intent'].values.tolist()
query_word_dic = list(set(query_word_dic))

curri_word_dic = df_curri['intent'].values.tolist()
curri_word_dic = list(set(curri_word_dic))

pf_word_dic = df_pf['intent'].values.tolist()
pf_word_dic = list(set(pf_word_dic))

## 단어사전 -> 사전 내에 질문지 해당내용 없을 경우 -> 일상대화 모델
import urllib.request
import pandas as pd
from konlpy.tag import Mecab
from nltk import FreqDist
import numpy as np
import matplotlib.pyplot as plt

# Univ_dict = query_word_dic + depart_word_dic + curri_word_dic
# 정답지에 있는 문장들 다 끌어와서 단어사전 구축
depart_ans_dic = df_department['answer'].values.tolist()
query_ans_dic = df_sju['answer'].values.tolist()
curri_ans_dic = df_curri['answer'].values.tolist()
pf_ans_dic = df_pf['answer'].values.tolist()

Univ_dict = depart_ans_dic + query_ans_dic + curri_ans_dic + pf_ans_dic
for i in range(len(Univ_dict)):
    Univ_dict[i] = str(Univ_dict[i]).replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")

# 불용어 정의
stopwords=['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']

tokenizer = Okt()
tokenized=[]

# 문장 토큰화 및 전처리
for sentence in Univ_dict:
    temp = tokenizer.nouns(sentence) # 토큰화
    temp = [word for word in temp if not word in stopwords] # 불용어 제거
    tokenized.append(temp)

vocab = FreqDist(np.hstack(tokenized))

#print('단어 집합의 크기 : {}'.format(len(vocab)))

dict(vocab)

# 한글자인 단어 제거
filtered_vocab = {key: value for key, value in vocab.items() if len(key) > 1}
sorted_dictionary = dict(sorted(filtered_vocab.items(), key=lambda x: x[1], reverse=True))
top_500_items = dict(list(sorted_dictionary.items())[:500])

#print('단어 집합의 크기 : {}'.format(len(top_500_items)))

# 단어사전 구축
Univ_dict_final = query_word_dic + depart_word_dic + curri_word_dic + pf_word_dic
Univ_dict_final += list(top_500_items)
len(Univ_dict_final)