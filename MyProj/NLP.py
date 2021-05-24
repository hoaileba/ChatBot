import numpy as np
import tensorflow as tf
import pandas as pd
import os
import json

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
from tensorflow.keras.layers import Conv2D,Input,Dropout,Bidirectional,Embedding,GRU
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Lambda, dot, Activation, concatenate
from tensorflow.keras.layers import Layer
from tensorflow.keras.models import load_model
graph = tf.compat.v1.reset_default_graph()

class Attention(Layer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, hidden_states):
        hidden_size = int(hidden_states.shape[2])
        score_first_part = Dense(hidden_size, use_bias=False, name='attention_score_vec')(hidden_states)
        h_t = Lambda(lambda x: x[:, -1, :], output_shape=(hidden_size,), name='last_hidden_state')(hidden_states)
        score = dot([score_first_part, h_t], [2, 1], name='attention_score')
        attention_weights = Activation('softmax', name='attention_weight')(score)
        context_vector = dot([hidden_states, attention_weights], [1, 1], name='context_vector')
        pre_activation = concatenate([context_vector, h_t], name='attention_output')
        attention_vector = Dense(128, use_bias=False, activation='tanh', name='attention_vector')(pre_activation)
        return attention_vector


model = Sequential()
model.add(Embedding(340,5000, input_length =25, trainable = False))
model.add(Bidirectional(GRU(256,return_sequences=True,reset_after = True)))
model.add(Attention())
model.add(Dropout(0.5))
model.add(Dense(128, activation = "relu"))
model.add(Dropout(0.5))
model.add(Dense(10, activation = "sigmoid"))
PATH = 'MyProj/'          
def load_model_():
    # global model
    model.load_weights(PATH + 'weight_model/model (1).h5')


load_model_()
dir_test_2 = PATH + 'weight_model/demo_submission_3.csv'
all_skill = ['W','Q', 'E', 'R']
stop_words = ['','ạ','ơi','chị','bạn','ừ','nhỉ',
              'nhờ','nhể','hả','em','anh','ê','à',
              'bot','về','với','hình như','thấy',
              'không','cứ','sai','hay sao','thế','đi','khỏe','yếu','ơ','đang','bảo là','sao','như nào','vậy','đi mid','đi rừng','đi sp','đi lane','đi ad']
all_intent = ['combine_with', 
              'be_countered', 
              'skill_up', 
              'counter', 
              'combo', 
              'introduce', 
              'support_socket', 
              'build_item', 
              'how_to_play',
              'how_to_use_skill']
label_dic = {}
id = 0
for intent in all_intent:
  label_dic[intent] = id
  id+=1
dict_replace = {'cộng':'lên','up':'lên','nâng':'lên','hành':'counter','thắng':'counter','săn':'counter','giết':'counter','đồ sát':'counter',
                'đi cùng':'chơi chung','đánh cùng':'chơi chung','ăn':'counter','sợ':'bị counter','xiên':'counter','hạ':'counter','phang':'counter'
                ,'đấm':'counter','kia':'gì','thua': 'bị counter','solo': 'đánh'}
df_test_2 = pd.read_csv(dir_test_2)

X_test_2 = df_test_2['0']

# list_champ = open(dir_champions)
dic_hero = {}
all_champions = []
path_champ = PATH + 'weight_model/list_champs.txt'
fpath = open(path_champ)

for line in fpath:
    all_champions.append(line.split('\n')[0])
fpath.close()
all_name = []
dic_hero = {}
for line in all_champions:
    name = line.split('\n')[0]
    dic_hero[name] = name
    parts = name.split(' ')
    if len(parts) >1:
        for p in parts:
            if p!= '&':
                dic_hero[p] = name
                all_name.append(p)
    all_name.append(name)
all_name.append('Rell')
def standard(all_line):
  all_l = []
  xx = []
  
  for line in all_line :
      line = ' ' + line + ' '
      for h in all_champions:
          l =re.sub(' '+h+' ',' hero ',line)
          line = l
      l = re.sub(r'\s+[A-Z]\s+',' skill ',line)
      l =l.strip()
      all_l.append(l)
  for line in all_l:
    w = line.split(' ')
    l =''
    for ww in w:
      if ww in dict_replace:
        l+=dict_replace[ww]+' '
      else:
        l+=ww + ' '
    l = l.strip()
    xx.append(l)
  return xx

def cleaning(sentences):
  words = []
  for s in sentences:
    clean = re.sub(r'[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]\s*', " ", s)
    # print(clean)
    w = clean.split(' ')
    #stemming
    
    words.append([i.lower() for i in w if i not in stop_words])
    
  return words

def create_tokenizer(words, filter = '[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]' ):
  token = Tokenizer(filters = filter)
  token.fit_on_texts(words)
  # token
  return token

def get_length(words):
  return len(max(words,key = len))

def encoding(words,token):
  return token.texts_to_sequences(words)

def padding(encoded, max_length):
  return pad_sequences(encoded,max_length,padding = 'post')


# clean = cleaning(X_train_data)

def get_dict(path):
  ff = open(path)
  for line in ff:
    dic = eval(line)
  # print(dic)
  return dic
Dic = get_dict(PATH + 'weight_model/dict-14_48-4-12-2020.txt')
# print(dic)
def get_train_data(encoded_doc, max_length,dic = Dic):
  ptest = standard(encoded_doc)
  ptest = cleaning(ptest)

  # print(predic_test)
  correct = cre_encode(ptest,dic)
#   print('succ')

  length = max_length
  padded_doc = padding(ptest, length)
  return padded_doc
def cre_encode(all_sen,dic):
  for i in range(len(all_sen)):
    # print(all_sen[i])
    for j, x in enumerate(all_sen[i]):
      if x in dic:
        num = dic[x]
      else:
        num = 0
      # print(num)
      all_sen[i][j] = num
  return all_sen


def getModel():
    return model

def Predict(Data_test,Raw):
    t = Data_test
    t = np.array(t).reshape(1,25)
    # print(t)
    cnt = np.count_nonzero(t == 0)
    if cnt == 25:
      return {'intent':'Unknow','entities' : {}}
    # global model
    pred = model.predict(t)
    pr = pred
    # print(pr)
    pred = np.argmax(pred,axis=1)
    # if(pr[0][pred[0]] < 0.1):
      # return {'intent':'Unknow','entities' : {}}
    

    #   all_name = []
    dic_hero = {}
    skill = []
    hero = []
    ind = []
    # print(Raw)
    for line in Raw:
        line = ' '+line+' '
        h= []
        sk = []
        tmph = []
        for name in all_name:
            result = re.findall(name,line)
            if  result:
                tmph.append(result[0])
        cor = []
        words = line.split(' ')
        for hh in tmph:
            for w in words:
                if hh == w:
                    cor.append(hh)
                    # print(hh)
                    ind.append(re.search(hh, line).start())
                    break
        hero.append(cor)
        sk = re.findall('\s+[A-Z]\s+',line)
        if sk != []:
            skill.append(sk[0].split(' ')[1])
        else:
            skill.append('')
    # for h in hero[0]:
    #   id = Raw.index(h)
    id = ind.index(min(ind))
    # print(hero[0][id])
    # print(ind)
    ghi = []
    tmp = {}
    tmp['intent'] = all_intent[pred[0]]
    enti = {}
    if skill[0] != '':
        enti['skill'] = skill[0]
    if hero[0]!='' and hero[0]!=[]:
        enti['hero'] = hero[0][id]
    dic = {}
    tmp['entities'] = enti
    # print(tmp['entities'])
    ghi.append(tmp)
    return ghi[0]


dic_champ = {}
list_champions = []

    
    
f = open(PATH + 'weight_model/champ__.txt')
for line in f:
    line = line.split('\n')[0]
    dic_champ[line.split('\t')[0]] = line.split('\t')[-1]
    text = line.split('\t')[-1]
    # print(line.split('\t'))
    if (text in list_champions) == False:
        list_champions.append(text)
list_champions.append('Rell')
f.close()