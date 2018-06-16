#coding: utf-8
import socket
import threading
import logging
import sys
import time

class Socket:
  __portaServidor, __serverSocket = None, None
  
  def __init__(self, portaServidor):
    self.__portaServidor = portaServidor
    self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  def getPortaServidor(self):
    return self.__portaServidor
  
  def getServerSocket(self):
    return self.__serverSocket 
  
  def setPortaServidor(self, portaServidor):
    self.__portaServidor = portaServidor

  def fecharSocket(self):
    self.__serverSocket.close()
#Fim da classe Socket 

#Lê o arquivo de configuração 'server-setup.txt' e guarda os valores em variáveis
def lerArquivoDeConfiguracao():
  try:
    arquivo = open('server-setup.txt', 'r')
  
    #Percorre as linhas do arquivo
    texto = arquivo.readlines()

    #Obtendo os valores de cada parametro do arquivo de config.
    porta = texto[0].split(':')[1]
  
    arquivo.close()
  except IOError: 
    print ("FATAL: O arquivo de configuração não pôde ser lido ou não existe!")
    sys.exit(-1)

  #Retirando o '\n' do final das strings e instanciando um objeto Socket
  return Socket(int(porta[:len(porta)-1]))

#Verifica se um usuário está online por meio de uma mensagem UDP pela porta do cliente
def estaOnline(s, endereco, porta):
  try:
    resposta, host = s.getServerSocket().sendto('CHECK'.encode(), (endereco, int(porta)))
    print('yo')
  except:return False
  return True

#Realiza uma verificação periodica para detectar quais dos usuários online ainda estão ativos
def verificacaoDeAtiviade():
  s = Socket(18000)
  s.getServerSocket().bind(('', 18000))
  s.getServerSocket().settimeout(3)
  while True:
    arquivo = open('user-status.dbf', 'r+')
    texto = arquivo.readlines()
    for linha in texto:
      if (estaOnline(s, linha.split(':')[1], linha.split(':')[2])):
        print('sd')
        continue
      else:
        deslogarUsuario(arquivo, linha.split(':')[0], None)
    time.sleep(20)
  arquivo.close()
  
      
#Retorna True se o apelido já existe e False se é único
def verificarApelido(apelido):
  #Não pode retornar valor boolean porque so pode enviar dados em bytes pelo UDP
  return 'False'

#Retorna True se o usuario foi cadastrado e salvo com sucesso
def cadastrarUsuario(usuario, senha):
  try:
    arquivo = open('user-data.dbf', 'a+')
    if(arquivo.write('%s[=|=]%s[=|=]\n' % (usuario, senha))):
      arquivo.close()
      return 'True'
    arquivo.close()
  except IOError:
    print ("FATAL: Um erro desconhecido ocorreu!")
    sys.exit(-1)
  return 'False'

#Retorna True se o usuario e senha coincidem com um login e False caso contrario
def autenticarUsuario(usuario, senha):
  try:
    arquivo = open('user-data.dbf', 'r')
  except IOError:
    return 'False'   
  #Percorre as linhas do arquivo
  if(arquivo != None): texto = arquivo.readlines()
  #Obtendo os valores de cada parametro do arquivo de config.
  if texto != None:
    for linha in texto:
      if usuario == linha.split('[=|=]')[0] and senha == linha.split('[=|=]')[1]:
        arquivo.close()
        return 'True'
  return 'False'
  

#Desloga o usuário, pode ser passado None para os campos arquivo e linha OU usuario
#Se o arquivo não for especificado, ele será aberto e será identificada a linha contendo o usuário correto
#Alternativamente, pode-se especificar um arquivo já aberto e a linha onde o usuário está guardado.
def deslogarUsuario(arquivo, linha, usuario):
  
  #Se o arquivo não estiver previamente aberto, será aberto e será identificado no texto o usuário solicitado
  if(arquivo == None):
    try:
      arquivo = open('user-status.dbf', 'r+') #mudar o .txt
      texto = arquivo.readlines()
      
      for linhas in texto:
        if usuario == linha.split(':')[0]:
          linha = linhas
          break
        
    except IOError:
        print('Um erro ocorreu')
        return
    
  if linha != None:
    for i in linha:
      arquivo.write(i.replace(linha, ''))
      print('Usuario deslogado %s' % linha.split(':')[0])
  
  if(usuario == None):
    arquivo.close()
  
  

#Guarda em um arquivo o nome e o endereço de um usuario toda vez que ele ficar online
def logarUsuario(usuario, ipCliente):
  arquivo = open('user-status.dbf', 'a+')
  arquivo.write('%s:%s:%s:\n' % (usuario, ipCliente[0], ipCliente[1]))
  arquivo.close()

#Lista os usuários online em formato de texto para enviar ao cliente
def listarOnline(usuario,serverSocket, ipCliente):
  #String que conterá todos os usuários online
  resposta = ''
  try:
    arquivo = open('user-status.dbf', 'r+')
    #Obtendo os usuarios presente no arquivo de usuarios online
    if(arquivo != None):
      texto = arquivo.readlines()
      if (texto != ''):
        for linha in texto:
          if linha.split(':')[0] != usuario:
            #Insere na variavel de resposta <apelido(usuario)> - <ip> de cada pessoa online
            #resposta = resposta + str('%s - %s\n' % (linha.split(':')[0], linha.split(':')[1]))
            serverSocket.sendto(('%s - %s\n' % (linha.split(':')[0], linha.split(':')[1])).encode(), (ipCliente))
            print(resposta)
        serverSocket.sendto(('END').encode(), (ipCliente))
    arquivo.close()
  except IOError:
    pass
  print(resposta)
  return resposta
    
    

#Thread que escuta e interpereta requisições de login e cadastro de usuário
def interpretarComando(s):
  try:
    serverSocket = s.getServerSocket()
    serverSocket.bind(('', 12000))
    while True:
      #Recebe uma mensagem do cliente que é constituida de:
      #COMANDO[=|=]ARGUMENTO1[=|=]ARGUMENTO2[=|=]
      mensagem, ipCliente = serverSocket.recvfrom(2048)
      mensagem = mensagem.decode()
      
      #teste
      print(mensagem)
      print(ipCliente)
     
      #Separa o comando e o usuario da mensagem
      comando = mensagem.split('[=|=]')[0]
      usuario = mensagem.split('[=|=]')[1]
      
      if (comando == 'LIST'):
        listarOnline(usuario, serverSocket, ipCliente)
        #serverSocket.sendto(listarOnline(usuario).encode(), (ipCliente))
      
      if(comando == 'LOGIN' or comando == 'NEW'):
        senha = mensagem.split('[=|=]')[2]

      #Se o comando é para logar
      if(comando == 'LOGIN'):
        serverSocket.sendto(autenticarUsuario(usuario, senha).encode(), (ipCliente))
    
        #Se o comando é para verificar um apelido
      elif(comando == 'NICK'):
        #Verica se o apelido já existe nos arquivos do servidor e envia a resposta ao cliente
        print(verificarApelido(usuario))
        serverSocket.sendto(verificarApelido(usuario).encode(), (ipCliente))
        print('ok')

      elif(comando == 'NEW'):
        #Salva o novo usuário nos arquivos
        resposta = (cadastrarUsuario(usuario, senha))
        serverSocket.sendto(resposta.encode(), (ipCliente))

  except Exception as e:
    print('Um erro ocorreu')
    logging.fatal(e, exc_info=True) 
    
  finally:
    s.fecharSocket()

s = lerArquivoDeConfiguracao()
loginThread = threading.Thread(target=interpretarComando, args=(s,))
loginThread.start()

#verificacaoThread = threading.Thread(target=verificacaoDeAtiviade)
#verificacaoThread.start()
print("Ready!")
