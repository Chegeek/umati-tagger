import redis

''' ------------------------------- Redis Database Functions Class------------------------------- '''
class RedisDBase():
    def __init__(self, **redis_kwargs):
        self.r_server = redis.Redis('localhost')

    def checkUserCredentials(self, username, password):
        error = None
        if username != self.r_server.get('username'):
            error = 'Invalid username'
        elif password != self.r_server.get('userpassword'):
            error = 'Invalid password'
        return error

    def postSessionInfo(self, session_info):
    	self.r_server.incr('session_id')
    	tag_sessionid = 'session_id' + str(self.r_server.get('session_id')) 
    	self.r_server.hmset(tag_sessionid, session_info)
    	return tag_sessionid

    def postUserSessionInfo(self, sessions_to_create):
    	for session_id in sessions_to_create:
    		self.r_server.hmset(session_id, sessions_to_create[session_id])

    def getSessionInfo(self, session_id):
        self.tag_qst, self.key_options = self.r_server.hmget(session_id, 'tag_qst', 'key_options')
        return self.tag_qst, self.key_options

    def getUserSessionInfo(self, session_id):
    	self.result = self.r_server.hgetall(session_id)
    	return self.result

    def updateUserSessionTagList(self, session_id, comments_to_tag):
    	self.r_server.hset(session_id, 'comments_to_tag', comments_to_tag)