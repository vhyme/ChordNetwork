import Config
from ClientNode import ClientNode, draw_graph, simulate_async_daemon

N0 = ClientNode('N0')
for i in range(1, Config.capacity + 1):
    Ni = ClientNode('N' + str(i))
    Ni.join_network_via_director(N0)

    draw_graph()
    simulate_async_daemon()
    draw_graph()

    # 模拟某些节点掉线
    if i % 5 == 0:
        Ni.cold_offline()
        draw_graph()
        simulate_async_daemon()
        draw_graph()

print('Saved at', N0.put_resource('Hello.txt', 'Hello, World'))
print('Saved at', N0.put_resource('Hello.md', '# This is a Markdown'))
print(N0.get_resource('Hello.md'))
print(N0.get_resource('Hello.jpeg'))
print(N0.get_resource('Hello.txt'))

draw_graph()
