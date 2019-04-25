echo create function test_redis

zip -r test_redis.zip virtualenv/bin/activate_this.py virtualenv/lib/python2.7/site-packages/redis __main__.py

wsk -i action create test_redis test_redis.zip --kind python:2 --main test_redis

wsk -i action invoke test_redis -r
