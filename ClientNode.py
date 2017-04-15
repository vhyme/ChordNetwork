from time import sleep
from queue import Queue
import threading
from Draw import draw
import Config

current_nodes = []


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
    def __init__(self, address=''):
        self.id = 0
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
        current_nodes.append(self)

        print(self, 'Instantiated')
        self.start_daemon()
        sleep(Config.refresh_rate)

    def __str__(self):
        return self.address + '(' + str(self.id) + ')'

    def __repr__(self):
        return self.address

    def get_resource_local(self, key):
        try:
            return self.resources[key]
        except:
            return None

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

        print(self, 'error', self.finger)
        exit(0)

    # 从网络中读取资源,返回一个元组表示存放的节点 id 和资源内容
    def get_resource(self, key):
        key_id = Config.key_to_id(key)

        print(self, 'Called get_resource for', key, '(' + str(key_id) + ')')
        handler = self.find_handler_for_id(key_id)
        return str(handler), handler.get_resource_local(key)

    # 向网络中添加资源,返回存放的节点 id
    def put_resource(self, key, value):
        key_id = Config.key_to_id(key)

        print(self, 'Called put_resource for', key, '(' + str(key_id) + ')')
        handler = self.find_handler_for_id(key_id)
        handler.resources[key] = value
        return str(handler)

    # 加入某个节点所在的网络
    def join_network_via_director(self, director):
        print(self, 'Called join_network_via_director', director)

        handler = director.find_handler_for_id(self.id)
        first_id = self.id
        while handler.id == self.id:
            self.id = (self.id - 1) % Config.capacity
            if first_id == self.id:
                print(self, 'Failed to join network: Network', director, 'is full')
                return
            handler = director.find_handler_for_id(self.id)

        self.successor = handler
        if handler.successor == handler:
            handler.successor = self
        self.update_finger()
        draw_graph()

    # 前驱的 getter
    @property
    def predecessor(self):
        return self._predecessor

    # 每当前驱改变时,输出日志
    @predecessor.setter
    def predecessor(self, value):
        print(self, 'Updating predecessor to', value)
        self._predecessor = value
        self.update_finger()

    # 后继的 getter
    @property
    def successor(self):
        return self._successor

    # 每当后继改变时,更新后继缓存表
    @successor.setter
    def successor(self, value):
        print(self, 'Updating successor to', value)
        self._successor = value
        if value != self:
            self.successors = [self.successor] + self.successor.successors[:Config.cache_length]
        else:
            self.successors = []
        self.update_finger()

    # 更新幂次查询表
    def update_finger(self):
        print(self, 'Updating Finger')
        self.finger = []
        while len(self.finger) < Config.id_length:
            offset_to_find = 2 ** len(self.finger)
            id_to_find = (self.id + offset_to_find) % Config.capacity
            self.finger.append(self.find_handler_for_id(id_to_find))

    # 启动异步监控线程
    def start_daemon(self):
        def daemon():
            while self.daemon_started:
                print(self, 'Daemon Running')
                self.stabilize()
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
        print(self, 'Running stabilization')

        # 检查并修复后继在线状态
        if self.successor != self and not self.successor.partially_online:
            for node in self.successors:
                if node.partially_online:
                    self.successor = node
                    break
            # else:
            #     print('-', 'Node is partially offline, cleaning...')
            #     # 注意这里是 Python for ... else 语法,表示若没有触发 break ,则执行
            #     # 没有触发 break 则表示缓存的后继列表中所有节点均已失效
            #     self.hot_offline()

        # 检查后继的前驱是否为新后继
        if is_clockwise(self.id, self.successor.predecessor.id, self.successor.id):
            print('-', 'Found new successor:', self.successor.predecessor)
            self.successor = self.successor.predecessor

        # 标记是否发现了新前驱
        has_new_node = False

        # 检查并处理其他节点发来的消息
        while self.message_queue.qsize() > 0:
            notifier, new_node = self.message_queue.get()
            if self.predecessor == self or is_clockwise(self.predecessor.id, notifier.id, self.id):
                print('-', 'Found new predecessor:', notifier)
                self.predecessor = notifier

                # 发现新前驱时,进行标记,以便通过消息向后传递
                has_new_node = True
                self.update_finger()
            if new_node:
                self.update_finger()
            self.message_queue.task_done()

        # 让后继检查自己是否为新前驱
        if self.successor != self:
            print('-', 'Sending message to successor:', self.successor)
            self.successor.message_queue.put((self, has_new_node))

    # 热下线,即模拟正常下线情况
    def hot_offline(self):
        print(self, 'Node is offline')
        self.successor.predecessor = self.predecessor
        self.predecessor.successor = self.successor
        self.successor = self
        self.predecessor = self
        self.finger = []
        self.successors = []
        self.message_queue = []

    # 冷下线,即模拟网络断开等强制下线情况
    def cold_offline(self):
        print(self, 'Node is forced offline')
        self.successor = self
        self.predecessor = self
        self.finger = []
        self.successors = []
        self.message_queue = []