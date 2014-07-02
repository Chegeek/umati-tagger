# -*- coding: utf-8 -*- 

# import os, glob, re, json
# import pandas as pd
import os
import binascii
import postgresops
import redisops
import json
import csv

from flask import Flask, request, session, g, redirect, url_for, \
      abort, render_template, flash, jsonify

from time import strftime

''' ------------------------------- setup and initialize app ------------------------------- '''

app = Flask(__name__)
#app.run(debug=True)

''' ---------------------------------------- Routes ---------------------------------------- '''
@app.route('/')
def index():
    # load_data()
    return render_template('index.html')

@app.route('/sessions/<tag_sessionid>')
def session_code(tag_sessionid):
    return render_template('tagSession.html', session_id = tag_sessionid)

@app.route('/view/<tag_sessionid>', methods=['GET'])
def load_data(tag_sessionid):
    
    try:        
    # '''' Code to read session information from the Redis'''
        tag_sessionid = '/sessions/' + tag_sessionid
        dbase = redisops.RedisDBase()
        session_info = dbase.getSessionInfo(tag_sessionid)
        
        comments_list = session_info['comments_to_tag']
        
        # Comment ID formatting to remove unicode and array characters
        comments_list = str(comments_list).strip('[]')

        #Get the comment records from the database
        dbase = postgresops.PostGresDBase()
        comments_data = dbase.getComments(comments_list)
        
        #Return the updated session with actual comment data
        session_info['comments_to_tag'] = comments_data
       
        return jsonify(session_info)            

    except Exception as e:
        '''' Code to handle the various Exceptions here. Probably Flashing the message'''
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

@app.route('/create', methods=['GET', 'POST'])
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
    for user_session in sessions_details['taggers']:
        
        user_session['tag_qst_id'] = tag_qstid

        end_position =  start_position + user_session['number_to_tag']
        user_session['comments_to_tag'] = comments_to_tag[start_position:end_position]

        '''' Move position where to start slicing the list of comments_to_tag'''
        start_position+=user_session['number_to_tag']
        
        '''' Create the dynamic path for the tagging session '''
        tag_session_url = url_for('session_code', tag_sessionid=str(user_session['tag_qid'] + '_'+ user_session['user_to_tag']))

        # tag_session_url = url_for('session_code', tag_sessionid=str(binascii.b2a_hex(os.urandom(10))))

        '''' Add to the Object of sessions to create in RedisDBase '''
        sessions_to_create[tag_session_url] = user_session

    #Save each user session details to Redis     
    dbase.postUserSessionInfo(sessions_to_create)

    result = {'comments': total_tags}
    # result = {'comments': sessions_to_create}
    return jsonify(**result)    
    # return jsonify(sessions_to_create)

''' --------------------------------- Main Function -------------------------------------- '''                  
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',
         port=int('80'))
    # load_data()