import socket
MSGLEN = 2048

class Socket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, host,port):
        self.host = host
        self.port = port

    def connect(self):
        self.sock = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                self.sock.close()
                return b''.join(chunks)
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        self.sock.close()
        return b''.join(chunks)

class FakeSocket(Socket):
    def connect(self):
        pass

    def receive(self):
        data = """
        {"time":1516194872,
        "serial":"760170",
        "Nch":24,
        "sl":0,
        "chStat":["off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off.","off."],
        "chControl":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Vset":[0.0586962,0.0338544,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Cset":[0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001],
        "Vmeas":[0.0586962,0.0338544,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Cmeas":[4.04905e-08,1.17549e-38,1.17549e-38,1.17549e-38,1.7468e-08,6.674e-08,1.17549e-38,8.25797e-09,7.62087e-08,1.17549e-38,5.47456e-08,1.17549e-38,1.17549e-38,9.49307e-10,1.17549e-38,6.08515e-08,5.02428e-08,1.17549e-38,5.91287e-08,1.17549e-38,1.17549e-38,1.17549e-38,1.17549e-38,4.42336e-08]}
        """
        return data.replace('\n','').encode()
