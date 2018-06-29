#coding: utf-8
import getpass as g 
import datetime
import socket
import sys
import threading
import logging
import os
from platform import python_version
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
    
#Fim da classe Socket  

#Classe que obtém o status do usuário
class Status():
  
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
  
  def getEstado(self, remt):
    return 1 if (remt == self.__ipRemt) else 0#and (dest == self.__ipDest)) else INATIVO
  
  def setEstado(self, estado):
    self.__estado = estado
  
  def setIpRemt(self, remt):
    self.__ipRemt = remt
    
  def igetEstado(self):
    return self.__estado

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

  if (validarUsuario(usuario)) and (validarSenha(senha)):
    if (enviarMensagem(('LOGIN[=|=]%s[=|=]%s[=|=]%s[=|=]' % (usuario, senha, str(porta))).encode(),
    udpSocket).decode()) == 'True':
      for i in lista:
        if (i.split(':')[0] == usuario):
          print("\nERRO: Login simultâneo, este usuário já está logado.")
          return False
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

#Apaga as mensagens de um remetente da caixa de mensagens do usuário
def apagarMensagens(texto, usuario):
  #Separadores de cada seção do arquivo
  user = ('[=|=]USER:%s[=|=]\n' % (usuario))
  end = ('[=|=]END:%s[=|=]\n' % (usuario))
  i = 0
  found = False
  for palavra in texto:
    i  = i+1
    if (user == palavra):
      found = True
      break
  if(found == False):
	  return False
  del(texto[i:texto.index(end)+1])
  texto.pop(i-1)
  return True

#Imprime na tela as mensagens não lidas de um usuário
def lerMensagensDaCaixa(texto, usuario):
  user = ('[=|=]USER:%s[=|=]\n' % (usuario))
  end = ('[=|=]END:%s[=|=]\n' % (usuario))
  
  l = 0
  index = 0
  for palavra in texto:
    index = index+1
    nome = palavra.split(":")
    if (user == palavra):
      if(usuario in nome[1]):
        l = 1
        break
      
  if(l != 1):
    return
  i = index
  while(True):
    if("[=|=]END" in texto[i]):      
      break
    if(texto[i] != '' and texto[i] != '\n'):
      print("\n%s: %s" % (usuario, texto[i]))
    i = i + 1
  apagarMensagens(texto, usuario)
  gravarCaixaNoArquivo(texto)

#Retorna uma lista com todo o conteúdo da caixa de mensagens do usuário
#Toda a manipulação da caixa deve ser feita na lista. Posteriormente deve-se
#usar o metódo gravarCaixaNoArquivo(lista) para salvar as alterações feitas.
#New deve ser True se a intencao é ler um arquivo ja existente e Flase para criar um novo
def obterCaixaDeMensagens(new):
  texto = []
  try:
    if(new == True):
      arquivo = open('msg-box.dbf', 'r+')
      texto = arquivo.readlines()
      arquivo.close()
      
  except FileNotFoundError:
    arquivo = open('msg-box.dbf', 'w+')
    arquivo.close()
    return texto

  return texto

#Salva as alterações feitas na caixa de mensagem de usuário
def gravarCaixaNoArquivo(texto):
  
  with open('msg-box.dbf', 'w+') as arquivo:
    arquivo.writelines(texto)
 
#Insere uma mensagem de um remetente desconhecido na lista
def adicionarRemetenteNaCaixa(user, end, mensagem, texto):
  texto.append(user)
  texto.append(mensagem)
  texto.append(end)
  
#Insere uma nova mensagem na caixa de mensagem
def armazenarMensagens(texto, remetente, mensagem):
  mensagem = mensagem + '\n'
  #Separadores de cada seção do arquivo
  user = ('\n[=|=]USER:%s[=|=]\n' % (remetente))
  end = ('\n[=|=]END:%s[=|=]\n' % (remetente))
  
  #Se a caixa de mensagem está vazia, insere a primeira mensagem
  if texto == None or texto == '':
    texto = []
    adicionarRemetenteNaCaixa(user, end, mensagem, texto)
    gravarCaixaNoArquivo(texto)
    return

  #Se a caixa possui alguma mensagem, deve-se procurar pelo remetente especifico
  else:
    cont = 0
    for linha in texto:
      if(linha == end):
        #E assim insere a nova mensagem antes do END
        texto.insert(cont, mensagem)
        gravarCaixaNoArquivo(texto)
        return
      cont = cont+1
    
    #Caso o remetente não exista no arquivo
    adicionarRemetenteNaCaixa(user, end, mensagem, texto)
    gravarCaixaNoArquivo(texto)
def mostrarMensagem(mensagem):
  tipo = mensagem.split('[=|=]')[0]
  if(tipo != 'START_CHAT'):
    remetente = mensagem.split('[=|=]')[1]
    conteudo = mensagem.split('[=|=]')[3]
    print('\n%s: %s\n'  % (remetente, conteudo))
#Captura e trata mensagens enviadas ao usuario de outras e verificações do servidor
def interceptarMensagens(estado, porta, ipServidor, texto):
  try:
    lastRemetente = None
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
        mensagem = mensagem.decode()
        if(mensagem == 'CHECK'):   
          s.getClientSocket().sendto('OK'.encode(), (remetente))
               
        #Usuário está na conversa com o remetente?
        elif(estado.getEstado(remetente[0]) == 1):
          #Se sim, printa a mensagem devidamente formatada
          mostrarMensagem(mensagem)
          lastRemetente = None
          pass
        else:
          if (estado.igetEstado() != 1 and lastRemetente != mensagem.split('[=|=]')[1]):
            print('Você tem novas mensagens de %s' % mensagem.split('[=|=]')[1])
            lastRemetente = mensagem.split('[=|=]')[1]
         #Se não, salva na caixa de mensagem para mostrar posteriormente
          if(mensagem.split('[=|=]')[0] != 'START_CHAT'): 
            armazenarMensagens(texto, mensagem.split('[=|=]')[1], mensagem.split('[=|=]')[3])
      except socket.timeout:
        pass
  
  except OSError as x:
    clear()
    print("\nFATAL: Ocorreu um erro de soquete.\nSe estiver tentando abrir duas instâncias do chat, mude as portas no arquivo de configuração.")
    print ("Detalhes do erro:\n", x)
    
    #Força o fechamento do programa já que ele não pode retornar sua execução para a thread principal
    os._exit(-5)
    return

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')
        
def ajuda():
  return ('\nUse os comandos:\nLIST: para ver quem está online\nTALK  <nomeDoUsuario>: para iniciar uma conversa '
  + 'com alguém\nINFO: para ver detalhes da sessão\nHELP: para mostrar este guia de novo\nCLEAR: para limpar a tela.\n'
  + 'OUT : para fazer logout\nOFF : para sair do programa')

def info(dataLogin, usuario, udpSocket):
  
  try:
    hostIp = socket.gethostbyname(socket.gethostname())
  except socket.gaierror:
    hostIp = 'Falha na detecção do endereço'
  
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
      try:
        talk(comando, usuario, udpSocket, estado)
      except Exception as e:
        print(e)
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
        reiniciarCaixa()
        return True
  return False

def limparConversa(destino):
  clear()
  print('Agora, tudo o que você escrever, %s poderá receber!\nTente! Digite algo e tecle ENTER!\nUse:\n/TIME para exibir a data e hora atual\n/CLEAR para limpar a tela\n/OUT para voltar ao MENU.' % destino)
	


def abrirConversa(texto, estado, udpSocket, usuario, destino, ipDestino, portaDestino):
  
  #Toda mensagem é enviada por uma porta aleatoria, porém as mensagens
  #são mandadas para uma porta específica para cada usuário
  sock = udpSocket.getClientSocket()
  sock.sendto(("START_CHAT[=|=]%s[=|=]%s" % (usuario, destino)).encode(), (ipDestino, portaDestino))
  
  #Indica à classe Estado com quem se está conversando
  estado.setIpRemt(ipDestino)
  estado.setEstado(1)
  limparConversa(destino)
  lerMensagensDaCaixa(texto, destino)
  while True:
    mensagem = input('\n:')
    
    if (mensagem == ''): 
      continue
    else:
      i = 0
      achou = 0
      while (i < len(mensagem)):
        if (mensagem[i] != ' '):
          achou = 1
        i=i+1
      if (achou == 0):
        continue
        
    if(mensagem == '/CLEAR'):
      limparConversa(destino)
    elif(mensagem == '/TIME'):
      print('\nData e hora atual: ', datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
    elif(mensagem == '/OUT'):
      #Indica à classe Estado o fim da conversa
      estado.setIpRemt('None')
      estado.setEstado(0)
      clear()
      print('Você deixou o chat com %s' % destino)
      print (ajuda())
      return
    else:
      #Formata a mensagem e envia
      horaAtual = datetime.datetime.now().strftime('%H:%M')
      mensagem_f = ('%s (%s)' % (mensagem, horaAtual))
      sock.sendto(("CHAT[=|=]%s[=|=]%s[=|=]%s[=|=]" % (usuario, destino, mensagem_f)).encode(), (ipDestino, portaDestino))  

def talk(comando, usuario, udpSocket, estado):
  lista = obterUsuariosOnlines(usuario, udpSocket)
  if (lista.__len__() == 0):
    print("Não há outros usuários disponivéis para conversar.")
    return

  comando = comando.split('TALK ')
  
  try:
    if (comando[1] == usuario):
      print("Você está solitário?")
      return
    
    for i in lista:
      i = i.split(':')
      if (i[0] == comando[1]):
        destino = i[0]
        ipDestino = i[1]
        portaDestino = int(i[2])
        
        texto = obterCaixaDeMensagens(True) 
        abrirConversa(texto, estado, udpSocket, usuario, destino, ipDestino, portaDestino)
        return
    print ("\nO usuário informado não está online.")
  
  except IndexError:
    print("\nVocê deve fornecer o nome de usário que deseja conversar")
  except Exception as e:
    print (e)

def reiniciarCaixa():
	os.remove('msg-box.dbf')
	arquivo = open('msg-box.dbf', 'a+')
	arquivo.close()

def verificarVersaoPython():
  versao = python_version()
  if(int(versao[0]) != 3):
    print("FATAL: A versao utilizada do Python (%s) nao e compativel com o programa!\nUtilize a versao 3.0.0 ou superior!" % (versao))
    finalizar()

def main():
  try:
    #Verifica se a versão do Python utilizada é compatível e se é possível prosseguir
    verificarVersaoPython()
    
    #Obtendo um objeto Socket que é formado pelos prâmentros do arquivo de configuração
    udpSocket = lerArquivoDeConfiguracao()

    #Instancia um objeto Status que será usado no chat
    estado = Status()
    
    #Le o arquivo da caixa de mensagens
    caixaMensagem = obterCaixaDeMensagens(False)
    
    #Cria uma thread que capta mensagens endereçadas para o cliente
    chatThread = threading.Thread(target=interceptarMensagens, args=(estado, udpSocket.getMinhaPorta(), udpSocket.getIpServidor(), caixaMensagem))
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
      os.remove('msg-box.dbf')
      udpSocket.fecharSocket()
    except Exception as e:
      print(e)
      pass
    
    input('Pressione ENTER para continuar...')  
    return 0
  

if __name__== "__main__":
  main()
  sys.exit()
