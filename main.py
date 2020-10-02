import grpc
import asyncio
import uuid
import time
import logging
import sys
from netifaces import interfaces, ifaddresses, AF_INET


def main():
    node_id, node_list = init()


def init():
    print('/*----init----*/')
    node_id = create_node_id()
    my_ip = None
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
        res = throw_add_request(my_node_id, node_list, request_ip, my_ip)
        if res is False:
            # もし他のノードが存在しなかった時
            nodes.extend(create_node_list(my_node_id))
        else:
            # resの値をnode_listへ
            nodes.extend(res['node_list'])
    start_grpc_server()
    return node_id, node_list


def throw_add_request():
    return


def create_node_list(node_id):
    return


def create_node_id():
    return str(uuid.uuid4())


def start_grpc_server():
    pass




if __name__ == '__main__':
    main()
