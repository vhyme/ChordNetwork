from time import sleep
from ClientNode import ClientNode, draw_graph

N1 = ClientNode('N1')
N2 = ClientNode('N2')
N1.join_network_via_director(N2)
N3 = ClientNode('N3')
N3.join_network_via_director(N2)
N4 = ClientNode('N4')
N4.join_network_via_director(N1)

for i in range(5, 64 + 1):
    Ni = ClientNode('N' + str(i))
    Ni.join_network_via_director(N4)
draw_graph()

print('Saved at', N2.put_resource('Hello.txt2', 'Hello, World'))
print('Saved at', N2.put_resource('Hello2.md', '# This is a Markdown'))
print(N1.get_resource('Hello2.md'))
print(N3.get_resource('Hello.jpg'))
