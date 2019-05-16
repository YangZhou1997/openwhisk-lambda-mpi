import redis

def main(args):
    r = redis.Redis(host='10.10.1.2', port=7001, db=0)
    res1 = r.set('foo', 'bar')
    res2 = r.get('foo')
    res3 = r.get('random')
    print(res3)
    return {"result": str(res1) + " " + str(res2)}

# print(main(0))
