#!/usr/bin/python

import os
import _thread
import time
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

#SET NETWORK TOPOLOGY


setLogLevel('info')

net = Containernet(controller=Controller)

info('*** Adding controller\n')
net.addController('c0')

N = 80 
d = []
for i in range(N):
    d.append(net.addDocker('d%s'%i,ip='172.19.0.%s'%(100+i), volumes=['myvolume:/app/data'], dimage="vivaldi:latest"))

info('*** Adding switches\n')
S = 11
s = []
for i in range(S):
    s.append(net.addSwitch('s%s'%i))

info('*** Creating links\n')
bw = 50 
net.addLink(s[0], s[2], cls=TCLink, delay='2ms', bw=1000)
net.addLink(s[1], s[2], cls=TCLink, delay='4ms', bw=1000) #v3,5 => 4, v6 => 10
net.addLink(s[2], s[5], cls=TCLink, delay='8ms', bw=1000)
net.addLink(s[2], s[4], cls=TCLink, delay='10ms', bw=1000)
net.addLink(s[4], s[6], cls=TCLink, delay='7ms', bw=1000)
net.addLink(s[3], s[6], cls=TCLink, delay='12ms', bw=1000)
net.addLink(s[6], s[7], cls=TCLink, delay='6ms', bw=1000) #v3 => 3,  v5 => 10, 
net.addLink(s[4], s[8], cls=TCLink, delay='8ms', bw=1000) #v3,5,6 => 8, v7 => 15
net.addLink(s[6], s[9], cls=TCLink, delay='5ms', bw=1000)
net.addLink(s[4], s[10], cls=TCLink, delay='3ms', bw=1000)

net.addLink(s[0], d[0])

for i in range(1, N): 
    if i % 8== 0:
        net.addLink(s[1], d[i])
    elif i % 8 == 1 :
        net.addLink(s[9], d[i])
    elif i % 8 == 2:
        net.addLink(s[8], d[i])
    elif i % 8 == 3 :
        net.addLink(s[5], d[i])
    elif i % 8 == 4 :
        net.addLink(s[3], d[i])
    elif i % 8 == 5 :
        net.addLink(s[7], d[i])
    elif i % 8 == 6 :
        net.addLink(s[10], d[i])
    elif i % 8 == 7 :
        net.addLink(s[0], d[i])

# 인터페이스가 생성된 뒤에 ip 할당이 필요
for i in range(N):
    d[i].cmd('ifconfig d' + str(i) + '-eth0 172.19.0.' + str(100+i) +' netmask 255.0.0.0')
    
info('*** Starting network\n')
net.start()

info('*** Testing connectivity\n')

net.ping([d[1], d[3]])
net.ping([d[26], d[49]])

# EXECUTE PEER NODES
#2,4번째 인자에 의해 차원이 결정됨.
def exec_nodes(i) :
    os.system('docker exec mn.d%s python3 ./vivaldi.py %s %s >> ./vivaldi_log_%s.txt'%(i,6,i,6)) # execute validator
#2,4번째 인자를 바꿀 때 해당 숫자를 바꿔줘여함.
os.system('touch ./vivaldi_log_6.txt')
for i in range(N):
    exec_nodes(i)

info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()

 