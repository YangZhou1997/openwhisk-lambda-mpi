import redis

def test(args):
    r = redis.Redis(host='localhost', port=7001, db=0)
    print r.set('foo', 'bar')
    print r.get('foo')

if __name__ == "__main__":
    test(0);
