import redis

''' ------------------------------- Redis Database Functions Class------------------------------- '''
class RedisDBase():
    def __init__(self, **redis_kwargs):
        self.r_server = redis.Redis('localhost')

    def postSessionInfo(self, sessions_to_create):
    	for session_id in sessions_to_create:
    		self.r_server.hmset(session_id, sessions_to_create[session_id])

    def getSessionInfo(self, session_id):
    	self.result = self.r_server.hgetall(session_id)
    	return self.result

    def updateSessionTagList(self, session_id, comments_to_tag):
    	self.r_server.hset(session_id, 'comments_to_tag', comments_to_tag)