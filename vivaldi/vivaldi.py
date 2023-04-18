import numpy as np
from scapy.all import *
import socket
import constants
import sys
import subprocess
import re

class Vivaldi:
        
    def selectnodej():
        #이웃노드 선택(랜덤하게/ 이때 자기 자신과 이미 선택한 이웃노드를 제외)
        while True:
            a=random.randrange(0,80)
            while (100+a in nodej or 100+a == 100+int(port)):
                a=random.randrange(0,80)
            nodej.append(100+a)
            break
        # 좌표가 정해진 노드 목록
        try:
            with open("/app/data/dataoutput.txt", "r") as f:
                datacontents=f.read()
            with open("/app/data/erroroutput.txt", "r") as f:
                errorcontents=f.read()
        except FileNotFoundError:
            with open("/app/data/dataoutput.txt", "w") as f:
                datacontents=[]
            with open("/app/data/erroroutput.txt", "w") as f:
                errorcontents=[]
        #선택한 이웃노드가 좌표가 정해져 있다면 참조
        if "{}{}".format(100+a,"th node")  in datacontents and "{}{}".format(100+a,"th node")  in errorcontents:
            datalines=datacontents.split('}')
            errorlines=errorcontents.split('}')
            for dataline in datalines:
                for errorline in errorlines:
                    if "{}{}".format(100+a,"th node") in dataline and "{}{}".format(100+a,"th node")  in errorline:
                        datakey,datavalue = dataline.split(':')
                        errorkey,errorvalue=errorline.split(':')
                        data=datavalue[7:-2].strip("[]").split(",")
                        xj=[float(x)for x in data]
                        ej=float(errorvalue[2:-1])
            print(a,"node coordinate info",xj)
        #없다면 새로운 값을 부여
        else:
            xj=[0 for i in range(int(sys.argv[1]))]
            ej=1
            print(a,"node coordinate new info",xj)

        return a,xj,ej
    # rtt값 계산
    def ping(host):
        ping_response = subprocess.run(["ping",host,"-c", "5",],capture_output=True,text=True).stdout   
        #print(ping_response)
        pattern = r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms"

        match = re.search(pattern,ping_response)
        if match:
            avg_rtt=float(match.group(1))
            return avg_rtt
        else:
            return 10

    # xi,xj 간의 거리
    def distance(xi, xj):
        sum_of_squares = sum((xi[i] - xj[i])**2 for i in range(len(xi)))
        return math.sqrt(sum_of_squares)

    # 방향 벡터 계산(동일한 위치라면 랜덤하게 방향 부여)
    def unitvector(xi,xj):
        d = Vivaldi.distance(xi, xj)
        unitarray=[]
        if d == 0:
                unitarray.append(np.random.rand(xi.size)*10)
        else:
            for index in range(xi.size):
                unitarray.append((xj[index] - xi[index]) / d)
        return unitarray

    def vivaldi(xi,ei,iter):

        a,xj,ej=Vivaldi.selectnodej()
        xi=np.array(xi)
        xj=np.array(xj)
        rtt=Vivaldi.ping('172.19.0.%d'%(100+a))
        print('172.19.0.%d'%(100+a) ,"rtt:",rtt)

        e =  rtt- abs(np.linalg.norm(xi - xj))
        # Find the direction of the force the error is causing.
        dir = Vivaldi.unitvector(xi,xj)
        # The force vector is proportional to the error.
        if ei==1:
            f = np.multiply(dir[0],e)
        else:
            f = np.multiply(dir,e)
        # Sample weight balances local and remote error.
        w = ei / (ei + ej)
        # Compute relative error of this sample.
        es = abs(abs(np.linalg.norm(xi - xj)) - rtt)/ rtt
        # Update weighted moving average of local error.
        ei = es * constants.ce * w + ei * (1 - constants.ce * w)
        # Update local coordinates.
        delta = constants.cc * w
        xi = xi + delta * f

        if iter != 1:
            iter=iter-1
            return Vivaldi.vivaldi(xi,ei,iter)
            
        else: 
            print(xi)
            return xi,ei

#sys.argv[1]은 차원을 의미하는 인자, sys.argv[2]는 노드 순서를 의미하는 인자  (실행 시 꼭 2개의 인자 전달 할것)
xi=[0 for i in range(int(sys.argv[1]))]
port=sys.argv[2]

datax={}
datae={}
nodej=[]
datax[port],datae[port]=Vivaldi.vivaldi(xi,constants.ei,constants.iter)

#나온 결과 값을 추가해 이웃노드를 참조할 목록 만들기
with open("/app/data/dataoutput.txt", "a") as f:
    print(f" {100+int(port)}th node {datax}",file=f)
with open("/app/data/erroroutput.txt", "a") as f:
    print(f"{100+int(port)}th node {datae}",file=f)
