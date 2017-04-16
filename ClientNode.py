from time import sleep
from queue import Queue
import threading
from Draw import draw
import Config

current_nodes = []


def simulate_async_daemon():
    for k in range(0, len(current_nodes)):
        for node in current_nodes:
            node.stabilize()


def draw_graph():
    draw(current_nodes)


def is_clockwise(id1, id2, id3):
    count = 0
    if id1 < id2:
        count += 1
    if id2 < id3:
        count += 1
    if id3 < id1:
        count += 1
    return count == 2


class ClientNode:
    # 初始化节点并开始运行
    def __init__(self, address='', async=False):
        self.id = 0
        self.async = async
        if address != '':
            self.id = Config.address_to_id(address)
        self.address = address
        self.resources = {}
        self._successor = self
        self._predecessor = self
        self.finger = []
        self.successors = []
        self.message_queue = Queue()
        self.daemon_started = False
        self.io_lock = False
        current_nodes.append(self)

        if Config.verbose:
            print(self, 'Instantiated')
        if self.async:
            self.start_daemon()
            sleep(Config.refresh_rate)

    def __str__(self):
        return self.address + '(' + str(self.id) + ')'

    def __repr__(self):
        return self.address

    def get_resource_local(self, key):
        try:
            return {
                'physical_holder': str(self),
                'data': self.resources[key]
            }
        except:
            if self.io_lock:
                return None
            self.io_lock = True
            resource = self.predecessor.get_resource_local(key)
            self.io_lock = False
            return resource

    # 判断是否在线
    @property
    def fully_online(self):
        # 只要同一网络中有其它节点,视为在线;否则视为不在线
        return self.successor != self and self.predecessor != self

    # 判断是否在线
    @property
    def partially_online(self):
        # 只要同一网络中有其它节点,视为在线;否则视为不在线
        return self.successor != self or self.predecessor != self

    # 判断某一资源 id 是否归本节点存储
    def should_handle_resource(self, resource_id):
        return self.id == resource_id \
               or self.id == self.predecessor.id \
               or is_clockwise(self.predecessor.id, resource_id, self.id)

    # 查找某个 id 对应的节点或其后继
    def find_handler_for_id(self, _id):
        if self.should_handle_resource(_id):
            return self

        if self.successor.should_handle_resource(_id):
            return self.successor

        for node in reversed(self.finger):
            if is_clockwise(self.id, node.id, _id):
                return node.find_handler_for_id(_id)

        print(self, 'Error', self.finger)
        exit(0)

    # 从网络中读取资源,返回一个元组表示存放的节点 id 和资源内容
    def get_resource(self, key):
        key_id = Config.key_to_id(key)
        handler = self.find_handler_for_id(key_id)
        return 'GET', {
            'key': key,
            'logical_holder': str(handler),
            'result': handler.get_resource_local(key)
        }

    # 向网络中添加资源,返回存放的节点 id
    def put_resource(self, key, value):
        key_id = Config.key_to_id(key)
        handler = self.find_handler_for_id(key_id)
        handler.resources[key] = value
        return 'PUT', {
            'key': key,
            'holder': str(handler)
        }

    # 加入某个节点所在的网络
    def join_network_via_director(self, director):
        if Config.verbose:
            print(self, 'Called join_network_via_director', director)

        if self.async:
            sleep(Config.refresh_rate)
        handler = director.find_handler_for_id(self.id)
        first_id = self.id
        while handler.id == self.id:
            self.id = (self.id - 1) % Config.capacity
            if first_id == self.id:
                if Config.verbose:
                    print(self, 'Failed to join network: Network', director, 'is full')
                return
            handler = director.find_handler_for_id(self.id)

        self.successor = handler
        if handler.successor == handler:
            handler.successor = self
        # draw_graph()

    # 前驱的 getter
    @property
    def predecessor(self):
        return self._predecessor

    # 每当前驱改变时,输出日志
    @predecessor.setter
    def predecessor(self, value):
        if Config.verbose:
            print(self, 'Updating predecessor to', value)
        self._predecessor = value

    # 后继的 getter
    @property
    def successor(self):
        return self._successor

    # 每当后继改变时,更新后继缓存表
    @successor.setter
    def successor(self, value):
        if Config.verbose:
            print(self, 'Updating successor to', value)
        self._successor = value

    # 更新幂次查询表
    def update_finger(self):
        next_finger = self.successor
        step = 1
        self.finger = [next_finger]
        while len(self.finger) < Config.id_length:
            for k in range(0, step):
                next_finger = next_finger.successor
            self.finger.append(next_finger)
            step *= 2

    # 启动异步监控线程
    def start_daemon(self):
        def daemon():
            while self.daemon_started:
                if Config.verbose:
                    print(self, 'Daemon Running')
                self.stabilize()
                if Config.verbose:
                    print(self, 'Daemon Sleeping')
                    print('')
                sleep(Config.refresh_rate)

        self.daemon_started = True
        thread = threading.Thread(target=daemon)
        thread.setDaemon(True)
        thread.start()

    # 停止异步监控线程
    def stop_daemon(self):
        self.daemon_started = False

    # 定期执行的稳定化调整
    def stabilize(self):

        # 检查并修复后继在线状态
        if self.successor != self:
            if self.successor.partially_online:
                # 检查后继的前驱是否为新后继
                if is_clockwise(self.id, self.successor.predecessor.id, self.successor.id)\
                        and self.successor.predecessor.partially_online:
                    if Config.verbose:
                        print('-', 'Found new successor:', self.successor.predecessor)
                    self.successor = self.successor.predecessor
                self.successor.message_queue.put(self)

            # 检查并修复后继在线状态
            else:
                for node in self.successors:
                    if node.partially_online:
                        self.successor = node
                        break

            self.successors = [self.successor] + self.successor.successors[:Config.cache_length]
        else:
            self.successors = []

        self.update_finger()

        # 检查并处理其他节点发来的消息
        while self.message_queue.qsize() > 0:
            notifier = self.message_queue.get()
            if (self.predecessor == self
                or not self.predecessor.partially_online
                or is_clockwise(self.predecessor.id, notifier.id, self.id))\
                    and notifier.partially_online:
                if Config.verbose:
                    print('-', 'Found new predecessor:', notifier)
                self.predecessor = notifier

                self.update_finger()
            self.message_queue.task_done()

    # 热下线,即模拟正常下线情况
    def hot_offline(self):
        if Config.verbose:
            print(self, 'Node is offline')
        self.successor.predecessor = self.predecessor
        self.predecessor.successor = self.successor
        self.successor = self
        self.predecessor = self
        self.finger = []
        self.successors = []
        self.message_queue = Queue()

    # 冷下线,即模拟网络断开等强制下线情况
    def cold_offline(self):
        if Config.verbose:
            print(self, 'Node is forced offline')
        self.successor = self
        self.predecessor = self
        self.finger = []
        self.successors = []
        self.message_queue = Queue()
