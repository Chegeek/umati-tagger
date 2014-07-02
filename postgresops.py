#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Jun 18, 2014

@author: chalenge
'''
import settings
import psycopg2

from psycopg2 import extras

       
''' ------------------------------- MySQL Database Functions Class------------------------------- '''
class PostGresDBase():
    def __init__(self):
        self.conn = psycopg2.connect(**settings.dbaseConfig)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def getToTag(self, tags_needed):
        query = 'SELECT post_comments_id FROM "AutoCollected" ORDER BY RANDOM() LIMIT ' + str(tags_needed)
        self.cursor.execute(query)
        self.result = self.cursor.fetchall()
        return list(item['post_comments_id'] for item in self.result)

    def getComments(self, tags_list):
        query = 'SELECT page_id, page_name,post_message,post_comments_id,post_comments_message FROM "AutoCollected" WHERE post_comments_id IN (%s)' % tags_list
        self.cursor.execute(query)
        self.result = self.cursor.fetchall()
        return self.result

    # def postTags(self, tagged_set):
    #     #TODO - Optimize to execute to database only once
    #     query = 'INSERT INTO tagged_data VALUES (%s)'

    #     for tag in tagged_set['tags']:
    #         self.cursor.execute(query, tagged_set['session_id'],tagged_set['session_desc'], tagged_set['tagged_by'], tag, tagged_set['tags'][tag])
        
    #     self.conn.commit()

