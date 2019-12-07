import socket,threading,time,os,sys,platform

#~--------------Variables Globales---------------
ip="18.188.14.65"
port=15370
size_packages=65536
#------------------------------------------------


nick=input("Elije un Nick: ")
nick=nick.encode()



client=socket.socket()

#--El cliente cifra el mensaje con esta funcion
def cifrar_mensaje(mensaje):
	mensaje=mensaje[::-1]
	lista_letras=()
	for letra in mensaje:
		n=ord(letra)
		n=n+867
		n=hex(n)
		lista_letras=lista_letras + (str(n)+"/*//",)
	mensaje="".join(lista_letras)
	mensaje=mensaje.encode()
	return mensaje

#--El cliente descifra el chat con esta funcion
def descifrar_mensaje(mensaje,client):
	mensaje=mensaje.decode()
	mensaje=mensaje.split("/*//")
	mensaje=mensaje[:-1]
	
	lista_letras=()
	for letra in mensaje:
		try:
			letra=int(letra,16)
		except ValueError:
			
			limpiar_pantalla()
			print("\nEl paquete es muy grande y no puede ser descifrado... (Sube el limite de tamaño de los paquetes)\nPulse enter para Finalizar la conexion...")
			client.close()
			quit()

		letra=letra-867
		letra=chr(letra)
		lista_letras=lista_letras + (letra,)
	mensaje="".join(lista_letras)
	mensaje=mensaje[::-1]
	return mensaje

#detecta el sistema operativo para limpia la pantalla	
def limpiar_pantalla():
	if "Windows" in platform.platform():
		os.system("cls")
	else:
		os.system("clear")

def recibir_mensajes(client):
	while True:
		try:
			mensaje=client.recv(size_packages)
		except ConnectionAbortedError:
			break
		except OSError:
			break

		mensaje=descifrar_mensaje(mensaje,client)
		limpiar_pantalla()
		
		print(mensaje)

		sys.stdout.write("""----------------------------------------------------------------------------------------------
> """)
		time.sleep(1)

def tratar_mensaje(mensaje,client):
	if ("/exit" in mensaje):
		client.close()
		print("Conexion finalizada Pulse para Salir del Programa...")
		input("")
		quit()
	else:
		return


def enviar_mensaje(client):
	while True:
		mensaje=input("> ")
		tratar_mensaje(mensaje,client)
		mensaje=cifrar_mensaje(mensaje)
		try:
			client.send(mensaje)
		except OSError:
			limpiar_pantalla()
			print("El servidor a finalizado la conexion... Pulse enter para salir")
			input("")
			break
try:
	client.connect((ip,port))
	client.send(nick)
except ConnectionRefusedError:
	print("No existe Conexion con el servidor")
	input("pulse para salir del programa...")
	quit()


recibir=threading.Thread(name="recibir_msg", target=recibir_mensajes,args=(client, ))
recibir.start()

enviar=threading.Thread(name="enviar_msg", target=enviar_mensaje,args=(client, ))
enviar.start()





