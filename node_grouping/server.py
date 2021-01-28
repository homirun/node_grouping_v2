from concurrent import futures
from queue import Empty

import grpc

from proto import node_pb2
from proto import node_pb2_grpc
from node import *
from utils import *
# from main import GROUP_NUM

logger = logger_setting.logger.getChild(__name__)
share_node_list = list()
process_queue = None
process_queue_for_client = None
node_list_history = list()

GROUP_NUM = 3


class RequestServiceServicer(node_pb2_grpc.RequestServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def add_request(self, request, context):
        global share_node_list, process_queue

        updated_list = _check_update(process_queue_for_client, share_node_list)
        if updated_list is not None:
            share_node_list = updated_list

        # share_node_list = [{'id': 'aaaaa-aaaaa-aaaaa-aaaaa', 'ip': '192.168.100.1', 'boot_time': 1000000,
        #                    'group_id': 1, 'is_primary': True},
        #                    {'id': 'bbbbb-bbbbb-bbbbb-bbbbb', 'ip': '192.168.100.2', 'boot_time': 2000000,
        #                     'group_id': 2, 'is_primary': True}]

        logger.debug('request: %s', request)
        add_node = Node(uid=request.id, ip=request.sender_ip, boot_time=request.boot_time).__dict__
        add_list_flag = True
        for dic in share_node_list:
            if dic['id'] == request.id:
                add_list_flag = False
        if add_list_flag:
            share_node_list.append(add_node)
            share_node_list = grouping(share_node_list, GROUP_NUM)
            share_data = {'node_list': share_node_list, 'method': 'add', 'diff_list': [add_node],
                          'is_allow_propagation': True, 'request': 'add', 'time_stamp': request.time_stamp}
            # _manage_node_list_history(share_data, request.time_stamp)
            process_queue.put(share_data)

        return node_pb2.AddResponseDef(request_id=request.request_id, node_list=share_node_list,
                                       time_stamp=get_now_unix_time())

    def update_request(self, request, context):
        global share_node_list, process_queue, process_queue_for_client
        updated_list = _check_update(process_queue_for_client, share_node_list)
        if updated_list is not None:
            share_node_list = updated_list

        logger.debug('update: %s', request)
        share_data = list()
        if request.method == 'add':
            add_node = Node(uid=request.node_id, ip=request.ip, boot_time=request.boot_time).__dict__
            add_list_flag = True
            for dic in share_node_list:
                if dic['id'] == request.node_id:
                    add_list_flag = False
            if add_list_flag:
                share_node_list.append(Node(uid=request.node_id, ip=request.ip,
                                            boot_time=request.boot_time).__dict__)
                share_data = {'node_list': share_node_list, 'method': 'add', 'diff_list': [add_node],
                              'is_allow_propagation': False, 'request': 'update', 'time_stamp': request.time_stamp}
                process_queue.put(share_data)

        elif request.method == 'del':
            del_node = Node(uid=request.node_id, ip=request.ip, boot_time=request.boot_time).__dict__
            for i, dic in enumerate(share_node_list):
                if dic['id'] == request.node_id:
                    del share_node_list[i]
                    # is_majority = get_is_majority(share_node_list, GROUP_NUM)
                    share_node_list = grouping(share_node_list, GROUP_NUM)
                    share_data = {'node_list': share_node_list, 'method': 'del', 'diff_list': [del_node],
                                  'is_allow_propagation': False, 'request': 'update', 'time_stamp': request.time_stamp}
                    # share_data = {'node_list': share_node_list, 'method': 'del', 'diff_list': [del_node],
                    #               'is_allow_propagation': False, 'is_majority': is_majority}
                    process_queue.put(share_data)
        else:
            pass

        # _manage_node_list_history(share_data, request.time_stamp)

        return node_pb2.DiffNodeResponseDef(request_id=request.request_id, status='OK',
                                            time_stamp=get_now_unix_time())

    def heartbeat_request(self, request, context):
        global share_node_list, process_queue, process_queue_for_client
        updated_list = _check_update(process_queue_for_client, share_node_list)
        if updated_list is not None:
            share_node_list = updated_list

        # logger.debug('heartbeat: %s', request)
        # TODO: node_listを参照していなければ通告する
        # for dic in share_node_list:
        #     if dic['id'] == request.
        return node_pb2.HeartBeatResponseDef(request_id=request.request_id, status='heartbeat_response',
                                             time_stamp=get_now_unix_time())

    def request_heartbeat_request(self, request, context):
        global share_node_list, process_queue, process_queue_for_client
        updated_list = _check_update(process_queue_for_client, share_node_list)
        if updated_list is not None:
            share_node_list = updated_list

        # TODO: 実際にはここで指定されたノードへハートビートを送りその結果をstatusに含めて返す
        return node_pb2.RequestHeartBeatResponseDef(request_id=request.request_id, status='request_heartbeat_response',
                                                    time_stamp=get_now_unix_time())

    def nodes_status_request(self, request, context):
        global share_node_list
        return node_pb2.AddResponseDef(request_id=request.request_id, node_list=share_node_list,
                                       time_stamp=get_now_unix_time())


def serve(q_for_server: object, q_for_client: object, default_node_list: list):
    logger.info('Start server_process')
    global share_node_list, process_queue, process_queue_for_client
    share_node_list = default_node_list
    process_queue = q_for_server
    process_queue_for_client = q_for_client

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
    node_pb2_grpc.add_RequestServiceServicer_to_server(RequestServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('Start gRPC Server')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


def _check_update(q, node_list):
    try:
        queue_content = q.get(block=False)
    except Empty:
        return None
    else:
        if queue_content['method'] == 'add':
            add_node = Node(uid=queue_content['diff_list'][0]['id'], ip=queue_content['diff_list'][0]['ip'],
                            boot_time=queue_content['diff_list'][0]['boot_time']).__dict__
            add_list_flag = True
            for dic in node_list:
                if dic['id'] == queue_content['diff_list'][0]['id']:
                    add_list_flag = False
            if add_list_flag:
                node_list.append(add_node)
                node_list = grouping(node_list, GROUP_NUM)
        elif queue_content['method'] == 'del':
            del_node = Node(uid=queue_content['diff_list'][0]['id'], ip=queue_content['diff_list'][0]['ip'],
                            boot_time=queue_content['diff_list'][0]['boot_time']).__dict__
            for i, dic in enumerate(node_list):
                if dic['id'] == queue_content['diff_list'][0]['id']:
                    del node_list[i]
                    # is_majority = get_is_majority(share_node_list, GROUP_NUM)
                    node_list = grouping(node_list, GROUP_NUM)

    return node_list


def _manage_node_list_history(share_data, time_stamp):
    global node_list_history
    share_data['time_stamp'] = time_stamp
    if len(node_list_history) > 0:
        node_list_history = sorted(node_list_history, key=lambda x: x['time_stamp'])
    flag = False
    for dic in node_list_history:
        if dic['time_stamp'] >= time_stamp:
            flag = True
            break

    node_list_history.append(share_data)

    if flag:
        _apply_history()

    if len(node_list_history) >= 4:
        node_list_history.pop(0)


def _apply_history():
    global node_list_history, share_node_list
    for share_data in node_list_history:
        process_queue.put(share_data)
        if share_data['method'] == 'add':
            add_node = Node(uid=share_data['diff_list'][0]['id'], ip=share_data['diff_list'][0]['ip'],
                            boot_time=share_data['diff_list'][0]['boot_time']).__dict__
            add_list_flag = True
            for dic in share_node_list:
                if dic['id'] == share_data['diff_list'][0]['id']:
                    add_list_flag = False
            if add_list_flag:
                share_node_list.append(add_node)
                share_node_list = grouping(share_node_list, GROUP_NUM)
        elif share_data['method'] == 'del':
            del_node = Node(uid=share_data['diff_list'][0]['id'], ip=share_data['diff_list'][0]['ip'],
                            boot_time=share_data['diff_list'][0]['boot_time']).__dict__
            for i, dic in enumerate(share_node_list):
                if dic['id'] == share_data['diff_list'][0]['id']:
                    del share_node_list[i]
                    # is_majority = get_is_majority(share_node_list, GROUP_NUM)
                    share_node_list = grouping(share_node_list, GROUP_NUM)

