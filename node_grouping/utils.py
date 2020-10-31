import uuid
import uptime
from datetime import datetime


def create_node_id() -> str:
    return str(uuid.uuid4())


def create_request_id() -> str:
    return str(uuid.uuid4())


def get_boot_unix_time() -> float:
    return uptime.boottime().timestamp()


def get_now_unix_time() -> float:
    return float(datetime.now().strftime('%s'))


def get_my_group_id(nodes, my_id):
    my_group_id = None

    for i in nodes:
        if i['id'] == my_id:
            my_group_id = i['group_id']
            break
    return my_group_id


def get_my_group_node_list(nodes, my_group_id):
    my_group_node_list = list()
    for i in nodes:
        if i['group_id'] == my_group_id:
            my_group_node_list.append(i)
    return my_group_node_list


def get_leader_node_list(nodes):
    leader_node_list = list()
    for i in nodes:
        if i['is_leader'] is True:
            leader_node_list.append(i)
    return leader_node_list


def get_is_leader(nodes, my_id):
    is_leader = False
    for i in nodes:
        if i['id'] == my_id:
            is_leader = i['is_leader']
            break

    return is_leader


def get_is_group_for_ip(nodes, ip):
    is_my_group = False
    for i in nodes:
        if i['ip'] == ip:
            is_my_group = True
            break
    return is_my_group


def get_is_majority(node_list: list, group_num) -> bool:
    if len(node_list) >= group_num:
        count = 0
        for dic in node_list:
            if dic['is_leader'] is True:
                count += 1

        if group_num / 2 + 1 > count:
            return False

    return True

