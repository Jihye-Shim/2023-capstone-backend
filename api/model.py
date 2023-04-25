import torch
import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm
import pickle
import os

with open(os.getenv('MODEL_PATH'), 'rb') as f:
    model = pickle.load(f)

df = pd.read_csv(os.getenv('SW_CSV_PATH'), encoding = 'utf-8')

def predict(msg, major):
    df['embedding'] = pd.Series([[]] * len(df)) # dummy
    df['embedding'] = df['query'].map(lambda x: list(model.encode(x)))
    embedding_data = torch.tensor(df['embedding'].tolist())

    user_text = msg
    user_major = major

    embed_list = []
    answer_list = []

    for idx in range(0,df.shape[0]):
        
        row = df.iloc[idx]
        index = df.index[idx]
        
        if row['intent'] == user_major:
            embed_list.append(row['embedding'])
            answer_list.append(row['answer'])

    embed_list = torch.tensor(embed_list)

    user_encode = model.encode(user_text)
    user_tensor = torch.tensor(user_encode)

    def cos_sim(A, B):
        return dot(A, B)/(norm(A)*norm(B))

    cos_similarity = []

    for i in range(len(embed_list)):
        cos_similarity.append(cos_sim(user_tensor, embed_list[i]))

#    print("user: " + user_text)
    #print(len(embed_list))

    best_sim_idx = int(np.argmax(cos_similarity))
    answer = answer_list[best_sim_idx]

#    print("bot: " + answer)
    return answer