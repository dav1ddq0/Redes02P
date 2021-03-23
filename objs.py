from enum import Enum
import queue


class Data(Enum):
    Null = "Null"
    One = "1"
    Zero = "0"


class Cable:
    def __init__(self):
        # conozco la informacion qu esta pasando por el cable
        self.data = Data.Null  # 0 1 Null son los tres estados en los que puede estar el cable
        self.transfer_port = None
        # puerto de donde se esta enviando la informacion
        # es muy util para cuando haya que desconectar


class Port:
    def __init__(self, name: str, device) -> None:
        # nombre del puerto
        self.name = name
        # con esta propiedad conozco si un cable conectado al puerto
        self.cable = None
        # un puerto sabe de que dispositvo es
        self.device = device


class Host:
    def __init__(self, name: str) -> None:
        self.name = name
        portname = f"{name}_1"
        port = Port(portname, self)
        self.port = port
        self.file = f"./Hosts/{name}.txt"
        self.data = ""
        # guarda todos los bloques de cadenas que aun no han sido enviados
        self.data_pending = queue.Queue()
        # muestra informacion sobre el bit que se esta transmitiendo cuando el host esta enviando informacion
        self.bit_sending = None
        self.transmitting_time = 0
        self.transmitting = False
        self.stopped = False
        self.stopped_time = 0
        self.failed_attempts = 0
        # me permite conecer  si una PC esta transmitiendo o no en un momento determinado informacion
        f = open(self.file, 'w')
        f.close()

    def __update_file(self, message):
        f = open(self.file, 'a')
        f.write(message)
        f.close()

    def log(self, data, action, time, collison=False):
        terminal = "collision" if collison else "ok"
        message = f"{time} {self.port.name} {action} {data} {terminal}\n"
        self.__update_file(message)

    def put_data(self, data: int):
        if self.port.cable == None or self.port.cable.data != Data.Null:
            return False
        else:
            self.port.cable.data = data
            self.port.cable.transfer_port = self.port
            self.bit_sending = data
            return True

    def next_bit(self):
        n = len(self.data)
        if n > 0:
            next = self.data[0]
            self.data = self.data[1:]
            return next

        if self.data_pending.qsize() > 0:
            self.data = self.data_pending.get()
            return self.next_bit()    
       
        return None


class Hub:
    def __init__(self, name: str, ports_amount: int) -> None:
        self.name = name
        self.connections = [None] * ports_amount
        self.file = f"./Hubs/{name}.txt"
        self.ports = []  # instance a list of ports
        # con esto se si el hub esta retrasmitiendo la informacion proveniente de un host que esta enviando info y que informacion
        # es resulta util para detectar colisiones
        self.bit_sending = None
        for i in range(ports_amount):
            portname = f"{name}_{i + 1}"
            port = Port(portname, self)
            self.ports.append(port)
        # make the hub file
        f = open(self.file, 'w')
        f.close()

    def __update_file(self, message: str) -> None:
        f = open(self.file, 'a')
        f.write(message)
        f.close()

    def log(self, data, action, port, time) -> None:
        message = f"{time} {port} {action} {data}\n"
        self.__update_file(message)

    def put_data(self, data:str, port: Port):
        port.cable.data = data
        port.cable.transfer_port = port

