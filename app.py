# -*- coding: utf-8 -*- 

# import os, glob, re, json
# import pandas as pd
import os
import binascii
import postgresops
import redisops
import json
import csv
import ast
import time

from flask import Flask, request, session, g, redirect, url_for, \
      abort, render_template, flash, jsonify
from time import strftime
from flask.ext.mail import Mail, Message

''' ------------------------------- setup and initialize app ------------------------------- '''
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_TLS = False
MAIL_USE_SSL= True
MAIL_USERNAME = 'chalenge@ihub.co.ke'
MAIL_PASSWORD = 'testdevapp'
# DEFAULT_MAIL_SENDER = chalengezw@gmail

app = Flask(__name__)
app.config.from_object(__name__)
mail = Mail(app)

''' ---------------------------------------- Routes ---------------------------------------- '''
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        dbase = redisops.RedisDBase()
        error = dbase.checkUserCredentials(request.form['username'], request.form['password'])
        
        if not error:
            session['logged_in'] = True
            flash('You were logged in')
            time.sleep(2)
            return redirect(url_for('create'))
    return render_template('login.html', error=error)

@app.route('/create')
def create():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('createSession.html')

@app.route('/sessions/<tag_sessionid>')
def session_code(tag_sessionid):
    return render_template('tagSession.html', session_id = tag_sessionid)

@app.route('/view/<tag_sessionid>', methods=['GET'])
def load_session_data(tag_sessionid):
    
    try:        
    # '''' Code to read session information from the Redis'''
        tag_sessionid = '/sessions/' + tag_sessionid
        dbase = redisops.RedisDBase()
        session_info = dbase.getUserSessionInfo(tag_sessionid)
        
        tag_qstid = session_info['tag_qst_id']
        tag_qst, tag_keys = dbase.getSessionInfo(tag_qstid)

        comments_list = session_info['comments_to_tag']
        
        # Comment ID formatting to remove unicode and array characters
        tag_keys = eval(tag_keys)

        comments_list = str(comments_list).strip('[]')

        #Get the comment records from the PostGres database
        dbase = postgresops.PostGresDBase()
        comments_data = dbase.getComments(comments_list)
        
        #Return the updated session with actual comment data
        session_info['comments_to_tag'] = comments_data

        session_info['tag_qst'] = tag_qst
        session_info['tag_keys'] = tag_keys

        return jsonify(session_info)            

    except Exception as e:
        ''' Code to handle the various Exceptions here. Probably Flashing the message'''
        return 'Session ({0}) has not been found'.format(e)

@app.route('/sessions/add', methods=['POST'])
def saveLabels():
    tagdataString = request.form['toSave']
    tagdata = json.loads(tagdataString)

    tag_time = strftime("%Y-%m-%d %H:%M:%S")

    # Redis write --> Need to figure how to add the tags to the jsonfile or whatever and trim file

    try:
        tag_sessionid = '/sessions/' + tagdata['session_id']
        dbase = redisops.RedisDBase()
        session_info = dbase.getSessionInfo(tag_sessionid)

        session_info['comments_to_tag'] = eval(session_info['comments_to_tag'])

        filePath = 'static/_data/tagged_data/' + tagdata['session_qst'] + '.csv'
        with open(filePath, "a+") as csvreader:
            qst_file = csv.writer(csvreader, delimiter=',')
            tag_lines=[]
            for tag_item in tagdata['tags']:
                line =[]
                line.append(tagdata['session_id'])
                line.append(tagdata['session_desc'])
                line.append(tagdata['tagged_by'])
                line.append(tag_time)
                line.append(tag_item)
                line.append(tagdata['tags'][tag_item])
                tag_lines.append(line)


                session_info['comments_to_tag'].remove(tag_item)
                # = session_info['comments_to_tag'][tagdata['tag_pos']:]

            # qst_file.writerows(tag_lines)
    #         # session_info = json.load(qst_file)

    # # ''' Code to post tags to RedisDBase or wherever '''
    # # # dbase = redisops.RedisDBase()
    # # # dbase.postTags(tagdata)    

    # '''' Code to update tag list and remove those tagged in RedisDBase or wherever '''
        dbase = redisops.RedisDBase()
        dbase.updateSessionTagList(tag_sessionid, session_info['comments_to_tag'])        
        
        return jsonify(session_info)            

    except IOError as e:
        return 'Session ({0}) has not been found'.format(tagdata['session_id'])    

@app.route('/sessions/create', methods=['GET', 'POST'])
def create_sessions():
    '''' Code to create sessions '''
    sessions_to_create = {}
    start_position = 0
    details_string = request.form['sessionsObject']
    sessions_details = (json.loads(details_string))['taggers_info']

    total_tags = sum(item['number_to_tag'] for item in sessions_details['taggers'])
    
    dbase = postgresops.PostGresDBase()
    comments_to_tag = dbase.getToTag(total_tags)
    
    #Save the tagging session details to Redis
    dbase = redisops.RedisDBase()        
    tag_qstid = dbase.postSessionInfo(sessions_details)

    #Create individual user tagging sessions with list of comment ids
    with mail.connect() as conn:
        for user_session in sessions_details['taggers']:
            
            user_session['tag_qst_id'] = tag_qstid

            end_position =  start_position + user_session['number_to_tag']
            user_session['comments_to_tag'] = comments_to_tag[start_position:end_position]

            '''' Move position where to start slicing the list of comments_to_tag'''
            start_position+=user_session['number_to_tag']
            
            '''' Create the random path for the tagging session '''
            # tag_session_url = url_for('session_code', tag_sessionid=str(user_session['tag_qid'] + '_'+ user_session['user_to_tag']))
            tag_session_url = url_for('session_code', tag_sessionid=str(binascii.b2a_hex(os.urandom(10))))

            '''' Add to the Object of sessions to create in RedisDBase '''
            sessions_to_create[tag_session_url] = user_session

            ''' --------------------------------- Code to send the emails to the users -------------------------------------- '''                  
            message = 'Hello, %s. \n\nPlease tag the data in response to the question\n\n %s\n\n Find the tagging session at http://41.242.2.131%s .\n\nThanks' \
                         % (user_session['user_to_tag'], sessions_details['tag_qst'],  tag_session_url)
            subject = 'Request to tag data' 
            msg = Message(sender=("Python App Development", "chalenge@ihub.co.ke"),
                            recipients=[user_session['user_email']],
                            body=message,
                            subject=subject)

            conn.send(msg)        

    ''' --------------------------------- Save each user session details to Redis -------------------------------------- '''     
    dbase.postUserSessionInfo(sessions_to_create)

    # result = {'comments': total_tags}
    # result = {'comments': sessions_to_create}
    # return jsonify(**result)    
    return jsonify(sessions_to_create)

''' --------------------------------- Main Function -------------------------------------- '''                  
if __name__ == '__main__':
    app.secret_key = 'MPF\xfbz\xfbz\xa7\xcf\x84\x8cd\rg\xd5\x04\xee\xa4\xd6\xb9]\xf8\x0e\xf3'
    app.debug = True
    app.run(host='0.0.0.0',
         port=int('80'))
    # load_data()