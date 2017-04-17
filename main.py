import Config
from ClientNode import ClientNode, draw_graph, thread_wait

N0 = ClientNode('N0')
for i in range(1, Config.capacity + 1):
    Ni = ClientNode('N' + str(i))
    Ni.join_network_via_director(N0)
    print(N0.put_resource('Hello' + str(i) + '.ini', '[HELLO]\nindex=' + str(i)))

    draw_graph()
    thread_wait()
    draw_graph()

    # 模拟某些节点掉线
    if i % 5 == 0:
        Ni.cold_offline()
        draw_graph()
        thread_wait()
        draw_graph()

print(N0.put_resource('Hello.txt', 'Hello, World'))
print(N0.put_resource('Hello.md', '# This is a Markdown'))
print(N0.get_resource('Hello.md'))
print(N0.get_resource('Hello.jpeg'))
print(N0.get_resource('Hello.txt'))
print(N0.get_resource('Hello12.ini'))
print(N0.get_resource('Hello7.ini'))

draw_graph()
