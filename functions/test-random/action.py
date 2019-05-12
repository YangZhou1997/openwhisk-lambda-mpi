import redis

def main(args):
    r = redis.Redis(host='130.127.133.134', port=7001, db=0)
    res1 = r.set('foo', 'bar')
    res2 = r.get('foo')
    return {"result": str(res1) + " " + str(res2)}

