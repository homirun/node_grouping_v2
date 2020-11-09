import json
from subprocess import Popen

import requests
from flask import Flask

app = Flask(__name__)
proc1 = None
proc2 =None


@app.route('/nodes_status', methods=['get'])
def nodes_status():
    r = requests.get('localhost:5000')
    return json.dumps(r.json())


@app.route('/network_partition/start', methods=['get'])
def start_network_partition():
    global proc1, proc2
    proc1 = Popen('pumba netem --duration 330s -target 172.16.124.1/32 -target 172.16.124.2/32 -target 172.16.124.3/32'
                  ' -target 172.16.124.4/32  -target 172.16.124.5/32 loss -p 100 node6 node7 node8 node9 node10',
                  shell=True)
    proc2 = Popen('pumba netem --duration 330s -target 172.16.124.6/32 -target 172.16.124.7/32 -target 172.16.124.8/32'
                  ' -target 172.16.124.9/32  -target 172.16.124.10/32 loss -p 100 node1 node2 node3 node4 node5',
                  shell=True)

    return 'success! start network partition'


@app.route('/network_partition/stop', methods=['get'])
def stop_network_partition():
    global proc1, proc2
    try:
        proc1.terminate()
        proc2.terminate()
    except Exception as e:
        return 'error'

    return 'success! stop network partition'


if __name__ == '__main__':
    app.run('0.0.0.0', port=5500, debug=True, use_reloader=False)
