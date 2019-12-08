import socket,threading,time,sys,os
from pathlib import Path

#-------Variables Globales--------
ip="192.168.1.222"
port=8362
admin="brian"
size_packages=16192
refresh_time=1800 #Tiempo de eliminacion de chat (en segundos)
#------------------------------------





#----------------------Funciones---------------


#Limpia el chat cada 30 minutos
def temporizador_chat():
	while True:
		time.sleep(refresh_time)
		limpiar_chat()


#Crea una copia del chat en logs/ con la fecha y hora de guardado.
def guardar_chat_en_logs():
	fecha=time.strftime("[%d-%m-%Y][%I;%M %p]")
	archivo=open("chat.txt","r")
	datos=archivo.read()
	archivo.close()
	archivo_new=open(f"logs\\chat-{fecha}.txt","w")
	archivo_new.write(datos)
	archivo_new.close()



#---Comandos Para el chat
def tratar_mensajes(mensaje,nick,client_ip):
	if (("/clear" in mensaje) and (nick == admin) and (ip in client_ip)):
		limpiar_chat()
	else:
		return

#--El server cifra el chat con esta funcion
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

#el server descifra el mensaje con esta linea
def descifrar_mensaje(mensaje):
	mensaje=mensaje.decode()
	mensaje=mensaje.split("/*//")
	mensaje=mensaje[:-1]
	
	lista_letras=()
	for letra in mensaje:
		letra=int(letra,16)
		letra=letra-867
		letra=chr(letra)
		lista_letras=lista_letras + (letra,)
	mensaje="".join(lista_letras)
	mensaje=mensaje[::-1]
	return mensaje	

# Remplaza la tupla de la ip de los clientes por un texto mas legible
def client_to_ip(cliente_ip): 
	cliente_ip=str(cliente_ip)
	cliente_ip=cliente_ip.replace("'","")
	cliente_ip=cliente_ip.replace(",",":")
	cliente_ip=cliente_ip.replace("(","[")
	cliente_ip=cliente_ip.replace(")","]")
	cliente_ip=cliente_ip.replace(" ","")
	return cliente_ip

def hora_mensaje():
	hora=time.strftime("[%I:%M %p] | ")
	return hora
# Recoje el nick y la IP del cliente y lo muestra en pantalla
def recibir_nick_clientes(client,client_ip):
	nick=client.recv(size_packages)
	try:
		nick=nick.decode()
	except UnicodeDecodeError:
		print("Error desconocido al recibir nombre...")
		client.close()
	try:
		nick.encode()
	except UnicodeDecodeError:
		#print (f"{nick} no es valido para los clientes")
		os.system(f"echo [93m {nick} [92m no es un nick valido para los clientes.[0m")
		client.close()
	login=f"* {hora_mensaje()}{nick} --> {client_to_ip(client_ip)} Acaba de conectarse."
	print(login)
	escribir_mensaje_en_archivo(login,nick)

	recibir_mensaje_clientes(client,nick,client_ip)


# Acepta conexiones entrantes
def conectar_clientes(server):
	while True:
		client,client_ip=server.accept()
		
		

		#LA siguiente linea es la que permite que se conecten multiples clientes ya que no tiene que finalizar la funcion para realizar la comprobacion de nuevos clientes.
		recibir_Nick=threading.Thread(name="recibir_nick_clientes", target=recibir_nick_clientes, args=(client,client_ip))
		recibir_Nick.start()

		Enviar_Chat=threading.Thread(name="Enviar_Chat", target=enviar_chat, args=(client, ))
		Enviar_Chat.start()
	
#Esta funcion se encarga de recibir todos los mensajes de los clientes
def recibir_mensaje_clientes(client,nick,client_ip):
	while True:
		try:
			mensaje=client.recv(size_packages)		
			try:
				mensaje=f"  {hora_mensaje()}{nick}: {descifrar_mensaje(mensaje)}"
			except UnicodeDecodeError:
				print (f"* {hora_mensaje()}{nick} --> {client_to_ip(client_ip)} ha introducido un caracter no valido.")
				continue
			except ConnectionAbortedError:
				print (f"* {hora_mensaje()}{nick} --> {client_to_ip(client_ip)} se ha forzado la desconexion..")
				continue
			escribir_mensaje_en_archivo(mensaje,nick)
			tratar_mensajes(mensaje,nick,client_ip)
			print(mensaje)
			time.sleep(1)
		except ConnectionResetError:
			logout=f"* {hora_mensaje()}{nick} --> {client_to_ip(client_ip)} Se ha desconectado."
			escribir_mensaje_en_archivo(logout,nick)
			print(logout)
			limpiar_chat()
			break
		except:
			print (f"* {hora_mensaje()}{nick} --> {client_to_ip(client_ip)} se ha forzado la desconexion por un error inesperado ...")
			limpiar_chat()
			break

#Esta funcion escribe cada uno de los mensajes enviados a un fichero de texto plano
def escribir_mensaje_en_archivo(mensaje,nick):
	archivo=open("chat.txt","a")
	try:
		archivo.write(mensaje+"\n")
	except UnicodeEncodeError:
		print(f"* {hora_mensaje()}{nick} ha introducido Un caracter no valido")
	archivo.close()

def leer_mensajes_de_archivo():
	archivo=open("chat.txt","r")
	datos=archivo.read()
	archivo.close()
	return datos
def comprobar_igualdad_archivos():
	archivo_Temp=open("temp.txt","r")
	datos_Temp=archivo_Temp.read()
	archivo_Temp.close()
	datos_chat=leer_mensajes_de_archivo()
	if (datos_chat == datos_Temp):
		return False
	else:
		return True
def escribir_temp(chat):
	archivo_Temp=open("temp.txt","w")
	datos_Temp=archivo_Temp.write(chat)
	archivo_Temp.close()


#Esta funcion envia el archivo chat.txt a los clientes cada 1 segundo
def enviar_chat(client):
	while True:
		chat=leer_mensajes_de_archivo()
		if (comprobar_igualdad_archivos()):
			escribir_temp(chat)
			chat=cifrar_mensaje(chat)
			try:
				client.send(chat)
			except:
				break	
		else:
			continue


def limpiar_chat():
	#guardar_chat_en_logs()
	archivo=open("chat.txt","w")
	archivo.write("")
	archivo.close()

	File=open("temp.txt","w")
	File.write("")
	File.close()

#------------------------MAIN------------------------------

#------Limpiar registro de chat--------------
limpiar_chat()
#--------------

server=socket.socket()
server.bind((ip,port))
server.listen(50)

refresh_chat=threading.Thread(name="refresh_chat", target=temporizador_chat)
refresh_chat.start()

os.system("echo [96mEl server Esta escuchando...[0m")
conectar_clientes(server)