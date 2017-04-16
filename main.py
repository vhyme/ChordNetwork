from time import sleep
from ClientNode import ClientNode, draw_graph, simulate_async_daemon

N0 = ClientNode('N0')
for i in range(1, 64 + 1):
    Ni = ClientNode('N' + str(i))
    Ni.join_network_via_director(N0)

    draw_graph()
    simulate_async_daemon()
    draw_graph()

    # 模拟某些节点掉线
    if i % 9 == 0:
        Ni.cold_offline()
        simulate_async_daemon()
        draw_graph()

print('Saved at', N0.put_resource('Hello.txt2', 'Hello, World'))
print('Saved at', N0.put_resource('Hello2.md', '# This is a Markdown'))
print(N0.get_resource('Hello2.md'))
print(N0.get_resource('Hello.jpg'))
