#from api import cache
import numpy as np
import torch
import pandas as pd
from api import dic
from api import talk
import pickle
import os

with open(os.getenv('MODEL_PATH'), 'rb') as f:
    model = pickle.load(f)

#serving 
def get_prediction(uid, msg, major):
    # user 정보
    # 정보 얻는 방식은 sju data + 자기 해당 학과 정보만 저장해서 임베딩
    user_id = uid
    user_depart = major

    '''
    df_department = cache.get('department_data.csv')
    em_department = cache.get('department_data.pt')
    
    df_curri = cache.get('curriculum_16_23.csv')
    em_curri = cache.get('curriculum_16_23.pt')

    df_sju = cache.get('sju_data.csv')
    em_sju = cache.get('sju_data.pt')
    '''
   
    # 해당학과 질문지 추출
    user_DQ = dic.df_department[dic.df_department['intent'] == user_depart]
    # 해당학과 질문지 index 값 추출
    user_DQ_idx = dic.df_department.loc[dic.df_department['intent'] == user_depart].index
    user_depart_embed = dic.em_department[user_DQ_idx]

    # 해당 학번 커리큘럼 추출
    user_curri = dic.df_curri[dic.df_curri['intent']==user_id]
    # 해당 학번 커리큘럼 질문지 index 값 추출
    user_curri_idx = dic.df_curri.loc[dic.df_curri['intent'] == user_id].index
    user_curri_embed = dic.em_curri[user_curri_idx]

    # 세 데이터프레임 합치기
    concat_sju = pd.concat([dic.df_sju,user_DQ,user_curri])

    #print('sju_data length',len(dic.df_sju),'user department length',len(user_DQ),'user id curri',len(user_curri))
    #print('concat sju length',len(concat_sju))

    em_sju_list = dic.em_sju.tolist()
    user_depart_embed_list = user_depart_embed.tolist()
    user_curri_embed_list = user_curri_embed.tolist()
    concat_sju_embed = em_sju_list + user_depart_embed_list + user_curri_embed_list
    #print('sju_data embed length',len(em_sju_list),'user department embed length',len(user_depart_embed_list),'user curri embed list',len(user_curri_embed_list))
    #print('concat sju embed length',len(concat_sju_embed))
    
    sju_answer = concat_sju['answer'].values.tolist()
    sju_query = concat_sju['query'].values.tolist()

    user_text = msg
    #print("질문: " + msg)
    # user 질문 임베딩값, 텐서
#    model = cache.get("model.pkl")
#    if model is None:
#         print("nooo")
    user_encode = model.encode(user_text)
    user_tensor = torch.tensor(user_encode)

    cos_similarity = []
    count = 0

    # 질문지 유사도 탐색
    for i in range(len(concat_sju_embed)):
            cos_similarity.append(dic.cos_sim(user_tensor, concat_sju_embed[i]))

    # 유사도 가장 높은 답변 탐색 및 출력
    best_sim_idx = int(np.argmax(cos_similarity))
    cos_sim_value = np.max(cos_similarity)

    # 유사도 0.5보다 낮은경우는 우리 질문지에 없는 질문.
    if cos_sim_value <= 0.5:
        answer = '준비되지 않은 답변입니다!!'
        
        user_text_nouns =  dic.tokenizer.nouns(user_text)
        for noun in user_text_nouns:
            if noun in dic.Univ_dict_final:
                print('단어사전 내에 정보가 있음')
                count += 1
                break

        # 단어사전내에 정보가 있음 -> 일상대화 x / 준비중인 답변
        if count > 0 :
            answer = '준비되지 않은 답변입니다!'

        else:
            #일상대화 출력
            answer = talk.conv_model(user_text)

        # 이부분에서 잘못된 정답일 경우 -> 일상대화 모델?
        # 단어사전 탐색 후  있으면 답변이 준비중 // 아니면 일상대화
        
    else : 
        answer = sju_answer[best_sim_idx]

    #print(cos_sim_value)
    #print(sju_query[best_sim_idx])
    #print(answer)

    return answer

         