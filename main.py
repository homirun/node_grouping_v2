import asyncio
import uuid
import time
import logging
import sys
from datetime import datetime

import grpc
from netifaces import interfaces, ifaddresses, AF_INET
import uptime

from proto import node_pb2
from proto import node_pb2_grpc
from server import *
from node import *


def main():
    node_id, node_list = init()


def init():
    print('/*----init----*/')
    node_id = create_node_id()
    my_ip = None
    nodes = []
    try:
        my_ip = ifaddresses('en0')[AF_INET][0]['addr']
    except ValueError:
        my_ip = ifaddresses('eth0')[AF_INET][0]['addr']
    finally:
        args = sys.argv
        if len(args) > 1:
            request_ip = args[1]
        else:
            request_ip = input('request_ip:')

        res = throw_add_request(node_id, request_ip, my_ip)

        if res is False:
            # もし他のノードが存在しなかった時
            nodes.extend(create_node_list(node_id))
        else:
            pass
            # resの値をnode_listへ
            # TODO nodesにnodeの情報を格納する
            # nodes.extend(res['node_list'])
    start_grpc_server()
    return node_id, nodes


def throw_add_request(node_id, request_ip, my_ip):
    with grpc.insecure_channel(request_ip) as channel:
        stub = node_pb2_grpc.AddRequestServiceStub(channel)
        request_message = node_pb2.AddRequestDef(request_id=create_request_id(), id=node_id, sender_ip=my_ip,
                                                 boot_time=get_boot_unix_time(), time_stamp=get_now_unix_time())
        response = stub.add_request(request_message)
        print(response)

    return response


def create_node_list(my_node_id):
    node_id = my_node_id
    my_ip = None
    try:
        my_ip = ifaddresses('en0')[AF_INET][0]['addr']
    except ValueError:
        my_ip = ifaddresses('eth0')[AF_INET][0]['addr']
    finally:
        my_node = Node(uid=node_id, ip=my_ip, boot_time=get_boot_unix_time())

    pre_node_list = list()
    pre_node_list.append(my_node.__dict__)

    return pre_node_list


def create_node_id():
    return str(uuid.uuid4())


def create_request_id():
    return str(uuid.uuid4())


def get_boot_unix_time():
    return uptime.boottime().timestamp()


def get_now_unix_time():
    return float(datetime.now().strftime('%s'))


def start_grpc_server():
    pass


if __name__ == '__main__':
    main()
