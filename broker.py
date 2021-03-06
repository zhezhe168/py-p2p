import socket
import gevent
import json
import time
import random
import gevent.monkey

gevent.monkey.patch_all()


class Registry:
    def __init__(self):
        self._registry=[]
    
    def notify_all(self,data):
        for i,r in enumerate(self._registry):
            if r.get("connection"):
                try:
                    r['connection'].sendall(data)
                except Exception as e:
                    print "notify node failure",r,str(e)
                    self._registry.pop(i)
                    continue
                    
    

                
    def add_node(self,connection,address):
        _node=self.find_node(address)
        if _node:
            print "node already in registry",_node
            return
        
        r={"connection":connection,
           "address":address}
        print "new node added .",address
        self._registry.append(r)
    
    def find_node(self,address):
        for r in self._registry:
            addr=r['address']
            if addr[0]==address[0] and addr[1]==address[1]:
                return r
             
    def close_all(self):
        for r in self._registry:
            try:
                r['connection'].close()
            except:
                print "close connection failure ",r
                


        
class MyTCPBroker:
    def __init__(self,host,port,registry):
        self._socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._socket.bind((host,port))
        self.registry=registry
        
    def run(self,clients=5):
        self._socket.listen(clients)
        while True:
            connection,address=self._socket.accept()
            self.registry.add_node(connection,address)
            
            self.registry.notify_all(json.dumps({"nodes":[{"address":str(r['address'])} for r in self.registry._registry],"from":"broker"}))
            time.sleep(5)

            gevent.spawn(lambda :handle_tcp_connection(self.registry, connection, address))

         
def handle_tcp_connection(registry,connection,address):
    while True:
        data = connection.recv(1024)
        print "received",data 
        connection.sendall(json.dumps({"from":"broker","data":"pong"}))
        time.sleep(3)
        notification=json.dumps({"address":str(address),"data":data,"from":"broker"})
        
        registry.notify_all(notification)
        
    
if __name__=='__main__':
    server_port=8002
    print "Starting Listen...",server_port
    tcp_broker=MyTCPBroker('',server_port,Registry())
    tcp_broker.run(6)
    
    

