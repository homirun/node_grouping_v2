import grpc
from proto import node_pb2
from proto import node_pb2_grpc
from concurrent import futures
import time
from datetime import datetime

import logger_setting
from node import *

logger = logger_setting.logger.getChild(__name__)
share_node_list = list()
process_queue = None


class RequestServiceServicer(node_pb2_grpc.RequestServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def add_request(self, request, context):
        global share_node_list, process_queue

        # share_node_list = [{'id': 'aaaaa-aaaaa-aaaaa-aaaaa', 'ip': '192.168.100.1', 'boot_time': 1000000,
        #                    'group_id': 1, 'is_primary': True},
        #                    {'id': 'bbbbb-bbbbb-bbbbb-bbbbb', 'ip': '192.168.100.2', 'boot_time': 2000000,
        #                     'group_id': 2, 'is_primary': True}]

        logger.debug('request: %s', request)

        share_node_list.append(Node(uid=request.id, ip=request.sender_ip, boot_time=request.boot_time).__dict__)
        process_queue.put(share_node_list)
        return node_pb2.AddResponseDef(request_id=request.request_id, node_list=share_node_list,
                                       time_stamp=float(datetime.now().strftime('%s')))


def serve(queue, default_node_list):
    global share_node_list, process_queue
    share_node_list = default_node_list
    process_queue = queue

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
