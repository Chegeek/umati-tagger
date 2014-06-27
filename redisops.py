''' ------------------------------- Redis Database Functions Class------------------------------- '''
class RedisDBase():
    def __init__(self):
        self.conn = r_server = redis.Redis('localhost')
        # self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    
