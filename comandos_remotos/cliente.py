#coding:utf-8
import socket
import subprocess
import logging

def executarComandoOffline(comando):
   output = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, 
                        universal_newlines=True)
   
   resposta = output.stdout
      
   if (resposta == '' or resposta == None):
     if(output.stderr != ''):
       resposta = output.stderr
       print (output.stdout)
       if resposta == None:
         resposta = '\n'
                        
   return resposta
   
def conectar():
  arquivo = open('config.txt', 'r')
  texto = arquivo.readlines()

  #Obtendo os valores de cada parametro do arquivo de config.
  HOST = texto[0].split(':')[1].strip()
  PORTA = int(texto[1].split(':')[1].strip())
  
  try:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    enderecoServidor  = (HOST, PORTA)
    tcpSocket.connect(enderecoServidor); 
    return tcpSocket
  except Exception as e:
    return None

def cliente():
  print("\tBem-vindo\nComados de mudança de diretório podem não funcionar corretamente.\nUtilize caminhos absolutos")
  
  tcpSocket = conectar()
  if (tcpSocket is None):
    conexao = False
  else:
    print ("Conexão estabelecida com servidor");
    conexao =  True
     
  #Variavel de controle para exibir um aviso quando o servidor desconectar
  mensagemOffline = True #True significa que a qualquer momento poderá ser exibida
  6
  while True:
    comando = input("\n:");
    if(comando == 'exit'):
      break
    try:
      #Tentando reconectar...
      #if(conexao == False):
       # tcpSocket = conectar()
      #  if(tcpSocket):
      #    print("\nServidor tá de volta, galera!\n")
      #Está comentado por causar problemas >:( Preciso investigar
      
      tcpSocket.send(comando.encode('utf-8'));
      n = 0;
      resposta = tcpSocket.recv(10).decode('utf-8')
      try:
        n = int(resposta)
      except ValueError:
        n = 1024 
		  
      resposta = tcpSocket.recv(n).decode('utf-8')
        

    except:
      #Fechando o socket
      if(conexao):
        tcpSocket.close()
        conexao = False
      
      if(mensagemOffline == True):
        print("\n!O servidor remoto não está conectado!\n")
        mensagemOffline = False
      
      resposta = executarComandoOffline(comando)

    
    print(resposta)

try:
  cliente()

except Exception as e:
  print("Algo sinistro aconteceu.\nDetalhes do erro: ", e)
  logging.fatal(e, exc_info=True) 
 



