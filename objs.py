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

class CableDuplex:
    def __init__(self):
        # un cable duplex se representaria como dos cables normales 
        self.cableA = Cable()  
        self.cableB = Cable() 

class Port:
    def __init__(self, name: str, device) -> None:
        # nombre del puerto
        self.name = name
        # con esta propiedad conozco si un cable conectado al puerto
        self.cable = None
        self.read_channel = None
        self.write_channel = None
        # un puerto sabe de que dispositvo es
        self.device = device
        # un puerto conoce con que puerto esta conectado
        self.next = None


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
        self.data_frame_penfing = queue.Queue()
        # muestra informacion sobre el bit que se esta transmitiendo cuando el host esta enviando informacion
        self.bit_sending = None
        self.bit_format = None
        self.transmitting_time = 0
        self.transmitting = False
        self.stopped = False
        self.stopped_time = 0
        self.failed_attempts = 0
        self.frame =""
        # me permite conecer  si una PC esta transmitiendo o no en un momento determinado informacion
        # direccion mac que tendria la PC
        self.mac = None
        # se escribiran solamente los datos recibidos por esta PC y quien los recibio
        self.file_d =f"./Hosts/{name}_data.txt"

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

    def data(self, origin_mac, data_frame, time):
        message = f"{time} {origin_mac} {data_frame}"
        self.__update_file(message)


    def put_data(self, data: int):
        if self.port.cable == None or self.port.cable.write_channel.data != Data.Null:
            return False
        else:
            self.port.write_channel.data = data
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

    def send(self, bit, incoming_port, devices_visited, time):
        self.log(data, "send", incoming_port, time)
        self.put_data(bit, incoming_port)
        self.port.write_channel.data = bit
        if self.port.next != None:
            self.port.next.device.send(bit, self.port.next, devices_visited, time)



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
        port.write_channel.data = data

    def receive(self, bit, port, time):
        self.log(bit, "receive", port,time)

    def send(self, bit, incoming_port, devices_visited, time):
        self.log(data, "send", incoming_port, time)
        self.put_data(bit, incoming_port)
        devices_visited.append(self.name)
        for _port in self.ports:
            if _port != incoming_port and _port.next != None and _port.next.device.name not in devices_visited:
                _port.next.device.receive(bit, _port.next, time)
                _port.next.device.send(bit, _port.next, devices_visited, time)






class Switch:
     def __init__(self, name: str, ports_amount: int) -> None:
        self.name = name
        self.connections = [None] * ports_amount
        self.file = f"./Switches/{name}.txt"
        self.ports = []  # instance a list of ports
        # con esto se si el hub esta retrasmitiendo la informacion proveniente de un host que esta enviando info y que informacion
        
        # diccionario de la forma key = mac value= port of device mac
        self.map={}

        for i in range(ports_amount):
            portname = f"{name}_{i + 1}"
            port = Port(portname, self)
            self.ports.append(port)
        # make the hub file
        f = open(self.file, 'w')
        f.close()

