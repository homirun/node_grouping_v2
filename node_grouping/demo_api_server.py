import json
import sys

from flask import Flask, request
import grpc

from proto import node_pb2
from proto import node_pb2_grpc
from utils import *
from node import *

app = Flask(__name__)


@app.route('/api/nodes_status', methods=['get'])
def nodes_status():
    node_list = get_node_list()
    return json.dumps(node_list)


def get_node_list():
    # TODO: gRPCで稼働中のノードから受け取る
    request_ip = '172.16.124.1'
    with grpc.insecure_channel(request_ip + ':50051') as channel:
        stub = node_pb2_grpc.RequestServiceStub(channel)
        request_message = node_pb2.AddRequestDef(request_id=create_request_id(), time_stamp=get_now_unix_time())
        response = stub.nodes_status_request(request_message)
    response_node_list = list()
    for node in response.node_list:
        tmp_node = Node(uid=node.id, ip=node.ip, boot_time=node.boot_time, group_id=node.group_id,
                        is_leader=node.is_leader)
        response_node_list.append(tmp_node.__dict__)
    return response_node_list


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True, use_reloader=False)
