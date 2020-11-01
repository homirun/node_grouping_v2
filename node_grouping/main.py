import sys
from multiprocessing import Process, Queue

from netifaces import ifaddresses, AF_INET

from server import *
from node import *
import logger_setting
from utils import *

GROUP_NUM = 3

logger_setting.logger_setting()
logger = logger_setting.logger.getChild(__name__)
failed_check_dict = dict()
node_status = True


def main():
    global node_status
    node_id, node_list, my_ip = init()
    q_for_server = Queue()
    q_for_client = Queue()
    server_process = Process(target=serve, args=(q_for_server, q_for_client, node_list))
    server_process.start()

    stop_node_list = list()
    count = 0
    is_majority = True

    while True:
        if node_status is True:
            count += 1
            try:
                queue_content = q_for_server.get(block=True, timeout=0.5)
            except Empty:
                pass
            else:
                if queue_content:
                    old_node_list = node_list
                    node_list = queue_content['node_list']
                    node_list = grouping(node_list, GROUP_NUM)
                    # if 'for_primary' in queue_content and queue_content['for_primary'] is True:
                    #     # for_primaryキー存在しかつTrueの際にはPrimaryへは発出しない
                    #     pass
                    # else:
                    if queue_content['method'] == 'del':
                        stop_node_list.append(queue_content['diff_list'][0])
                        for i, dic in enumerate(node_list):
                            if dic['id'] == queue_content['diff_list'][0]['id']:
                                del node_list[i]
                    if queue_content['is_allow_propagation'] is True:
                        throw_update_request_beta(queue_content['method'], queue_content['diff_list'],
                                                  old_node_list, node_id, my_ip)
            finally:
                if count >= 3:
                    count = 0
                    del_node_diff = throw_heartbeat(node_list, stop_node_list, node_id, my_ip)
                    logger.debug('diff %s', del_node_diff)

                    if del_node_diff is False:
                        _down_node(server_process)
                    elif del_node_diff is not None:
                        is_majority = get_is_majority(node_list, GROUP_NUM)
                        node_list = grouping(node_list, GROUP_NUM)
                        share_data = {'node_list': node_list, 'method': 'del', 'diff_list': [del_node_diff]}
                        q_for_client.put(share_data)

                        logger.debug('del %s', del_node_diff)

                # if not is_majority:
                #    _down_node(server_process)

        else:
            leader_node_list = get_leader_node_list(node_list)
            while True:
                # TODO: 復旧するときのリスト配布はタイミングによってうまく行かないことあるので複数回再送するかtime_stampよりあとにjoinしたノードにだけ再送する等考える

                time.sleep(3)
                for dic in leader_node_list:
                    try:
                        logger.info('try rejoin cluster ip: %s', dic['ip'])
                        node_list = grouping(throw_add_request(node_id=node_id, request_ip=dic['ip']+':50051',
                                                               my_ip=my_ip), GROUP_NUM)
                    except grpc.RpcError:
                        pass
                    else:
                        logger.info('rejoin cluster')
                        server_process = Process(target=serve, args=(q_for_server, q_for_client, node_list))
                        server_process.start()
                        node_status = True
                        break
                else:
                    continue
                break


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

        # node_list = grouping(node_list, GROUP_NUM)

    return node_id, node_list, my_ip


def throw_add_request(node_id: str, request_ip: str, my_ip: str) -> list:
    with grpc.insecure_channel(request_ip, options=(('grpc.initial_reconnect_backoff_ms', 500), ('grpc.min_reconnect_backoff_ms', 500))) as channel:
        stub = node_pb2_grpc.RequestServiceStub(channel)
        request_message = node_pb2.AddRequestDef(request_id=create_request_id(), id=node_id, sender_ip=my_ip,
                                                 boot_time=get_boot_unix_time(), time_stamp=get_now_unix_time())
        response = stub.add_request(request_message)
        response_node_list = list()
        for node in response.node_list:
            tmp_node = Node(uid=node.id, ip=node.ip, boot_time=node.boot_time, group_id=node.group_id,
                            is_leader=node.is_leader)
            response_node_list.append(tmp_node.__dict__)
    return response_node_list


def throw_update_request(node_list_diff: list, old_node_list: list):
    pass


def throw_update_request_beta(method: str, node_list_diff: list, old_node_list: list, my_id: str, my_ip: str):
    for node in old_node_list:
        if node['id'] != my_id:
            try:
                with grpc.insecure_channel(node['ip']+':50051', options=(('grpc.initial_reconnect_backoff_ms', 1000), ('grpc.min_reconnect_backoff_ms', 1000))) as channel:
                    stub = node_pb2_grpc.RequestServiceStub(channel)
                    request_message = node_pb2.DiffNodeRequestDef(request_id=create_request_id(), method=method,
                                                                  node_id=node_list_diff[0]['id'],
                                                                  ip=node_list_diff[0]['ip'],
                                                                  boot_time=float(node_list_diff[0]['boot_time']),
                                                                  sender_ip=my_ip,
                                                                  time_stamp=get_now_unix_time())
                    logger.debug('throw_update_ip: %s', node['ip'])
                    response = stub.update_request(request_message)
            except grpc.RpcError as e:
                logger.error('gRPC Error Message: %s', e)


def throw_heartbeat(node_list: list, stop_node_list: list, my_id: str, my_ip: str):
    group_node_list = get_my_group_node_list(node_list, get_my_group_id(node_list, my_id))
    if get_is_leader(node_list, my_id):
        group_node_list.extend(get_leader_node_list(node_list))

    for node in group_node_list:
        if node['id'] != my_id:
            try:
                with grpc.insecure_channel(node['ip']+':50051', options=(('grpc.initial_reconnect_backoff_ms', 500), ('grpc.min_reconnect_backoff_ms', 500))) as channel:
                    stub = node_pb2_grpc.RequestServiceStub(channel)
                    request_message = node_pb2.HeartBeatRequestDef(request_id=create_request_id(), status='heartbeat',
                                                                   time_stamp=get_now_unix_time())
                    logger.debug('throw_heartbeat_ip: %s', node['ip'])
                    response = stub.heartbeat_request(request_message)
            except grpc.RpcError:
                logger.error('Connection Failed: %s', node)
                if node['id'] in failed_check_dict and failed_check_dict[node['id']] <= 1:
                    failed_check_dict[node['id']] += 1
                    logger.debug('increment %s', failed_check_dict[node['id']])
                elif node['id'] in failed_check_dict and failed_check_dict[node['id']] >= 2:
                    # TODO: ネットワーク分断か判定を入れる
                    # 再groupingする前に判定してノードリストから削除するのかそれとも過半数チェックするかを確認
                    if request_heartbeat_for_leader(node_list, node, my_id):
                        for i, dic in enumerate(node_list):
                            if dic['id'] == node['id']:
                                del node_list[i]

                        stop_node_list.append(node)
                        throw_update_request_beta(method='del', node_list_diff=[node], old_node_list=node_list,
                                                  my_id=my_id, my_ip=my_ip)
                        return node
                    else:
                        return False
                else:
                    failed_check_dict[node['id']] = 1
                    return None


def request_heartbeat_for_leader(node_list: list, check_node, my_id: str) -> bool:
    leader_node_list = get_leader_node_list(node_list)
    failed_response_list = list()
    for dic in leader_node_list:
        if dic['id'] != my_id:
            try:
                with grpc.insecure_channel(dic['ip']+':50051', options=(('grpc.initial_reconnect_backoff_ms', 500), ('grpc.min_reconnect_backoff_ms', 500))) as channel:
                    stub = node_pb2_grpc.RequestServiceStub(channel)
                    request_message = node_pb2.RequestHeartBeatRequestDef(request_id=create_request_id(),
                                                                          destination_node_id=check_node['id'],
                                                                          time_stamp=get_now_unix_time())
                    logger.debug('request_heartbeat_for_leader ip: %s, check: %s', dic['ip'], check_node['ip'])
                    response = stub.request_heartbeat_request(request_message)
            except grpc.RpcError:
                logger.error('failed request_heartbeat_for_leader ip: %s', dic['ip'])
                failed_response_list.append(dic['id'])

    print(failed_response_list)
    if len(failed_response_list) >= (int(GROUP_NUM / 2) + 1):
        return False

    return True


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


def _down_node(server_process):
    global node_status
    logger.error('Less than half of leader nodes')
    logger.info('Node status: False')
    # TODO: .close()やexit()から再復帰処理へ置き換える
    # TODO: node_status is falseのときはthrow_add_requestをつかって自分のノード情報だけを送信する. node_listを削除する.
    node_status = False
    server_process.terminate()
    # exit()


if __name__ == '__main__':
    main()
