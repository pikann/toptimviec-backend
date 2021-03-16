def when_ready(server):
    open('/tmp/app-initialized', 'w').close()


bind = '0.0.0.0:80'