from time import sleep
from ClientNode import ClientNode
# from Draw import draw

N1 = ClientNode('N1')
N2 = ClientNode('N2')
N1.join_network_via_director(N2)
N3 = ClientNode('N3')
N3.join_network_via_director(N2)

sleep(3)

print(N1.id, N2.id, N3.id)

print('Saved at', N2.put_resource('Hello.txt2', 'Hello, World'))
print('Saved at', N2.put_resource('Hello2.md', '# This is a Markdown'))
print(N1.get_resource('Hello2.md'))
print(N3.get_resource('Hello.jpg'))
