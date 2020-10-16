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


def get_primary_node_list(nodes):
    primary_node_list = list()
    for i in nodes:
        if i['is_primary'] is True:
            primary_node_list.append(i)
    return primary_node_list


def get_is_primary(nodes, my_id):
    is_primary = False
    for i in nodes:
        if i['id'] == my_id:
            is_primary = i['is_primary']
            break

    return is_primary


def get_is_group_for_ip(nodes, ip):
    is_my_group = False
    for i in nodes:
        if i['ip'] == ip:
            is_my_group = True
            break
    return is_my_group

