from subprocess import Popen
import sys


def main():
    arg = sys.argv
    node_num = arg[1]
    proc1, proc2 = start_network_partition(int(node_num))
    print(proc1)
    print(proc2)
    # stop_network_partition(proc1, proc2)


def start_network_partition(node_num):
    ip_list1 = []
    hostname_list1 = []
    ip_list2 = []
    hostname_list2 = []
    base_cmd1 = 'pumba netem --duration 330s'
    base_cmd2 = 'pumba netem --duration 330s'
    for i in range(1, int(node_num / 2) + 1):
        ip_list1.append('172.16.124.' + str(i))
        hostname_list1.append('node' + str(i))

    for i in range(int(node_num / 2) + 1, node_num + 1):
        ip_list2.append('172.16.124.' + str(i))
        hostname_list2.append('node' + str(i))

    for ip in ip_list1:
        base_cmd1 = base_cmd1 + ' -target ' + ip + '/32'

    for ip in ip_list2:
        base_cmd2 = base_cmd2 + ' -target ' + ip + '/32'

    base_cmd1 += ' loss -p 100'
    base_cmd2 += ' loss -p 100'

    for hostname in hostname_list1:
        base_cmd2 = base_cmd2 + ' ' + hostname

    for hostname in hostname_list2:
        base_cmd1 = base_cmd1 + ' ' + hostname

    return base_cmd1, base_cmd2

    # proc1 = Popen('pumba netem --duration 330s -target 172.16.124.1/32 -target 172.16.124.2/32 -target 172.16.124.3/32'
    #               ' -target 172.16.124.4/32  -target 172.16.124.5/32 loss -p 100 node6 node7 node8 node9 node10',
    #               shell=True)
    # proc2 = Popen('pumba netem --duration 330s -target 172.16.124.6/32 -target 172.16.124.7/32 -target 172.16.124.8/32'
    #               ' -target 172.16.124.9/32  -target 172.16.124.10/32 loss -p 100 node1 node2 node3 node4 node5',
    #               shell=True)
    # return proc1, proc2


def stop_network_partition(proc1, proc2):
    try:
        proc1.terminate()
        proc2.terminate()
    except Exception as e:
        return 'error'

    return 'success! stop network partition'


if __name__ == '__main__':
    main()
