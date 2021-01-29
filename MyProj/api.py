import json
from flask import request, jsonify, Blueprint, abort, render_template, session, redirect, url_for
from flask import Flask,current_app
import re
from flask_socketio import SocketIO, emit  ,send 
from . import db
from .NLP import standard,Predict,get_train_data,dic_champ
import sys
from . import socketio, main_blue

# print()
@main_blue.route('/chat')
def chat():
    return render_template('chat1.html')


# @app.route("/apis/init",methods=['GET','POST'])
@socketio.on('initDialogue',namespace = '/chat')
def initDialogue(message):
    # print(request)
    print('Send')
    c = db.getCount()
    db.addInit()
    emit('status',{'conversation_id':c})

@socketio.on('text', namespace='/chat')
def text(message):
    print(message)
    emit('message', {'msg': message['msg']+'\n'})


# @app.route('/apis/conversation',methods = ['POST'])
@socketio.on('Bot',namespace = '/chat')
def Bot(requestUser):
    print('bot ',requestUser)
    dialog = requestUser['conversation_id']
    
    datatext = []

    datatext.append(requestUser['msg'])
    action =''
    # print(datatext)
    test= get_train_data(datatext,25)
    # print(datatext)
    pred = Predict(test,Raw=datatext)
    # print("pred: ",pred)
    
    


    repmess=''
    if pred['intent'] == 'Unknow':
        repmess = 'Bạn vui lòng hãy đặt câu hỏi đầy đủ để mình có thể trả lời tốt nhất'
        action = 'Unknow'
    test = standard(datatext)
    # print(test)
    dic_play = ['chơi','dùng','sử dụng']
    dic_use = ['dùng','sử dụng']
    dic_object = ['nó','tướng','con này','hero','champ','anh hùng']
    dic_skill = ['chiêu','skill','ký năng']
    intent = pred['intent']
    
    if pred['intent'] == 'how_to_play':
        cnt = 0 
        for w in dic_play:
            result = re.search(w,test[0])
            if result != None:
                cnt+=1
        if cnt == 0:
                intent = 'Unknow'
            # break
        # print(intent)
        cnt1 = 0
        for w in dic_object:
            result = re.search(w,test[0])
            if result != None:
                cnt1+=1
        if cnt1 == 0 or cnt == 0:
            intent = 'Unknow'
                # break
    pred['intent'] = intent
    action = intent
    # if pred['intent'] != intent:
    hero = ''
    skill = ''
    enti  = pred['entities']
    if 'hero' in enti:
        hero = enti['hero']
    if 'skill' in enti:
        skill = enti['skill']
    if(db.getAllObjectReq(id=dialog) != 0):
        # if :
            
        # last = last.filter(id_dia=dialog).latest('id_re')
        last = db.getLastRep(id = dialog)
        # print(last.intent)
        if last['intent'] != 'Unknow' and pred['entities']!={} and pred['intent'] == 'Unknow':
            # if 
            if (last['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with']) and 'hero' in pred['entities'] :
                hero = pred['entities']['hero']
                pred['intent'] = last['intent']
            if (last['intent'] == 'how_to_use_skill' or last['intent'] == 'skill_up' ) and ('hero' in pred['entities'] or 'skill' in pred['entities']) :
                if hero == '':
                    hero = last['hero']
                if skill == '':
                    skill = last['skill']
                pred['intent'] = last['intent']

        if last['intent'] == pred['intent']:
                if hero == '':
                    hero = last['hero']
                if skill == '':
                    skill = last['skill']

        # if last.intent == 'introduce':


        intent = pred['intent']
        action = intent
    # if()
        if intent == 'Unknow':
            # print('yes')
            if hero != '' and (last['action'] == 'ask_hero' or last['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with']):
                intent = last['intent'] 
                action = intent
                pred['intent'] = intent
            if skill != '' and (last['action'] == 'ask_skill' or last['intent'] in ['how_to_use_skill','skill_up']):
                intent = last['intent']
                action = intent
                pred['intent'] = intent
            if skill =='' and hero  == '':
                repmess = ' bạn có thể đặt lại câu hỏi được không ạ ? :( mình vẫn chưa hiểu ý của bạn :(('
                action = 'ask_intent'
    
    # if pred['intent'] in ['how_to_play', 'introduce','combo','counter','be_countered'] 
        pred['intent'] = intent
        if (last['intent'] == 'how_to_use_skill' or last['intent'] == 'skill_up' ) and (skill =='' or hero =='') and last['intent'] == pred['intent'] :
            if skill == '' and hero == '':
                repmess = 'bạn muốn hỏi skill gì và của tướng nào vậy :(('
                action = 'ask_hero_and_skill'
            if skill == '' and hero !='':
                repmess = 'bạn muốn tìm hiểu skill nào của tướng '+ hero+ " vậy bạn có thể nói rõ hơn không ? :(( "
                action = 'ask_skill'
            if skill !='' and hero == '':
                repmess = 'Có nhiều tướng có skill '+ skill +' mà bạn bạn nói rõ hơn được không :(( ?'
                action  = 'ask_hero'
        if(last['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with']) and hero == '' and last['intent'] == pred['intent']:
            repmess = 'bạn vui lòng nói rõ tên tướng hộ mình'
            action = 'ask_hero'
        if pred['intent'] != 'Unknow' and pred['intent'] != last['intent'] and last['intent'] != 'Unknow':
            if pred['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with'] and hero == '':
                if last['hero'] != '':
                    hero = last['hero']
                else :
                    repmess = 'bạn vui lòng nói rõ tên tướng hộ mình'
                    action = 'ask_hero'
            if pred['intent'] in ['how_to_use_skill', 'skill_up']:
                if hero == '' and skill != '': 
                    if last['hero'] !='':
                        hero = last['hero']
                    else :
                        repmess = 'bạn vui lòng nói rõ tên tướng hộ mình'
                        action = 'ask_hero'
                if skill == ''and hero != '':
                    repmess = 'bạn muốn tìm hiểu skill nào của tướng '+ hero+ " vậy bạn có thể nói rõ hơn không ? :(( "
                    action = 'ask_skill'
                if skill =='' and hero == '':
                    repmess = 'bạn muốn hỏi skill gì và của tướng nào vậy :(('
                    action = 'ask_hero_and_skill'
        if pred['intent'] != 'Unknow' and last['intent'] == 'Unknow':
            if (pred['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with']) and hero == '':
                repmess = 'bạn vui lòng nói rõ tên tướng hộ mình'
                action = 'ask_hero'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero =='' and skill !='' :
                repmess = 'bạn muốn biết skill '+ skill + ' của tướng nào vậy ạ ?'
                action = 'ask_hero'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero !='' and skill =='' :
                repmess = 'bạn muốn biết skill nào của '+ hero + ' vậy ạ ?'
                action = 'ask_skill'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero =='' and skill =='' :
                repmess = 'bạn vui lòng nói rõ tên tướng và skill giúp mình với ạ'
                action = 'ask_hero_and_skill'
            
        if pred['intent'] == 'Unknow' and last['intent'] == 'Unknow':
            
            if hero != '':
                repmess = 'Bạn muốn biết thông tin gì về tướng '+ hero +'ạ'
                action = 'ask_intent'
            if skill != '':
                repmess = 'Bạn muốn biết thông tin gì về skill ' + skill + 'ạ'
                action = "ask_intent"
            if hero != '' and skill != '':
                repmess= 'mình không rõ câu hỏi của bạn lắm bạn, bạn có thể hỏi rõ hơn được khoong? '
                action = 'ask_intent'
            # if skill != '' and hero != ''

        # if 
    else :
        if intent == 'Unknow':
            if hero != '':
                repmess = 'Bạn muốn biết thông tin gì về tướng '+ hero +'ạ'
                action = 'ask_intent'
            if skill != '':
                repmess = 'Bạn muốn biết thông tin gì về skill ' + skill + 'ạ'
                action = "ask_intent"
            if hero != '' and skill != '':
                repmess= 'mình không rõ câu hỏi của bạn lắm bạn, bạn có thể hỏi rõ hơn được khoong? '
                action = 'ask_intent'
        else :
            if (pred['intent'] in ['how_to_play','build_item','counter','be_countered','introduce','combo','support_socket','combine_with']) and hero == '':
                repmess = 'bạn vui lòng nói rõ tên tướng hộ mình'
                action = 'ask_hero'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero =='' and skill !='' :
                repmess = 'bạn muốn biết skill '+ skill + ' của tướng nào vậy ạ ?'
                action = 'ask_hero'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero !='' and skill =='' :
                repmess = 'bạn muốn biết skill nào của '+ hero + ' vậy ạ ?'
                action = 'ask_skill'
            if (pred['intent'] in ['how_to_use_skill', 'skill_up']) and hero =='' and skill =='' :
                repmess = 'bạn vui lòng nói rõ tên tướng và skill giúp mình với ạ'
                action = 'ask_hero_and_skill'
    

    def check_(s):
        if s == '' or (s is None )or s == ' ':
            return False
        else :
            return True
    if (skill in ['Q','W','E','R']) == False and skill != '':
        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về skill '+ skill +':(( . Mình sẽ cập nhật sớm nhất'
        action = 'no_answer'
    else : 
        if hero !='':
            champ = dic_champ[hero]
            # print(champ)
            message = db.getAnsChamp(champ = champ)

            # print(message.combo)
            if  pred['intent'] == 'how_to_play':
                if check_(message['how_to_play']) and hero != '' :
                    repmess = message['how_to_play']
                else :
                    if check_(message['how_to_play']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách chơi của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'how_to_use_skill' and skill == 'Q':
                if check_(message['how_to_use_skill_Q']) and hero != '' and skill == 'Q' :
                    repmess = message['how_to_use_skill_Q']
                else :
                    if check_(message['how_to_use_skill_Q']) == False:

                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về skill Q của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if skill == 'W' and pred['intent'] == 'how_to_use_skill':
                if check_(message['how_to_use_skill_W']) and hero != '' and skill == 'W' and pred['intent'] == 'how_to_use_skill':
                    repmess = message['how_to_use_skill_W']
                else :
                    if check_(message['how_to_use_skill_W']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về skill W của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if skill == 'E' and pred['intent'] == 'how_to_use_skill':
                if check_(message['how_to_use_skill_E']) and hero != '':
                    repmess = message['how_to_use_skill_E']
                else :
                    if check_(message['how_to_use_skill_E']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về skill E của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if skill == 'R' and pred['intent'] == 'how_to_use_skill':
                if check_(message['how_to_use_skill_R']) and hero != '':
                    repmess = message['how_to_use_skill_R']
                else :
                    if check_(message['how_to_use_skill_R']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về skill R của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'skill_up':
                if check_(message['skill_up']) and hero != '' and pred['intent'] == 'skill_up':
                    repmess = message['skill_up']
                else :
                    if check_(message['skill_up']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách lên kĩ năng của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'combine_with':
                if check_(message['combine_with']) and hero != ''and pred['intent'] == 'combine_with':
                    repmess = message['combine_with']
                else :
                    if check_(message['combine_with']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về những tướng kết hợp với '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'counter':
                if check_(message['counter']) and hero != '' and pred['intent'] == 'counter':
                    repmess = message['counter']
                else :
                    if check_(message['counter']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về những tướng kém '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'be_countered':
                if check_(message['be_countered']) and hero != ''and pred['intent'] == 'be_countered':
                    repmess = message['be_countered']
                else :
                    if check_(message['be_countered']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách khắc chế của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'combo':
                if check_(message['combo']) and hero != '' and pred['intent'] == 'combo':
                    repmess = message['combo']
                else :
                    if check_(message['combo']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách combo của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'build_item':
                if check_(message['build_item']) and hero != '' and pred['intent'] == 'build_item' :
                    repmess = message['build_item']
                else :
                    if check_(message['build_item']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách lên đồ của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'support_socket':
                if check_(message['support_socket']) and hero != '' and pred['intent'] == 'support_socket':
                    repmess = message['support_socket']
                else :
                    if check_(message['support_socket']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có dữ liệu về cách build bảng ngọc của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
            if pred['intent'] == 'introduce':
                if check_(message['introduce']) and hero != '' and pred['intent'] == 'introduce':
                    repmess = message['introduce']
                else :
                    if check_(message['introduce']) == False:
                        repmess = 'Xin lỗi bạn hiện tại mình chưa có thông tin của '+ hero +' :(( . Mình sẽ cập nhật sớm nhất'
                        action = 'no_answer'
                
    
    if requestUser['msg'] != '':
        mess = db.addReq(id_dia_id=dialog,req = requestUser['msg'],hero = hero,skill = skill,intent= intent,action = action)
        # mess.save()

    # print("last: ",last.count())
    # mess = Request_dia(id_dia=dialog,req = data['mess'],)
    all_line = repmess.split('\n')
    s = ''
    for line in all_line:
        s+= '<p>' + line + '</p>' 
    emit('message_bot',{'msg':s+'\n','conversation_id':dialog})
    # return jsonify({
    #     'intent':intent,
    #     'action':'action_'+action,
    #     'message': repmess,


# app = create_app()

# if __name__ == '__main__':
    # socketio.run(app,debug=True)