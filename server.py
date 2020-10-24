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

GROUP_NUM = 3


class RequestServiceServicer(node_pb2_grpc.RequestServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def add_request(self, request, context):
        global share_node_list, process_queue

        updated_list = _check_update(process_queue_for_client)
        if updated_list is not None:
            share_node_list = updated_list

        # share_node_list = [{'id': 'aaaaa-aaaaa-aaaaa-aaaaa', 'ip': '192.168.100.1', 'boot_time': 1000000,
        #                    'group_id': 1, 'is_primary': True},
        #                    {'id': 'bbbbb-bbbbb-bbbbb-bbbbb', 'ip': '192.168.100.2', 'boot_time': 2000000,
        #                     'group_id': 2, 'is_primary': True}]

        logger.debug('request: %s', request)
        add_node = Node(uid=request.id, ip=request.sender_ip, boot_time=request.boot_time).__dict__
        share_node_list.append(add_node)
        share_node_list = grouping(share_node_list, GROUP_NUM)
        share_data = {'node_list': share_node_list, 'method': 'add', 'diff_list': [add_node],
                      'is_allow_propagation': True}
        process_queue.put(share_data)
        return node_pb2.AddResponseDef(request_id=request.request_id, node_list=share_node_list,
                                       time_stamp=float(datetime.now().strftime('%s')))

    def update_request(self, request, context):
        global share_node_list, process_queue
        logger.debug('update: %s', request)
        share_data = list()
        if request.method == 'add':
            add_node = Node(uid=request.node_id, ip=request.ip, boot_time=request.boot_time).__dict__
            share_node_list.append(Node(uid=request.node_id, ip=request.ip,
                                        boot_time=request.boot_time).__dict__)
            share_data = {'node_list': share_node_list, 'method': 'add', 'diff_list': [add_node],
                          'is_allow_propagation': False}
        elif request.method == 'del':
            del_node = Node(uid=request.node_id, ip=request.ip, boot_time=request.boot_time).__dict__
            for i, dic in enumerate(share_node_list):
                if dic['id'] == request.node_id:
                    del share_node_list[i]
                    # is_majority = get_is_majority(share_node_list, GROUP_NUM)
                    share_node_list = grouping(share_node_list, GROUP_NUM)
                    share_data = {'node_list': share_node_list, 'method': 'del', 'diff_list': [del_node],
                                  'is_allow_propagation': False}
                    # share_data = {'node_list': share_node_list, 'method': 'del', 'diff_list': [del_node],
                    #               'is_allow_propagation': False, 'is_majority': is_majority}
        else:
            pass

        process_queue.put(share_data)

        return node_pb2.DiffNodeResponseDef(request_id=request.request_id, status='OK',
                                            time_stamp=get_now_unix_time())

    def heartbeat_request(self, request, context):
        global share_node_list, process_queue
        # logger.debug('heartbeat: %s', request)
        # TODO: node_listを参照していなければ通告する
        return node_pb2.HeartBeatResponseDef(request_id=request.request_id, status='heartbeat_response',
                                             time_stamp=get_now_unix_time())

    def request_heartbeat_request(self, request, context):
        global share_node_list, process_queue
        # TODO: 実際にはここで指定されたノードへハートビートを送りその結果をstatusに含めて返す
        return node_pb2.RequestHeartBeatResponseDef(request_id=request.request_id, status='request_heartbeat_response',
                                                    time_stamp=get_now_unix_time())


def serve(q_for_server: object, q_for_client: object, default_node_list: list):
    logger.info('Start server_process')
    global share_node_list, process_queue, process_queue_for_client
    share_node_list = default_node_list
    process_queue = q_for_server
    process_queue_for_client = q_for_client

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    node_pb2_grpc.add_RequestServiceServicer_to_server(RequestServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('Start gRPC Server')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


def _check_update(q):
    try:
        queue_content = q.get(block=False)
    except Empty:
        return None
    else:
        return queue_content['node_list']
