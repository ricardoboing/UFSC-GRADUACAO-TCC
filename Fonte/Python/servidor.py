import socket
import pygame

from threading import Thread, Lock
from bd.agendamento import *
from bd.no_iot import *



SERVER_HOST = "192.168.25.16"#"192.168.50.179"#"192.168.50.179"#
SERVER_PORT = 8085

def ativar_servidor(mutex, eventoAtual):
    serverSocket = socket.socket()
    serverSocket.bind((SERVER_HOST, SERVER_PORT))
    serverSocket.listen()

    print("SERVER CONNECT - HOST: %s | PORT : %s" %(SERVER_HOST, SERVER_PORT))

    pygame.init()
    pygame.mixer.music.load("musica.mp3")

    try:
        while True:
            conexao = serverSocket.accept()[0]
            print("CLIENT CONNECT -------\n")

            operacao = str(ler_conteudo_conexao(conexao,1))

            mutex.acquire()

            # INSERIR EVENTO
            if operacao == 'a':
                print("_INSERIR EVENTO")
                valorDeRetorno = bd_agendamento_insert(conexao)
                eventoAtual.buscar_proximo_evento()

            # REMOVER EVENTO
            elif operacao == 'b':
                print("_REMOVER EVENTO")
                valorDeRetorno = bd_agendamento_remove(conexao)
                eventoAtual.buscar_proximo_evento()

            # UPDATE EVENTO
            elif operacao == 'c':
                print("_UPDATE EVENTO")
                valorDeRetorno = bd_agendamento_update(conexao)
                eventoAtual.buscar_proximo_evento()

            # SELECT EVENTO
            elif operacao == 'd':
                print("_SELECT EVENTO")
                valorDeRetorno = bd_agendamento_select(conexao)

            # SELECT_ALL EVENTO NO BANCO DE DADOS
            elif operacao == 'e':
                print("_SELECT_ALL EVENTO")
                valorDeRetorno = bd_agendamento_select_all()

            # CONTROLE_NO_IOT
            elif operacao == 'f':
                print("_CONTROLE_NO_IOT")
                comando = ler_conteudo_conexao(conexao,1)
                valorDeRetorno = no_iot_enviar_comando()

            # CONTROLE_SOM
            elif operacao == 'g':
                print("_CONTROLE_SOM")
                comando = ler_conteudo_conexao(conexao,1)

                # Comando de alterar o volume do som precisa dos 3 bytes do volume
                if comando != "a":
                    comando += ler_conteudo_conexao(conexao,3)

                valorDeRetorno = som_configurar(comando)

            # GET ESTIMATIVA DE CONSUMO
            elif operacao == "h":
                print("_GET ESTIMATIVA DE CONSUMO")
                valorDeRetorno = bd_no_iot_select_estimativa_de_consumo()

            # REINICIAR ESTIMATIVA DA BATERIA
            elif operacao == "i":
                print("_REINICIAR ESTIMATIVA DA BATERIA")
                valorDeRetorno = bd_no_iot_reset_estimativa_da_bateria()

            # SELECT CONFIGURACOES NO_IOT
            elif operacao == "j":
                print("_SELECT CONFIGURACOES NO_IOT")
                valorDeRetorno = bd_no_iot_select_configuracoes()

            # UPDATE CONFIGURACOES NO_IOT
            elif operacao == "k":
                print("_UPDATE CONFIGURACOES NO_IOT")
                valorDeRetorno = bd_no_iot_update_configuracoes(conexao)

            mutex.release()

            conexao.sendall(valorDeRetorno.encode())

            print ("\nCLIENT DISCONNECT -------\n");
            conexao.close()
    finally:
        conexao.close()
    serverSocket.close()

    mutex.release()

def som_configurar(comando):
    operacao = comando[0:1]

    if operacao == "a":
        pygame.mixer.music.stop()
    else:
        volume = int(comando[1:])
        volume /= 100
        
        pygame.mixer.music.set_volume(volume)

        if operacao == "b":
            pygame.mixer.music.play(-1)

    return "1"

def no_iot_enviar_comando(comando):
    operacao = comando[0:1]

    if operacao == "a":
        print("ATIVAR")
    elif operacao == "b":
        velocidade = comando[1:]
        print("Alterar velocidade | "+velocidade)

    return "1"