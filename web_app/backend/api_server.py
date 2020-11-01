from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/api/nodes_status', methods=['get'])
def get_nodes_status():
    node_list = get_node_list()
    return json.dumps(node_list)


def get_node_list():
    # TODO: gRPCで稼働中のノードから受け取る
    node_list = ''
    return node_list


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True, use_reloader=False)
