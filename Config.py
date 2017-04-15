from hashlib import md5

id_length = 6
cache_length = 6
capacity = 2 ** id_length  # 此行不可修改
refresh_rate = 0.6


def my_hash(string):
    string = str(md5(string.encode('utf-8')))
    result = 0
    for char in string:
        result += ord(char)
    return result


# 此处可指定将节点地址映射到节点 id 的哈希函数
def address_to_id(address):
    return my_hash(address) % capacity


# 此处可指定将资源 key 映射到资源 id 的哈希函数
def key_to_id(key):
    return my_hash(key) % capacity
