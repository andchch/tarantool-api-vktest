from tarantool import Connection


def tt_connect() -> Connection:
    conn = Connection(host='tarantool',
                      port=3301)
    return conn
