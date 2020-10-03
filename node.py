class Node:
    def __init__(self, uid, ip, boot_time, group_id=None, is_primary=False, is_me=False):
        self.id = uid
        self.ip = ip
        self.boot_time = boot_time
        self.group_id = group_id
        self.is_primary = is_primary

    def set_ip(self, ip):
        self.ip = ip

    def get_ip(self):
        return self.ip

    def set_group(self, group_id):
        self.group_id = group_id

    def get_group(self):
        pass

    def set_primary_status(self, is_primary: bool):
        self.is_primary = is_primary

    def get_primary_status(self):
        return self.is_primary
