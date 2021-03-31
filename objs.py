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
    def __init__(self) -> None:
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
        # bits que han sido recibidos por el host y que podrian ser una trama 
        self.rframe =""
        # me permite conecer  si una PC esta transmitiendo o no en un momento determinado informacion
        # direccion mac que tendria la PC
        self.mac = None
        # se escribiran solamente los datos recibidos por esta PC y quien los recibio
        self.file_d =f"./Hosts/{name}_data.txt"
        self.incoming_frame =""
        self.slot_time = 3
        f = open(self.file, 'w')
        f.close()
        f = open(self.file_d, 'w')
        f.close()
        

    def __update_file(self, message, file):
        f = open(file, 'a')
        f.write(message)
        f.close()

    def log(self, data, action, time, collison=False):
        terminal = "collision" if collison else "ok"
        message = f"{time} {self.port.name} {action} {data} {terminal}\n"
        self.__update_file(message, self.file)
    
    def log_frame(self, source_mac, datahex, time):
        message = f"{time} {source_mac} {datahex}"
        self.__update_file(message, self.file_d)

    def data(self, origin_mac, data_frame, time):
        message = f"{time} {origin_mac} {data_frame}"
        self.__update_file(message)

    def colision_protocol(self, time):
            self.transmitting = False
            # el host no puede enviar en este momento la sennal pues se esta transmitiendo informacion por el canal o no tiene canal para transmitir la informacion
            self.stopped = True
            # aumenta la cantidad de intentos fallidos
            self.failed_attempts += 1 
            # notifica que hubo una colision y la informacion no pudo enviarse
            self.log(self.data, "send", time, True)
            # el rango se duplica en cada intento fallido
            if self.failed_attempts < 16:
                nrand = random.randint(1, 2*self.failed_attempts*10)
                # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
                self.stopped_time = nrand * self.slot_time
            else:
                # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info                 
                self.stopped = True
                next_bit = self.next_bit()
                if next_bit != None:
                    self.bit_sending = next_bit
                    self.stopped = True
                    self.stopped_time = 1
                    self.failed_attempts = 0
                else:
                    self.stopped = False
        # en caso que no haya colision empiezo a regar la informacion  desde el host por toda la red de cables interconectados 
        # alcanzables por el host             


    def add_frame(self, frame:str):
        if self.data != "":
            # agrego esa nueva informacion a una cola de datos sin enviar
            self.data_pending.put(frame)
        else:
            self.data = frame

    def put_data(self, data: int):
        if self.port.cable == None or self.port.write_channel.data != Data.Null:
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
        self.log(bit, "receive", time)
        self.rframe +=bit
        if len(self.rframe) > 48:
            #obtengo la mac de la pc que mando el frame origen
            origin_mac = '{:X}'.format(int(self.rframe[16:32], 2))
            #obtengo la cantidad de bits que debe de tener la data del frame            
            nsizebits = int(self.rframe[32:40], 2) * 8
            garbage = self.rframe[40:48]
            data = self.rframe[48:]
            # la trama que llego a la pc es valida
            if len(data) == nsizebits:
                #obtengo en hexadecimal la data 
                datahex = '{:X}'.format(int(data,2))
                # guardo en el file _data.txt la trama que recibio la pc
                self.log_frame(origin_mac, datahex, time)



    
    
    def send(self, data, incoming_port, devices_visited, time):
                    
        self.transmitting = True
        self.log(data, "send", time)
        self.transmitting_time = 0
        if self.port.next != None:
            self.port.next.device.receive(data, self.port.next, devices_visited, time)
                

    def death_short(self, incoming_port):
        self.colision_protocol()

    def missing_data(self,incoming_port, devices_visited):
        return

    def retry(self, devices_visited, time):
        self.stopped = False
        self.send(self.bit_sending,self.port, devices_visited, time)
        

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
        if port.write_channel.data != Data.Null:
            port.write_channel.data = data
            return True
        else:
            return False    

    def receive(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "receive", self.port, time)
        self.send(bit, incoming_port, devices_visited, time)

    def send(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "send", incoming_port, time)
        self.put_data(bit, incoming_port)
        devices_visited.append(self.name)
        for _port in self.ports:
            if _port != incoming_port and _port.next != None and _port.next.device.name not in devices_visited:
                if not self.put_data(bit, _port):
                    self.device.death_short(incoming_port)
                    return
                _port.next.device.receive(bit, _port.next, time)
                _port.next.device.send(bit, _port.next, devices_visited, time)


    def death_short(self, incoming_port):
        incoming_port.read_channel = Data.Null
        incoming_port.next.device.death_short(incoming_port.next)
        for port in [p for p in self.ports if p!= incoming_port]:
            port.write_channel.data = Data.Null
            if port.next != None:
                port.next.device.death_short(port.next)
    
    def missing_data(self,incoming_port, devices_visited):
        if self in devices_visited:
            return 
        for port in [p for p in self.ports if p!= incoming_port]:
            port.write_channel.data = Data.Null
            if port.next != None:
                port.next.device.missing_data(port.next)            


class Buffer:
    def __init__(self):
        self.incoming_frame_pending = queue.Queue()
        self.sending_frame_pending = queue.Queue()
        # cadena de informacion que el switch ira transmitiendo por ese puerto hacia otro dispositivos
        self.sending_frame = ""
        # cadena de informacion que va recibiendo el switch bit a bit por ese puerto hasta que pueda completar el formato de una trama y decidir para donde
        # lo envia 
        self.incoming_frame = ""
        self.transmitting = False
        self.receiving = False
        self.mac = None
        self.bit_sending = None
        self.transmittig_time = 0
        self.failed_attempts = 0
        self.stopped = False
        self.stopped_time = 0

    def put_data(self, bit):
        self.incoming_frame += bit       
            

    


    def next_bit(self):
        n = len(self.sending_frame)
        if n > 0:
            next = self.sending_frame[0]
            self.sending_frame = self.sending_frame[1:]
            return next

        if self.sending_frame_pending.qsize() > 0:
            self.sending_frame = self.sending_frame_pending.get()
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
            self.buffers[portname] = Buffer()
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
        self.log(bit, "receive", incoming_port,time)
        self.buffers[incoming_port.name].putdata(bit)
        self.check_buffers()

    def put_data(self, data:str, port: Port):
        port.write_channel.data = data

    def colision_protocol(self, switch_port):
        pbuffer = self.buffers[switch_port.name]
        pbuffer.transmitting = False
        # el host no puede enviar en este momento la sennal pues se esta transmitiendo informacion por el canal o no tiene canal para transmitir la informacion
        pbuffer.stopped = True
        # aumenta la cantidad de intentos fallidos
        pbuffer.failed_attempts += 1 
        # notifica que hubo una colision y la informacion no pudo enviarse
        self.log(pbuffer.data, "send", switch_port.name, time, True)
        # el rango se duplica en cada intento fallido
        if pbuffer.failed_attempts < 16:
            nrand = random.randint(1, 2*self.failed_attempts*10)
            # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
            pbuffer.stopped_time = nrand * self.slot_time
        else:
            # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info                 
            pbuffer.stopped = True
            next_bit = self.next_bit()
            if next_bit != None:
                pbuffer.bit_sending = next_bit
                pbuffer.stopped = True
                pbuffer.stopped_time = 1
                pbuffer.failed_attempts = 0
            else:
                pbuffer.stopped = False

    

    # comprobar el en cada momento el cambio interno de un switch
    def check_buffers(self):
        for port in self.ports:
            mybuffer = self.buffers[port]
            incoming_frame = mybuffer.incoming_frame
            ## cumple el formato de una trama 16bit outmac 16 inmac 8 bit len 8bit0 data
            if len(incoming_frame) > 48:
               
                lendatabin = incoming_frame[31:39]
                lendata = int(lendata,2)
                framedata = incoming_frame[47:]
                if len(framedata) == lendata:
                    macbin =  framedata[0:16]
                    machex = '{:X}'.format(int(macbin,2))
                    if machex not in self.map.keys():
                        
                        for p2 in [p for p in self.ports if p !=port]:
                            name = p2.name
                            if self.buffers[name].sending_frame != "":
                                self.buffers[name].send_frame_pending.put(incoming_frame)
                            else:
                                self.buffers[name].sending_frame = incoming_frame
                    else:
                        nextport = map[machex].name
                        if self.buffers[nextport].sending_frame != "":
                            self.buffer[nextport].send_frame_pending.put(incoming_frame)
                        else:
                            self.buffers[nextport].sending_frame = incoming_frame
                
                mybuffer.incoming_frame = ""

               
    def send(self, bit, incoming_port, devices_visited, time):
        self.log(bit, "send", incoming_port.name, time)
        self.put_data(bit, incoming_port)
        nextport = incoming_port.next
        nextport.device.receive(bit, incoming_port, devices_visited, time)



    def death_short(self, incoming_port):
        portbuff = self.buffers[incoming_port.name]
        if portbuff.transmitting:
            self.colision_protocol(incoming_port)

        return
        
        
    def missing_data(self,incoming_port):
        return         

    def check_transmitting(self):
        return any(buffer.transmitting for buffer in self.buffer.values())
        
        
    