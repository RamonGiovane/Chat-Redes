#coding: utf-8
import socket
import logging
import subprocess

def servidor():
  try:
    PORTA = 15000 # Porta do servidor

    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpSocket.bind(('', PORTA));
    tcpSocket.listen(1)

    print("Aguardando conexão cliente...")
    while True:
      conexao, cliente = tcpSocket.accept()
      print ("Conexão estabelecida com ", cliente)
		
      while True:
        comando = conexao.recv(2048).decode('utf-8');
        output = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, 
                        universal_newlines=True)
                        
        resposta = output.stdout
        
        if(resposta):
          tamanho = len(resposta)
        else:
          tamanho = 5
        cabecalho = str(tamanho).zfill(10) 
        
        #Tentativa de melhorar a saida de mensagem. É, foi uma tentativa...
        if (resposta == '' or resposta == None):
          if(output.stderr != ''):
            resposta = output.stderr
            print (output.stdout)
          if resposta == None:
            resposta = '\n'
   
        print('Comando solicitado %s' % (comando))
        print('Resultado:\n', resposta)
        resposta = cabecalho + resposta
        
        conexao.send(resposta.encode('utf-8'))
        
  except Exception as e:
    print("Algo sinistro aconteceu\nDetalhes do erro: ", e)
  finally:
    tcpSocket.close()
	
servidor()
