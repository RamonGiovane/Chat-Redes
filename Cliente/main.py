#coding: utf-8
import getpass as g 
from datetime import date
import socket
import sys
import threading

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
  ATIVO, INATIVO = 'sd', 'ds'
  __ipDest, __ipRemt, __estado = None, None, 'paa'
  
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

  
def listarUsuarios(usuario, udpSocket):
  print ("\tUsuários Online")
  mensagem = ('LIST[=|=]%s' % (usuario))
  lista = enviarMensagem_(mensagem.encode(), udpSocket)
  for i in lista:
    print(i)
  
def finalizar():
  print ("Finalizar")
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
def enviarMensagem(mensagem, s):
  clientSocket = s.getClientSocket()
  try:
    clientSocket.sendto(mensagem, (s.getIpServidor(), s.getPortaServidor()))
    resposta, server = clientSocket.recvfrom(4096)
  except socket.timeout:
     print ("TIMEOUT: O servidor não está respondendo. Tente novamente mais tarde!")
     sys.exit()
  return resposta

#Envia uma mensagem para o servidor e recebe múltiplas respostas
def enviarMensagem_(mensagem, s):
  respostas = []
  clientSocket = s.getClientSocket()
  try:
    clientSocket.sendto(mensagem, (s.getIpServidor(), s.getPortaServidor()))
    while True:
      resposta, server = clientSocket.recvfrom(4096)
      if(resposta.decode() == 'END'): break
      respostas.append(resposta.decode())
      
  except socket.timeout:
     print ("TIMEOUT: O servidor não está respondendo. Tente novamente mais tarde!")
     sys.exit()
  return respostas

#Pergunta ao servidor se o apelido solicitado já existe
def verificarApelido(apelido, s):
  comando = ('NICK[=|=]%s' % apelido).encode()
  return enviarMensagem(comando, s)
    
#Lê os dados de um cadastro de usuário e os envia para o servidor
def novoUsuario(udpSocket):
  print ("\t-Cadastrar Usuário-")
  while True:
    usuario = input ("Qual é o seu apelido?")
    #Verica no servidor o apelido escolhido
    if(verificarApelido(usuario, udpSocket) == 'True'):
      print("Este apelido já está sendo usado por outro usuário!")
    else: break

  while True:
    while True:
      senha  =  g.getpass("Defina uma senha: ")
      if(len(senha)<5):
        print("A senha deve possuir no mínimo 5 caracteres")
      else: break
    csenha =  g.getpass("Confirme a senha: ")
    if (senha != csenha):
      print("As senhas não coincidem\n")
    else: 
      cadastrarUsuario(usuario, senha, udpSocket)
      break
      
#Solicita ao servidor que verifique se o login fornecido é válido
def validarLogin(usuario, senha, udpSocket):
  if (validarCampoLogin(usuario)) and (validarCampoLogin(senha)):
    if (enviarMensagem(('LOGIN[=|=]%s[=|=]%s' % (usuario, senha)).encode(), udpSocket).decode()) == 'True':
      return True
    else:
      print("Usuário ou senha incorreto(s)!\nSolicite o administrador, caso tenha esquecido.\n")
  else: print ("Usuário ou senha inválido(s)!\n\n")
  return False

#Função única que valida requisitos em comum entre usuário e senha, #como tamanho
def validarCampoLogin(x):
  if ((len(x) < 5) or ('[=|=]' in x)):
    return False
  return True

def logout(usuario):
  try:
    enviarMensagem('LOGOUT[=|=]%s' % (usuario))
  except: pass


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
      break
  return usuario

#Captura e trata mensagens enviadas ao usuario
def interceptarMensagens(estado, porta, ipServidor):

  arquivo = open('msg-box.txt', 'a+')
  s = Socket(None, None, porta)
    
  while True:
    try:
      s.getClientSocket().bind(('', porta))
      mensagem, remetente = s.getClientSocket().recvfrom(2048)
      
      #Recebeu uma verificação de atividade do servidor, envia resposta
      if(rementente[1] == ipServidor and mensagem.decode() == 'CHECK'):
        s.getClientSocket().sendto('OK', (ipServidor, ''))
      
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
      
        
def chat(udpSocket, usuario, estado):
  #Cria uma thread que capta mensagens endereçadas para o cliente
  chatThread = threading.Thread(target=interceptarMensagens, args=(estado, udpSocket.getMinhaPorta(), udpSocket.getIpServidor()))
  chatThread.start()
  
  #checkThread = threading.Thread(threading.Thread(target=verificacaoDeAtividade, args=(udpSocket.getIpServidor())))
  #checkThread.start()
  
  hostIP = '127.0.0.1' #Na verdade nao precisa disso
  udpSocket.getClientSocket().settimeout(5)
  data = date.today().strftime('%d/%m/%Y %H:%M')
  
  guia = "Use os comandos:\nLIST: para ver quem está online\nTALK  <nomeDoUsuario>: para iniciar uma conversa com alguém\nINFO: para ver detalhes da sessão\nHELP: para mostrar este guia de novo\nOFF : para sair do chat"
  info = "\t- Dados da Sessão - \nData: %s\nEndereço do Usuário: %s " % (data, hostIP)
  print ("\nOlá %s. Converse agora com seus amigos!" % (usuario, ) + guia + "\n")
  while True:
    comando = input("\n:")
    if(comando == 'INFO'):
      print (info)
    elif (comando == 'HELP'):
      print (guia)
    elif (comando == 'LIST'):
      listarUsuarios(usuario, udpSocket)
    elif (comando == 'OFF'):
      finalizar()
  
    #INSERIR AQUI UM COMANDO PARA LIMPAR A TELA

#print('ULTIMA MODIFICACAO: VERIFICAR APELIDO DO USUARIO FUNCIONANDO 07/06')
try:
  udpSocket = lerArquivoDeConfiguracao()
  estado = Status()
  usuario = login(udpSocket)
  chat(udpSocket, usuario, estado)

except ConnectionResetError:
  print("\nSEM CONEXAO:Parece que o servidor está com problemas!\nO programa não pôde prosseguir e foi interrompido.")
  sys.exit(-2)
except KeyboardInterrupt:
  print("Chat finalizado!")

finally:
  try:
    logout(usuario, udpSocket)
  except:
    pass
