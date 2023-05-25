# 일상대화 모델 답변 출력 부분 
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
import torch
#from api import cache
import os

# 토크나이저 사용을 위한 토큰 선언
Q_TKN = "<usr>"
A_TKN = "<sys>"
BOS = '</s>'
EOS = '</s>'
MASK = '<unused0>'
SENT = '<unused1>'
PAD = '<pad>'

device = "cuda" if torch.cuda.is_available() else "cpu"
our_model = torch.load(os.getenv("SJU_EPOCH8MODEL_PATH"), map_location='cpu')
koGPT2_TOKENIZER = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2",
            bos_token=BOS, eos_token=EOS, unk_token='<unk>',
            pad_token=PAD, mask_token=MASK)

# 답변 생성 과정 -> user_text에 대한 답변
def conv_model(text):
    #with torch.no_grad():
    q = text
    a = ""
    while 1:
        input_ids = torch.LongTensor(koGPT2_TOKENIZER.encode(Q_TKN + q + SENT + A_TKN + a)).unsqueeze(dim=0).to(device)
        pred = our_model(input_ids)
        pred = pred.logits
        gen = koGPT2_TOKENIZER.convert_ids_to_tokens(torch.argmax(pred, dim=-1).squeeze().cpu().numpy().tolist())[-1]
        if gen == EOS:
            break
        a += gen.replace("▁", " ")
    conv_ans = a.strip()
    return str(conv_ans)