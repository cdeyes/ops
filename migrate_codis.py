from kazoo.client import KazooClient
import json
import redis
import time
from multiprocessing import Pool 
import os
import pdb

zk_server = '10.51.28.197'
zk_port = '2181'
zk_codis_root_uri = '/codis3/'
zk_host = '%s:%s' % (zk_server, zk_port)

dst_redis_server='xxxxxx.redis.rds.aliyuncs.com'
dst_redis_port = '6379'
dst_redis_passwd='xxxxxx'

src_codis_passwd='xxxxx'

def get_codis_server(zk_host, zk_codis_root_uri, codis_product, timeout=5):
    zk = KazooClient(hosts=zk_host, read_only=True)
    zk.start()
    zk_codis_uri = '%s%s/group' % (zk_codis_root_uri, codis_product)
    result = {}
    # print dir(zk)
    # print zk.get_children('/') # like zkcli 'ls' command
    # print zk.get('/')  # like zkcli 'get' command
    codis_group_list = zk.get_children(zk_codis_uri)
    for codis_group in codis_group_list:
        zk_codis_info = zk.get(zk_codis_uri + '/' + codis_group)
        if zk_codis_info:
            server = json.loads(zk_codis_info[0]).get('servers', [])[0].get('server', {})
            if server:
                codis_key = '%s_%s' % (codis_product, codis_group)
                result[codis_key] = server
    zk.stop()
    return result


def get_redis_instance(redis_config):
    host = redis_config.get('host','')
    port = redis_config.get('port','')
    password = redis_config.get('password',None)
    max_connections = redis_config.get('max_connections',10)
    redis_instance = None
    if port and host:
        redis_pool = redis.ConnectionPool(host=host, port=port, password=password)
        redis_instance = redis.Redis(connection_pool=redis_pool, max_connections=max_connections)
    return redis_instance


def get_codis_content(src_redis_config, dst_redis_config, scan_count=1000, pipe_count=30000, ex=1800, match=None):
    src_keylist = []
    src_len = 0
    src_instance = get_redis_instance(src_redis_config)
    dst_instance = get_redis_instance(dst_redis_config)
    src_pipe = src_instance.pipeline(transaction=False)
    dst_pipe = dst_instance.pipeline(transaction=False)
    for src_keys in src_instance.scan_iter(match=match, count=scan_count):
        src_keylist.append(src_keys)
        if src_len < pipe_count and not src_keys:
            src_len += 1
        else:
            for src_key in src_keys:
                src_pipe.get(src_key)
            src_valuelist = src_pipe.execute()
            src_contents = zip(src_keylist,src_valuelist)    
            for content in src_contents:
                dst_pipe.set(content[0], content[1], ex=ex)
            dst_pipe.execute()
            src_keylist = []
            src_len = 0
     

def main():
    print 'Parent process %s.' % os.getpid()
    codis_servers = get_codis_server(zk_host, zk_codis_root_uri, 'hz-sharepasscodis-01')
    print codis_servers
    dst_redis_config = {'host': dst_redis_server, 'port': dst_redis_port, 'password': dst_redis_passwd}
    pool = Pool(processes=len(codis_servers))
    for codis_server in codis_servers.values():
        host, port = codis_server.split(':')
        src_redis_config = {'host': host, 'port': port, 'password': src_codis_passwd} 
        pool.apply_async(get_codis_content, (src_redis_config, dst_redis_config))
    pool.close()
    pool.join()

    
if __name__ == '__main__':
    main()    
