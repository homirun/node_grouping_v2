import asyncio
import uuid
import time
import sys
from datetime import datetime
from multiprocessing import Process, Queue

import grpc
from netifaces import interfaces, ifaddresses, AF_INET
import uptime

from proto import node_pb2
from proto import node_pb2_grpc
from server import *
from node import *
import logger_setting


logger_setting.logger_setting()
logger = logger_setting.logger.getChild(__name__)


def main():
    node_id, node_list = init()
    queue = Queue()
    server_process = Process(target=serve, args=(queue, node_list))
    server_process.start()
    logger.info('Start server_process')
    while True:
        # TODO: queue.get()の内容でgroupingさせる(queueではなくManagerあたりを使ったほうがいいかも検討)
        logger.info(queue.get())


def init():
    logger.info('Initialize Process')
    node_id = create_node_id()
    my_ip = None
    node_list = list()
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

        try:
            res_node_list = throw_add_request(node_id, request_ip, my_ip)
        except grpc.RpcError:
            # ipが無効だったときは独立して単独でクラスタを形成し始める
            node_list.extend(create_node_list(node_id))
        else:
            node_list.extend(res_node_list)

        node_list = grouping(node_list)
        logger.debug(node_list)

    return node_id, node_list


def throw_add_request(node_id, request_ip, my_ip):
    with grpc.insecure_channel(request_ip) as channel:
        stub = node_pb2_grpc.AddRequestServiceStub(channel)
        request_message = node_pb2.AddRequestDef(request_id=create_request_id(), id=node_id, sender_ip=my_ip,
                                                 boot_time=get_boot_unix_time(), time_stamp=get_now_unix_time())
        response = stub.add_request(request_message)
        response_node_list = list()
        for node in response.node_list:
            tmp_node = Node(uid=node.id, ip=node.ip, boot_time=node.boot_time, group_id=node.group_id,
                            is_primary=node.is_primary)
            response_node_list.append(tmp_node.__dict__)
    return response_node_list


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


if __name__ == '__main__':
    main()
