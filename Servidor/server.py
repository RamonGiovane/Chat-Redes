#coding: utf-8
import socket
import threading
import logging
import sys
import time
import re

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


#Apaga uma linha de um arquivo, onde path é o arquivo e index_linha a linha desejada
def apagarLinha(path,index_linha):
  with open(path,'r') as f:
    texto=f.readlines()
  with open(path,'w') as f:
    for i in texto:
      if texto.index(i)==index_linha:
        f.write('')
      else:
        f.write(i)

#Verifica se um usuário está online por meio de uma mensagem UDP pela porta do cliente
def estaOnline(s, endereco, porta):
  serverSck = s.getServerSocket()
  try:
    serverSck.sendto('CHECK'.encode(), (endereco, int(porta)))
    resposta, remetente = serverSck.recvfrom(5)
  except Exception as e:
	  logging.fatal(e, exc_info=True) 
	  return False
  if resposta.decode() != 'OK': return False
  return True

#Realiza uma verificação periodica para detectar quais dos usuários online ainda estão ativos
def verificacaoDeAtividade():
  s = Socket(18000)
  s.getServerSocket().bind(('', 18000))
  s.getServerSocket().settimeout(3)
  arquivo = open('user-status.dbf', 'w+')
  while True:
    time.sleep(2)
    arquivo = open('user-status.dbf', 'r+')
    if (arquivo != None):
      texto = arquivo.readlines()
      for linha in texto:
        if linha != '':
          endereco = linha.split(':')[1]
          porta = linha.split(':')[2]
          #Se recebeu uma resposta (estaOnline retornou True), ignora
          if(estaOnline(s, endereco, porta)):
            continue
          
          #Se não, desconecta o usuário
          else:
            deslogarUsuario(linha.split(':')[0])
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
def deslogarUsuario(usuario):
  nLinha = 0
  try:
        arquivo = open('user-status.dbf', 'r+')
        texto = arquivo.readlines()
        if(texto != None):
          #Percorre o arquivo procurando o usuário a ser desconectado
          for linhas in texto:
            if usuario == linhas.split(':')[0]:
              apagarLinha('user-status.dbf', nLinha)
              arquivo.close()
              print('Usuario saiu:', usuario )
              return
            nLinha = nLinha+1

        print('Não foi possível deslogar o usuário.')
  except Exception as e:
    print (e)
    return
  
#Guarda em um arquivo o nome e o endereço de um usuario toda vez que ele ficar online
def logarUsuario(usuario, ipCliente, porta):
  arquivo = open('user-status.dbf', 'a+')
  arquivo.write('%s:%s:%s\n' % (usuario, ipCliente, porta))
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
      for linha in texto:
        if linha != '' and linha.split(':')[0] != usuario:
          #Insere na variavel de resposta <apelido(usuario)> - <ip> de cada pessoa online
          #resposta = resposta + str('%s - %s\n' % (linha.split(':')[0], linha.split(':')[1]))
          serverSocket.sendto(('%s - %s\n' % (linha.split(':')[0], linha.split(':')[1])).encode(), (ipCliente))
      
      arquivo.close()
  except IOError:
    pass
  finally:
    serverSocket.sendto(('END').encode(), (ipCliente))
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
     
      #Separa o comando e o usuario da mensagem
      comando = mensagem.split('[=|=]')[0] #Todas as mensagens possuem pelo
      usuario = mensagem.split('[=|=]')[1] #menos esses dois parâmetros
     
      if (comando == 'LIST'):
        listarOnline(usuario, serverSocket, ipCliente)
      
      if(comando == 'LOGIN' or comando == 'NEW'):
        senha = mensagem.split('[=|=]')[2]

      #Se o comando é para logar
      if(comando == 'LOGIN'):
        serverSocket.sendto(autenticarUsuario(usuario, senha).encode(), (ipCliente))
        #Obtem o usuario, ip do cliente e a porta pela qual espera mensagens
        porta = mensagem.split('[=|=]')[3]
        logarUsuario(usuario, ipCliente[0], porta)
        print('Usuario logado:', usuario )
        #Se o comando é para verificar um apelido
      elif(comando == 'NICK'):
        #Verica se o apelido já existe nos arquivos do servidor e envia a resposta ao cliente
        serverSocket.sendto(verificarApelido(usuario).encode(), (ipCliente))

      elif(comando == 'NEW'):
        #Salva o novo usuário nos arquivos
        resposta = (cadastrarUsuario(usuario, senha))
        serverSocket.sendto(resposta.encode(), (ipCliente))
      
      elif(comando == 'LOGOUT'):
        deslogarUsuario(usuario)
        serverSocket.sendto('TRUE'.encode(), (ipCliente))
        

  except Exception as e:
    print('Um erro ocorreu')
    logging.fatal(e, exc_info=True) 
    
  finally:
    s.fecharSocket()

s = lerArquivoDeConfiguracao()
loginThread = threading.Thread(target=interpretarComando, args=(s,))
loginThread.start()

verificacaoThread = threading.Thread(target=verificacaoDeAtividade)
verificacaoThread.start()
print("Ready!")
