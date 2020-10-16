import sys
from multiprocessing import Process, Queue

from netifaces import ifaddresses, AF_INET

from server import *
from node import *
import logger_setting
from utils import *


logger_setting.logger_setting()
logger = logger_setting.logger.getChild(__name__)


def main():
    node_id, node_list, my_ip = init()
    queue = Queue()
    server_process = Process(target=serve, args=(queue, node_list))
    server_process.start()
    logger.info('Start server_process')
    while True:
        queue_content = queue.get()

        old_node_list = node_list
        node_list = queue_content['node_list']
        node_list = grouping(node_list)
        # if 'for_primary' in queue_content and queue_content['for_primary'] is True:
        #     # for_primaryキー存在しかつTrueの際にはPrimaryへは発出しない
        #     pass
        # else:
        if queue_content['is_allow_propagation'] is True:
            throw_update_request_beta(queue_content['method'], queue_content['diff_list'],
                                      old_node_list, node_id, my_ip)


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

    return node_id, node_list, my_ip


def throw_add_request(node_id: str, request_ip: str, my_ip: str) -> list:
    with grpc.insecure_channel(request_ip) as channel:
        stub = node_pb2_grpc.RequestServiceStub(channel)
        request_message = node_pb2.AddRequestDef(request_id=create_request_id(), id=node_id, sender_ip=my_ip,
                                                 boot_time=get_boot_unix_time(), time_stamp=get_now_unix_time())
        response = stub.add_request(request_message)
        response_node_list = list()
        for node in response.node_list:
            tmp_node = Node(uid=node.id, ip=node.ip, boot_time=node.boot_time, group_id=node.group_id,
                            is_primary=node.is_primary)
            response_node_list.append(tmp_node.__dict__)
    return response_node_list


def throw_update_request(node_list_diff: list, old_node_list: list):
    pass


def throw_update_request_beta(method: str, node_list_diff: list, old_node_list: list, my_id, my_ip):
    for node in old_node_list:
        if node['id'] != my_id:
            with grpc.insecure_channel(node['ip']+':50051') as channel:
                stub = node_pb2_grpc.RequestServiceStub(channel)
                request_message = node_pb2.DiffNodeRequestDef(request_id=create_request_id(), method=method,
                                                              node_id=node_list_diff[0]['id'], ip=node_list_diff[0]['ip'],
                                                              boot_time=float(node_list_diff[0]['boot_time']), sender_ip=my_ip,
                                                              time_stamp=get_now_unix_time())
                response = stub.update_request(request_message)


def throw_heartbeat():
    pass


def create_node_list(my_node_id: str) -> list:
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



if __name__ == '__main__':
    main()
