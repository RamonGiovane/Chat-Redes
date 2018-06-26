#coding: utf-8
import getpass as g 
import datetime
import socket
import sys
import threading
import logging
import os

class Socket:
  __ipServidor, __portaServidor, __clientSocket, __minhaPorta = None, None, None, None
  
  #Construtor para criação de sockets. Alguns parâmetros só são iniciados se a finalidade do socket for 
  #para trocar mensagens com o servidor
  def __init__(self, ipServidor, portaServidor, minhaPorta):
    if (ipServidor, portaServidor != None, None):
     self.__ipServidor = ipServidor
     self.__portaServidor = portaServidor
    
    self.__minhaPorta = minhaPorta
    self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  
  def getIpServidor(self):
    return self.__ipServidor
  
  def getPortaServidor(self):
    return self.__portaServidor
  
  def getClientSocket(self):
    return self.__clientSocket
  
  def getMinhaPorta(self):
    return self.__minhaPorta
  
  def setIpServidor(self, ipServidor):
    self.__ipServidor = ipServidor
  
  def setPortaServidor(self, portaServidor):
    self.__portaServidor = portaServidor
  
  
  def setMinhaPorta(self, minhaPorta):
    self.__minhaPorta = minhaPorta

  def fecharSocket(self):
    self.__clientSocket.close()

  def estaFechado(self):
    try:
      self.__clientSocket.sendto('', ('12000', '127.0.0.1'))
    except:
      return False
    return True
#Fim da classe Socket  

#Classe que obtém o status do usuário
class Status():
  
  #Teste
  _shared_state = {}

  def __new__(cls):
    inst = super().__new__(cls)
    inst.__dict__ = cls._shared_state
    return inst
  
  
  #Status ativo = usuário está com o chat aberto pronto para receber mensagens diretamente
  #Status inativo = usuário não está com a conversa aberta para receber mensagens
  ATIVO, INATIVO = 1, 0
  __ipDest, __ipRemt, __estado = None, None, None
  
  def _init_(self):
    self.__estado = INATIVO
    
  def getIpDest(self, ipDest):
    self.__ipDest = ipDest
  
  def getIpRemt(self, ipRemt):
    self.__ipRemt = ipRemt
  
  def getIpDest(self):
    return self.__ipDest
  
  def getIpRemt(self):
    return self.__ipRemt
  
  def getEstado(self, dest, remt):
    return ATIVO if ((dest == self.__ipDest) and (dest == self.__ipRemt)) else INATIVO
  
  def setEstado(self):
    self.__estado = 2
  
  def igetEstado(self):
    return self.__estado

class Thread(threading.Thread):
  def run(self):
    while self.running:
      self.function()

  def stop(self):
    self.running = False

def obterUsuariosOnlines(usuario, udpSocket):
    mensagem = ('LIST[=|=]%s' % (usuario))
    return enviarMensagem_(mensagem.encode(), udpSocket)
  
def listarUsuarios(usuario, udpSocket):
  lista = obterUsuariosOnlines(usuario, udpSocket)

  if (lista.__len__() == 1):
    print("\nNão há outros usuários online.")
    return

  print ("\tUsuários Online")
  for i in lista:
    if (i.split(':')[0] != usuario):
      print(i.split(':')[0])
      
def off():
  fim = input('\nDeseja mesmo ENCERRAR o programa? S/N: ')
  if(fim == 'S'):
    finalizar()
    
def finalizar():
  print ("Finalizando...")
  sys.exit()
  
def cadastrarUsuario(usuario, senha, udpSocket):
  mensagem = "NEW[=|=]%s[=|=]%s" % (usuario, senha)
  enviarMensagem(mensagem.encode(), udpSocket)

#Lê o arquivo de configuração 'setup.txt' e guarda os valores em variáveis
def lerArquivoDeConfiguracao():

  arquivo = open('setup.txt', 'r')
  
  #Percorre as linhas do arquivo
  texto = arquivo.readlines()

  #Obtendo os valores de cada parametro do arquivo de config.
  serverIP = texto[0].split(': ')[1]
  serverPort = texto[1].split(': ')[1]
  port = texto[2].split(': ')[1]

  arquivo.close()
  
  #Retirando o '\n' do final das strings e instanciando um objeto Socket
  return Socket(serverIP[:len(serverIP)-1], int(serverPort[:len(serverPort)-1]), int(port[:len(port)-1]))
    
#Envia uma mensagem para o servidor e recebe uma resposta
def enviarMensagem(mensagem, udpSocket):
  clientSocket = udpSocket.getClientSocket()

  clientSocket.sendto(mensagem, (udpSocket.getIpServidor(), udpSocket.getPortaServidor()))
  resposta, server = clientSocket.recvfrom(4096)

  return resposta

#Envia uma mensagem para o servidor e recebe múltiplas respostas
def enviarMensagem_(mensagem, udpSocket):

  respostas = []
  clientSocket = udpSocket.getClientSocket()

  clientSocket.sendto(mensagem, (udpSocket.getIpServidor(), udpSocket.getPortaServidor()))
  while True:
    clientSocket.settimeout(5)
    resposta, server = clientSocket.recvfrom(4096)
    if(resposta.decode() == 'END'): break
    respostas.append(resposta.decode())

  return respostas

#Pergunta ao servidor se o apelido solicitado já existe
def verificarApelido(apelido, s):
  comando = ('NICK[=|=]%s' % apelido).encode()
  return enviarMensagem(comando, s).decode()
    
#Lê os dados de um cadastro de usuário e os envia para o servidor
def novoUsuario(udpSocket):
  print ("\n\t-Cadastrar Usuário-")
  while True:
    usuario = input ("Qual é o seu apelido?")
    #Verica a validade do apelido
    if(validarUsuario(usuario) == False):
      print('\nApelido inválido! Tente outro!\nSeu nick deve ter ao menos 3 letras\n')
    
    #Verica no servidor o apelido escolhido
    elif(verificarApelido(usuario, udpSocket) == 'True'):
      print("\nEste apelido já está sendo usado por outro usuário!\n")
    
    else: break

  while True:
    while True:
      senha  =  g.getpass("Defina uma senha: ")
      if(len(senha)<5):
        print("\nA senha deve possuir no mínimo 5 caracteres\n")
      else: break
    csenha =  g.getpass("Confirme a senha: ")
    if (senha != csenha):
      print("\nAs senhas não coincidem\n")
    else: 
      cadastrarUsuario(usuario, senha, udpSocket)
      break
      
#Solicita ao servidor que verifique se o login fornecido é válido
def validarLogin(usuario, senha, udpSocket):
  #Separa a porta na qual o usuário recebe mensagens de outros usuarios
  porta = udpSocket.getMinhaPorta()

  lista = obterUsuariosOnlines(usuario, udpSocket)

  for i in lista:
    if (i.split(':')[0] == usuario):
      print("\nERRO: Login simultâneo, este usuário já está logado.")
      return False

  if (validarUsuario(usuario)) and (validarSenha(senha)):
    if (enviarMensagem(('LOGIN[=|=]%s[=|=]%s[=|=]%s[=|=]' % (usuario, senha, str(porta))).encode(),
    udpSocket).decode()) == 'True':
      return True
    else:
      print("\nUsuário ou senha incorreto(s)!\nSolicite o administrador, caso tenha esquecido.\n")
  else: print ("\nUsuário ou senha inválido(s)!\n\n")
  return False

def validarSenha(senha):
  if ((len(senha) < 5) or ('[=|=]' in senha)):
    return False
  return True

def validarUsuario(usuario):
  if ((len(usuario) < 3) or ('[=|=]' in usuario) or (usuario == 'NEW') or (usuario == 'LOGIN') or (usuario == 'NICK')):
    return False
  return True

def logout(usuario, socket):
  enviarMensagem(('LOGOUT[=|=]%s' % (usuario)).encode(), socket)

def login(udpSocket):
  print("Primeiro acesso? Insira NEW para começar")
  while True:
    print("\t-Bem-vindo ao Chat-")
    usuario = input("Usuário:")
    if (usuario == 'NEW'):
        novoUsuario(udpSocket)
        continue
    else: senha = g.getpass("Senha:")
    if (validarLogin(usuario, senha, udpSocket) is True):
      clear()
      break
  return usuario

#Captura e trata mensagens enviadas ao usuario de outras e verificações do servidor
def interceptarMensagens(estado, porta, ipServidor):

  arquivo = open('msg-box.txt', 'a+')
  s = Socket(None, None, porta)
  s.getClientSocket().bind(('', porta))
  s.getClientSocket().settimeout(3)
  
  t = threading.currentThread()  
  #Executa o loop enquanto a thread estiver viva
  while (getattr(t, "do_run", True)):
    try:
      mensagem, remetente = s.getClientSocket().recvfrom(2048)
      ipRemetente = remetente[0]
      #Recebeu uma verificação de atividade do servidor, envia resposta
      if(mensagem.decode() == 'CHECK'):   
        s.getClientSocket().sendto('OK'.encode(), (remetente))       
      #Usuário está na conversa com o remetente?
      elif(1>20):#if(estado.getEstado()):
        #Se sim, printa a mensagem formatadinha, bonitinha
        '''mostrarMensagem(mensagem, remetente)'''
        pass
      else:
        print()
        #Se não, salva na caixa de mensagem para mostrar posteriormente
        '''arquivarMensagem(mensagem, remetente)'''
        
    except socket.timeout:
      pass

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')
        
def ajuda():
  return ('\nUse os comandos:\nLIST: para ver quem está online\nTALK  <nomeDoUsuario>: para iniciar uma conversa '
  + 'com alguém\nINFO: para ver detalhes da sessão\nHELP: para mostrar este guia de novo\nCLEAR: para limpar a tela.\n'
  + 'OUT : para fazer logout\nOFF : para sair do programa')

def info(dataLogin, usuario, udpSocket):
  hostIp = socket.gethostbyname(socket.gethostname())
  data = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
  return "\t- Dados da Sessão - \nNome do Usuario: %s\nData: %s\nLogado desde: %s\nEndereço do Usuário: %s\nPorta do Servidor: %s\nEndereço do Servidor: %s\n" % (usuario, data, dataLogin, hostIp, udpSocket.getPortaServidor(), udpSocket.getIpServidor())

def chat(udpSocket, usuario, estado):
  udpSocket.getClientSocket().settimeout(5)
  
  dataLogin = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
  guia = ajuda()
  print ("\nOlá %s. Converse agora com seus amigos!" % (usuario, ) + guia + "\n")
  while True:
    comando = input("\n:")
    if(comando == 'INFO'):
      print (info(dataLogin, usuario, udpSocket))
    elif (comando[:4] == 'TALK'):
      talk(comando, usuario, udpSocket)
    elif (comando == 'HELP'):
      print (guia)
    elif (comando == 'CLEAR'):
      clear()
      print (guia)
    elif (comando == 'LIST'):
      listarUsuarios(usuario, udpSocket)
    elif (comando == 'OFF'):
      off()
    elif(comando == 'OUT'):
      if(input('\nDeseja mesmo SAIR para a tela de login? S/N: ') == 'S'):
        logout(usuario, udpSocket)
        clear()
        return True
  return False
  

def talk(comando, usuario, udpSocket):
   lista = obterUsuariosOnlines(usuario, udpSocket)

   if (lista.__len__() == 0):
     print("Não há outros usuários disponivéis para conversar.")
     return

   try:
      for i in lista:
         i = i.split(':')
         if (i[0] == comando.split('TALK ')[1]):
            print (('REQUEST_IP_FROM: %s' % i[1]))
            enviarMensagem(('REQUEST_IP_FROM[=|=]%s' % i[1]).encode(), udpSocket)
            break
      print ("\nO usuário informado não está online.")
   except IndexError:
      print("\nVocê deve fornecer o nome de usário que deseja conversar")

def main():
  try:
    #Obtendo um objeto Socket que é formado pelos prâmentros do arquivo de configuração
    udpSocket = lerArquivoDeConfiguracao()

    #Instancia um objeto Status que será usado no chat
    estado = Status()
    
    #Cria uma thread que capta mensagens endereçadas para o cliente
    chatThread = threading.Thread(target=interceptarMensagens, args=(estado, udpSocket.getMinhaPorta(), udpSocket.getIpServidor()))
    chatThread.start()
  
    #Cria uma thread que responde as checagens periodicas do servidor
    #checkThread = threading.Thread(threading.Thread(target=verificacaoDeAtividade, args=(udpSocket.getIpServidor())))
    #checkThread.start()    
    
    #Exibe o login ao  usuario, logo começa o programa de fato
    while True:
      usuario = None
      usuario = login(udpSocket)
      if(chat(udpSocket, usuario, estado) == False):
        break

  except socket.timeout:
    print("TIMEOUT: O servidor não está respondendo. Tente novamente mais tarde!")
    sys.exit(-3)
  except ConnectionResetError:
    print("\nSEM CONEXAO:Parece que o servidor está com problemas!\nO programa não pôde prosseguir e foi interrompido.")
    sys.exit(-2)
  except KeyboardInterrupt:
    print("\nFinalizando...")

  finally:
    chatThread.do_run = False
    chatThread.join()
    try:
      if (usuario != None):
        logout(usuario, udpSocket)
    except Exception as e:
      print(e)
      pass
    
    input('Pressione ENTER para continuar...')  
    return 0
  

if __name__== "__main__":
  main()
  sys.exit()


