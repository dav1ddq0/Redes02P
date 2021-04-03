# <center>Proyecto2 de Redes  Capa de Enlace<center>
### <center>David Orlando De Quesada Oliva C311</center>
### <center>Javier E. Domínguez Hernández C312</center>

## Como ejecutar el proyecto:
# python main.py -f file.txt

## Estructuración de proyecto:
#### En el archivo file.txt se copian las instrucciones con las que va a  simular la red

#### Asumimos que cada instrucción viene en orden . Si en el time i llego la instrucción j entonces toda instrucción j+1 tiene que llegar en un time >= i.

#### El tiempo que un bit va a estar siendo transmitido por un host es de 3ms por default. Esto puede cambiarse en el main.py dandole a slot_time otro valor.
#### Cada file que se cree de un device host se guarda en ./Hosts ,cada file de un device hub se guarda en ./Hubs y cada file de un Switch se guarda en ./Switches.

#### en myParser.py se analizara la sintaxis de cada linea en dependecia del comando a ejecutar para verificar si llega de la forma esperada luego  se ejecuta en device_handler.py

#### Consideramos que si una PC no tiene una mac asignada esta no puede conectarse con nadie por lo que al intentar hacer un connect daria error y no se completaria la conexion entre un puerto de la PC y el puerto de otro dispositivo.Esto lo consideramos de esta forma tratando de simular si una PC tenia o no una tarjeta de red conectada. Si la pc no tiene una tarjeta de red conectada entonces no es posible que se conecta con otro dispositivo. Asignar mas de una mac a la misma PC sobreescribiendo la anterior seria valido pues lo vemos como si le cambiaramos la tarjeta de red a la PC.

#### El cable duplex lo consideramos como que tiene dos cables normales uno para leer y otro para escribir. Por tanto cada puerto tendria un canal de escritura y un canal de lectura. Al estar conectados dos puertos P1 y P2 el canal de escritura de P1 es el canal de lectura de P1 y el canal de escritura de P2 es el de lectura de P1.

#### 

