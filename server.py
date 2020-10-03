import grpc
from proto import node_pb2
from proto import node_pb2_grpc
from concurrent import futures
import time


class AddRequestServiceServicer(node_pb2_grpc.AddRequestServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def add_request(self, request, context):
        dummy_node_list = [{'id': 'aaaaa-aaaaa-aaaaa-aaaaa', 'ip': '192.168.100.1', 'boot_time': 1000000, 'group_id': 1,
                            'is_primary': True},
                           {'id': 'bbbbb-bbbbb-bbbbb-bbbbb', 'ip': '192.168.100.2', 'boot_time': 2000000, 'group_id': 2,
                            'is_primary': True},
                           ]

        print(request.request_id)
        return node_pb2.AddResponseDef(request_id=request.request_id, node_list=dummy_node_list, time_stamp=3000000)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    node_pb2_grpc.add_AddRequestServiceServicer_to_server(AddRequestServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Start gRPC Server')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
