from os import name, stat
import objs
import random

errors = {1 : "do not has a cable connected", 2: "does not exist", 3: "is not free", 4: "the device must be a host",
          5: "host busy (collision)", 6: "has a cable connected, but its other endpoint is not connected to another device" }
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
class Device_handler:
    # @property
    # def hosts(self):
    #     return self.hosts

    def __init__(self, slot_time: int) -> None:
        self.hosts = []
        self.connections = {}
        self.time = 0
        self.slot_time = slot_time
        # diccionario que va a guardar todos los puertos de todos los devices para poder acceder de manera rapida a los mismo en 
        # las operaciones necesarias
        self.ports = {}
        self.devices_visited = []

    def __validate_send(self, host) -> bool:

        port_name = host+"_1"
        if port_name not in self.ports.keys():
            print(f"{bcolors.WARNING} send error {bcolors.ENDC} the device {bcolors.OKBLUE} {host} {bcolors.ENDC} {errors[2]}")
            return False

        port = self.ports[port_name]
        if not isinstance(port.device, objs.Host):
            print(f"{bcolors.WARNING} send error {bcolors.ENDC} the device {bcolors.OKBLUE} {host} {bcolors.ENDC} {errors[4]}")
            return False

        
        return True

    def __validate_disconnection(self, name_port):
        
        if name_port not in self.ports.keys():
             print(f"{bcolors.WARNING}invalid disconnection{bcolors.ENDC} port {bcolors.OKGREEN}{name_port} {bcolors.ENDC} {errors[2]}")
             return False
        port = self.ports[name_port]
        if port.cable == None:
                print(f"{bcolors.WARNING} invalid disconnection{bcolors.ENDC} port{bcolors.OKGREEN} {name_port} {bcolors.ENDC} {errors[1]}")
                return False

        return True

    def __validate_connection(self, name_port): # Private method to identify wether a device is a hub or a host
        

        if name_port not in self.ports.keys():
            print(f"{bcolors.WARNING} invalid connection{bcolors.ENDC} port  {bcolors.OKGREEN}{name_port} {bcolors.ENDC} {errors[2]}")
            return False

        port = self.ports[name_port]
        
        if  port.cable != None:
                print(f"{bcolors.WARNING} invalid connection {bcolors.ENDC} port  {bcolors.OKGREEN}{name_port} {bcolors.ENDC}{errors[3]}")
                return False

        return True

    def __validate_mac(self,pc):
        port = pc + "_1"
        if port not in self.ports.keys():
            print(f"{bcolors.WARNING} invalid mac assign{bcolors.ENDC} PC {bcolors.OKGREEN}{pc} {bcolors.ENDC} {errors[2]}")
            return False



    def finished_network_transmission(self):
        # al no quedar mas instruccionens por ejecutar
        # mantengo recorrido de los devices mientras haya alguna
        # actividad de los host      
        while True:
            self.time += 1
            if not self.__update_devices():
                break

    def __update_network_status(self, time: int):
        # actualizo la red hasta el time de la instruccion actual
        while self.time < time:
            self.time += 1
            self.__update_devices()
        self.time = time

    def create_pc(self, name: str, time: int):
        # actualiza la red hasta que llegues al time en que vino la nueva instruccion
        self.__update_network_status(time)
        newpc = objs.Host(name)
        self.hosts.append(newpc)
        # agrego el unico puerto que tiene un host al dicc que contiene todos los puertos de la red
        self.ports[newpc.port.name] = newpc.port

    def create_hub(self, name: str, ports, time: int):
        # actualiza la red hasta que llegues al time en que vino la nueva instruccion
        self.__update_network_status(time)    
        newhub = objs.Hub(name, ports)
        # agrego cada puerto que tiene un hub al dicc que contiene todos puertos de la red
        for port in newhub.ports:
            self.ports[port.name] = port
    
    def create_switch(self,name: str,ports, time: int):
        self.__update_network_status(time)
        newswitch = objs.Switch(name, ports)
        for port in newswitch.ports:
            self.ports[port.name] = port

    def mac(self, host, address, time: int):
        if __validate_mac():

    def setup_connection(self, name_port1: str, name_port2: str, time: int):
        # actualiza la red hasta que llegues al time en que vino la nueva instruccion
        self.__update_network_status(time)

        if self.__validate_connection(name_port1) and self.__validate_connection(name_port2):
            port1 = self.ports[name_port1]
            port2 = self.ports[name_port2]
            device1 = port1.device
            device2 = port2.device
            if device1 == device2:
                print("Ports of the same device is not possible connected")
                
            else:
                self.connections[name_port1] = name_port2
                self.connections[name_port2] = name_port1
                newcable = objs.Cable()
                port1.cable = newcable
                port2.cable = newcable
                # si los dispositvos  pertenecientes a los puertos estan transmitiendo informacion a la vez
                #
                # en caso que conecte un hub a otro hub que estan retransmitiendo la informacion desde distintos host
                # se manda un sennal para tumbar la transmision en ambos lados y los host volveraran a intentar 
                # transmitir la informacion luego de un tiempo aleatorio en cada uno 
                if device1.bit_sending != None and device2.bit_sending != None:
                    self.devices_visited.clear()
                    self.__clear_cables_data(device1, port1, True)
                    self.devices_visited.clear()
                    self.__clear_cables_data(device2, port2, True)
                # en caso que device1 esta transmitiendo informacion riego la informacion por los nuevos
                # cables que ahora estan interconectados desde el device2 
                elif device1.bit_sending != None:
                    
                    if isinstance(device1, objs.Host):
                        if device1.transmitting:    
                            self.__send_bit(device1,device1.bit_sending)
                        else:
                            return    
                    else:
                        port1.cable.data = device1.bit_sending
                        self.devices_visited.clear()
                        self.__spread_data(device2, device1.bit_sending, port2)
                    
                # en caso que device2 esta transmitiendo informacion riego la informacion por los nuevos
                # cables que ahora estan interconectados desde el device1    
                elif device2.bit_sending != None:
                   
                    if isinstance(device2, objs.Host): 
                        if device2.transmitting:
                            self.__send_bit(device1,device1.bit_sending)     
                        else:
                            return            
                    else:
                        port2.cable.data = device2.bit_sending                      
                        self.devices_visited.clear()
                        self.__spread_data(device1, device2.bit_sending, port1)
                

       



    # hay que remover los datos de los cables que se quedaron desconectados del host que estaba enviando informacion
    def __clear_cables_data(self, device,incoming_port:objs.Port, stop_signal : bool = False):
        # en caso que llegue a una PC es porque no tengo
        # que seguir verificando conexiones muertas pues la pc solo puede enviar o recibir
        if device.name in self.devices_visited:
            return
        self.devices_visited.append(device.name) 
        if stop_signal and isinstance(device, objs.Host):
            if device.transmitting:
                device.stopped = True
                device.transmitting = False
                device.failed_attempts = 1
                # notifica que hubo una colision y la informacion no pudo enviarse
                device.log(device.bit_sending, "send", self.time, True)
                # el rango se duplica en cada intento fallido
                if device.failed_attempts < 16:
                    nrand =  random.randint(1, 2*device.failed_attempts*10)
                    # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
                    device.stopped_time = nrand * device.failed_attempts
                else:
                    # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info
                    nex_bit = device.next_bit()
                    # if nex_bit == None and host.data_pending.qsize() > 0:
                    #   # obtengo la proxima cadena de bits a transmitir sacando el proximo elemento de la cola
                    #   host.data = host.data_pending.get()          
                    #   nex_bit = host.next_bit()
                    if nex_bit != None:
                        device.bit = nex_bit
                        device.stopped_time = 1
                        device.failed_attempts = 0
                    else:
                        device.bit_sending = None
                        device.stopped = False
                        device.failed_attempts = 0

            return
    
        elif isinstance(device, objs.Hub):
            device.bit_sending = None
            for port in device.ports:
                if port.cable != None and port != incoming_port:
                    port.cable.data = objs.Data.Null
                    if port.name in self.connections.keys():
                        portname2 = self.connections[port.name]
                        port2 = self.ports[portname2]
                        self.__clear_cables_data(port2.device,port2, stop_signal)

    def shutdown_connection(self, name_port: str, time: int):
        self.__update_network_status(time)

        if self.__validate_disconnection(name_port):
            port1 = self.ports[name_port]
            if name_port in self.connections.keys():
                name_port2 = self.connections[name_port]
                port2 = self.ports[name_port2]
                # si por este cable esta pasando informacion actualmente
                if port1.cable.data != objs.Data.Null:
                    # en caso que la informacion provenga a traves del port1
                    # esta deja de llegar desde el port2 a todas las conexiones que partan de el
                    port1.cable.data = objs.Data.Null
                    if port1.cable.transfer_port == port1:                        
                        self.devices_visited.clear()
                        self.__clear_cables_data(port2.device,port2)
                    else:
                    # en caso que la informacion provenga a traves del port2
                    # esta deja de llegar desde el port1 a todas las conexiones que partan de el    
                        self.devices_visited.clear()
                        self.__clear_cables_data(port1.device,port1)

                if isinstance(port1.device,objs.Host) and port1.device.transmitting:
                    port1.device.transmitting = False
                    # el host no puede enviar en este momento la sennal pues se esta transmitiendo informacion por el canal o no tiene canal para transmitir la informacion
                    port1.device.stopped = True
                    # aumenta la cantidad de intentos fallidos
                    port1.device.failed_attempts += 1 
                    # notifica que hubo una colision y la informacion no pudo enviarse
                    port1.device.log(port1.device.bit_sending, "send", self.time, True)
                    # el rango se duplica en cada intento fallido
                    if port1.device.failed_attempts < 16:
                        nrand = random.randint(1, 2*port1.device.failed_attempts*10)
                        # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
                        port1.device.stopped_time = nrand * self.slot_time
                    else:
                        # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info

                        port1.device.stopped = True
                        next_bit = port1.device.next_bit()
                        if next_bit != None:
                            port1.device.bit_sending =next_bit
                            port1.device.stopped = True
                            port1.device.stopped_time = 1
                            port1.device.failed_attempts = 0
                        else:
                            port1.device.stopped = False


                # tengo que remover el cable del puerto port1 
                port1.cable = None        
                del self.connections[name_port]
                del self.connections[name_port2]
            else:
                port1.cable = None    

    # de esta forma se revisa si host que esta transmitiendo dejo de hacerlo y por ende toda la informacion desaparece de los cables
    # a los que pueda llegar desde el otra
 
    def __update_devices(self):
        ischange = False  
        for host in self.hosts:
            # en caso que el host no haya podido enviar una informacion previamente producto de una colision
            # por la forma del carrier sense el va a esperar un tiempo aleatorio  para volver a enviar
            # esa informacion y el host esta en modo stopped
            if host.stopped:
                host.stopped_time -= 1
                if host.stopped_time == 0:
                    host.stopped = False
                    # vuelve a intentar enviar el bit que habia fallado previamente
                    self.__send_bit(host, host.bit_sending)
                ischange = True
            # en caso que el host este transmitiendo un informacion
            elif host.transmitting:
                host.transmitting_time +=1
                # compruebo si la informacion vencio el maximo time que puede estar en el canal
                if host.transmitting_time % self.slot_time == 0:
                    if host.port.cable != None:
                        host.port.cable.data = objs.Data.Null
                    host.bit_sending = None    
                    # dame el proximo bit a enviar por el host
                    nex_bit = host.next_bit()

                    
                    
                    if host.port.name in self.connections.keys():
                        portname2 = self.connections[host.port.name]
                        port2 = self.ports[portname2]
                        # limpia el camino para enviar el proximo bit
                        self.devices_visited.clear()
                        self.__clear_cables_data(port2.device,port2)
                    # intenta enviar el proximom bit 
                    if nex_bit != None:
                       
                       self.__send_bit(host,nex_bit)
                        
                    else:
                        host.transmitting = False
                        host.transmitting_time = 0    
                
                ischange = True   

        return ischange                



    def send(self, origin_pc, data, time):
        # actualiza primero la red por si todavia no ha llegado a time 
        self.__update_network_status(time)

        if self.__validate_send(origin_pc):  # El send es valido
            host = self.ports[origin_pc+'_1'].device
            # en caso que la pc este transmitiendo otra informacion
            if host.data != "":
                # agrego esa nueva informacion a una cola de datos sin enviar
                host.data_pending.put(data)
            else:
                host.data = data
            # en caso que el host este disponible para enviar pues el mismo puede estar
            # en medio de una transmision o estar esperando producto de una colision a enviar un dato fallido 
            if not host.stopped and not host.transmitting:
                nex_bit = host.next_bit()
                self.__send_bit(host, nex_bit)

            

    # Metodo que se encarga de intentar enviar un bit desde una PC
    def __send_bit(self, origin_pc, data):
        device = origin_pc
        device.bit_sending = data
        # si hubo colision 
        if not device.put_data(data):
                device.transmitting = False
                # el host no puede enviar en este momento la sennal pues se esta transmitiendo informacion por el canal o no tiene canal para transmitir la informacion
                device.stopped = True
                # aumenta la cantidad de intentos fallidos
                device.failed_attempts += 1 
                # notifica que hubo una colision y la informacion no pudo enviarse
                device.log(data, "send", self.time, True)
                # el rango se duplica en cada intento fallido
                if device.failed_attempts < 16:
                    nrand = random.randint(1, 2*device.failed_attempts*10)
                    # dada una colision espero un tiempo cada vez mayor para poder volverla a enviar
                    device.stopped_time = nrand * self.slot_time
                else:
                    # se cumplio el maximo de intentos fallidos permitidos por lo que se decide perder esa info
                     
                    device.stopped = True
                    next_bit = device.next_bit()
                    if next_bit != None:
                        device.bit_sending =next_bit
                        device.stopped = True
                        device.stopped_time = 1
                        device.failed_attempts = 0
                    else:
                        device.stopped = False
        # en caso que no haya colision empiezo a regar la informacion  desde el host por toda la red de cables interconectados 
        # alcanzables por el host                    
        else:
            device.transmitting = True
            device.transmitting_time = 0
            device.log(data, "send", self.time)
            # revise el object del puerto 
            destination_port = self.ports[self.connections[origin_pc.port.name]]
            destination_device = destination_port.device
            self.devices_visited.clear()
            self.__spread_data(destination_device, data, destination_port)


    # este metodo se encarga de regar la informacion a retransmitir por todos los cables alcanzables desde un device origen

    def __spread_data(self, device, data, data_incoming_port):
        # si este device ya fue visitado entonces no tengo nada que hacer
        if device.name in self.devices_visited:
            return
        # agrego el device a la lista de dispositivos visidados
        self.devices_visited.append(device.name)    
        if isinstance(device, objs.Host):
            device.log(data, "receive", self.time)
            
        elif isinstance(device, objs.Hub):
            device.bit_sending = data
            device.log(data, "receive", data_incoming_port.name, self.time)
            for port in device.ports:
                if port != data_incoming_port and port.cable != None and port.cable.data == objs.Data.Null:
                    # pongo la informacion en el cable
                    device.put_data(data, port)
                    # para seguir de forma recursiva por ese puerto es necesario primero verificar que este  este conectado con otro puerto a traves de un cable
                    # para eso verifico que este en dicc connections pues este guarda todas las conexiones entre puertos a traves de un cable
                    if port.name in self.connections.keys(): # en caso que este puerto conecte con otro de otro device
                        device.log(data, "send", port.name, self.time)
                        next_port = self.ports[self.connections[port.name]]
                        next_device = self.ports[self.connections[port.name]].device

                        # sigue regando la informacion a otros devices
                        self.__spread_data(next_device, data, next_port)

