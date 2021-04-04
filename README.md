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

#### El cable duplex lo consideramos como que tiene dos cables normales uno para leer y otro para escribir. Por tanto cada puerto tendría un canal de escritura y un canal de lectura. Al estar conectados dos puertos P1 y P2 el canal de escritura de P1 es el canal de lectura de P2 y el canal de escritura de P2 es el de lectura de P1.

#### Consideramos que el switch coge la mac de las pc que estén directamente conectadas a él y la guarda en su tabla la cual la representamos con un dicc de la forma <mac, port instance>. Dado que cada puerto del switch funciona de forma independiente tenemos como una especie de buffer para cada puerto que guarda todos los frames que se tienen que transmitir por ese puerto. Parecido a como hicimos con la PC los frames se van a ir encolando y se van a mandar en el orden en que lleguen. El switch detecta si hubo colisiones por uno de sus puertos en caso que ocurra aplica el protocolo de colisiones , consideramos usar el mismo que teníamos para los host. El buffer de cada puerto conoce si ocurrió una colisión y el puerto esta esperando a que pase el tiempo asignado según el protocolo.  En los hubs al estar más de dos host transmitiendo información que pase por estos se podría ocurrir una colisión, para esto mando a parar a todos los host y a los puertos de los swith que estén conectados a este y aplico el protocolo a cada uno. Luego de un  tiempo aleatorio cada uno intentará volver a enviar información. Como teníamos en el proyecto anterior el protocolo de colisiones tiene un máximo de intentos fallidos luego del cual se decide perder esa información. Ahora dos PC pueden estar enviando información una a la otra sin que haya colisión pues cada una escribe por su canal de escritura.

####  Al producirse una desconexión en caso que desconecte un puerto de un host y de un switch el switch borrara de su tabla automáticamente la mac de ese host referenciado a ese puerto.

#### Consideramos que para que una pc notifique en su file _data el frame que le llegue debe de cumplir correctamente que se tenga longitud mayor a 48 y que coincide el len de los 8 bists de la trama con el tamaño de la data.

#### Un switch no decide mandar hacia el o los puertos un frame si este no cumple con los requitistos de que se tenga longitud mayor a 48 y que coincide el len de los 8 bists de la trama con el tamaño de la data.

#### Puede darse  el caso que se producto  de una desconexión conexión se corrompan las tramas pero el switch no detecta esto y considera lo ve como si fuera la trama no corrupta.

#### Consideramos que si conectas dos hubs que estén retransmitiendo información desde host entonces se produce una colisión. En cambio dos PC pueden estar enviando información una a la otra mediante un hub sin ningún inconveniente.
