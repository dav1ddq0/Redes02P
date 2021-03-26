from enum import Enum
import queue
import random

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

    def colision_protocol(self):
            self.transmitting = False
            # el host no puede enviar en este momento la sennal pues se esta transmitiendo informacion por el canal o no tiene canal para transmitir la informacion
            self.stopped = True
            # aumenta la cantidad de intentos fallidos
            self.failed_attempts += 1 
            # notifica que hubo una colision y la informacion no pudo enviarse
            self.log(data, "send", self.time, True)
            # el rango se duplica en cada intento fallido
            if self.failed_attempts < 16:
                nrand = random.randint(1, 2*device.failed_attempts*10)
                # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
                self.stopped_time = nrand * self.slot_time
            else:
                # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info                 
                device.stopped = True
                next_bit = self.next_bit()
                if next_bit != None:
                    device.bit_sending = next_bit
                    device.stopped = True
                    device.stopped_time = 1
                    device.failed_attempts = 0
                else:
                    device.stopped = False
        # en caso que no haya colision empiezo a regar la informacion  desde el host por toda la red de cables interconectados 
        # alcanzables por el host             



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

    def receive(self, bit, incoming_port, devices_visited, time):
        self.log(next_bit, "receive", incoming_port, time)

    def send(self, bit, incoming_port, devices_visited, time):
        if self.data != "":
            # agrego esa nueva informacion a una cola de datos sin enviar
            self.data_pending.put(data)
        else:
            self.data = data 
            if not host.stopped and not host.transmitting:
                nex_bit = host.next_bit()
                self.log(next_bit, "send", incoming_port, time)
                if put_data(next_bit):
                    self.transmitting = True
                    self.transmitting_time = 0
                    if self.port.next != None:
                        self.port.next.device.receive(bit, self.port.next, devices_visited, time)
                else:
                    self.colision_protocol()        



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

    def receive(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "receive", port, time)
        self.send(bit, incoming_port, devices_visited, time)

    def send(self, bit, incoming_port, devices_visited, time):
        self.log(data, "send", incoming_port, time)
        self.put_data(bit, incoming_port)
        devices_visited.append(self.name)
        for _port in self.ports:
            if _port != incoming_port and _port.next != None and _port.next.device.name not in devices_visited:
                _port.next.device.receive(bit, _port.next, time)
                _port.next.device.send(bit, _port.next, devices_visited, time)



class Buffer:
    def __init__(self):
        self.port = nameport
        self.incoming_frame_pending = queue.Queue()
        self.send_frame_pending = queue.Queue()
        # cadena de informacion que el switch ira transmitiendo por ese puerto hacia otro dispositivos
        self.sending_frame = ""
        # cadena de informacion que va recibiendo el switch bit a bit por ese puerto hasta que pueda completar el formato de una trama y decidir para donde
        # lo envia 
        self.incoming_frame = ""
        self.transmitting = False
        self.receiving = False
        self.mac = None
        self.bit = None

    def put_data(self, bit):
        self.incoming_frame += bit       
            


    def next_bit(self):
        n = len(self.frame)
        if n > 0:
            next = self.frame[0]
            self.datself.incoming_frame_pending = queue.Queue()a = self.data[1:]
            return next

        if self.data_pending.qsize() > 0:
            self.data = self.data_pending.get()
            return self.next_bit()    
       
        return None

class Switch:
     def __init__(self, name: str, ports_amount: int) -> None:
        self.name = name
        self.connections = [None] * ports_amount
        self.file = f"./Switches/{name}.txt"
        self.ports = []  # instance a list of ports
        # con esto se si el hub esta retrasmitiendo la informacion proveniente de un host que esta enviando info y que informacion
        
        # diccionario de la forma key = mac value = port of device mac
        self.map={}
        self.buffers = {}
        self.frames = []
        for i in range(ports_amount):
            portname = f"{name}_{i + 1}"
            buffer[portname] = Buffer()
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

     def receive(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "receive", port,time)
        self.buffers[incoming_port.name].putdata(bit)
        self.check_buffers()

    def put_data(self, data:str, port: Port):
        port.write_channel.data = data

    # comprobar el en cada momento el cambio interno de un switch
    def check_buffers(self):
        for port in self.ports:
            mybuffer = buffers[port]
            incoming_frame = mybuffer.incoming_frame
            ## cumple el formato de una trama 16bit outmac 16 inmac 8 bit len 8bit0 data
            if len(incoming_frame) > 48:
               
                lendatabin = incoming_frame[32:40]
                lendata = int(lendata,2)
                framedata = [48:]
                if len(framedata) == lendata:
                    macbin =  framedata[0:16]
                    machex = '{:X}'.format(int(macbin,2))
                    if machex not in self.map.keys():
                        
                        for p2 in [p in self.ports if p !=port]:
                            name = p2.name
                            if buffer[name].sending_frame != "":
                                buffer[name].send_frame_pending.put(incoming_frame)
                            else:
                                buffer[name].sending_frame = incoming_frame
                    else:
                        nextport = map[machex].name
                        if buffer[nextport].sending_frame != "":
                            buffer[nextport].send_frame_pending.put(incoming_frame)
                        else:
                            buffer[nextport].sending_frame = incoming_frame
                
                mybuffer.incoming_frame = ""

               
    def send(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "send", incoming_port.name, time)
        self.put_data(bit, incoming_port)
        nexport = incoming_port.next
        nextport.device.receive(bit, incoming_port, devices_visited, time)




        
        
                

        
        
    