# -*- coding: utf-8 -*-
"""
Created on 04/10/2013
Versão 1.0
@author: Ariane Taffarello

Update on 24/06/2016
Biblioteca atualizada para a nova versão do visa (visa 1.8)
@author: Lucas Balthazar
"""
# Importa bibliotecas
import time
import visa

# ******************************************
# Comunicacao GPIB
class GPIB(object):
    def __init__(self):
        try:
            self.Comandos()
        except:
            return None

    def Conectar(self,address):
        try:
            aux = 'GPIB0::'+str(address)+'::INSTR'
##            self.inst = visa.instrument(aux.encode('utf-8')) (Essa instância não esxite mais para o visa 1.8)
            rm = visa.ResourceManager()
            self.inst = rm.open_resource(aux.encode('utf-8'))
            self.inst.timeout = 1
            return True
        except:
            return False

    def Comandos(self):
        try:
            CR = '\r'
            self.LerVolt = ':READ?'
            self.Reset = '*RST'
            self.Limpar = '*CLS'
            self.ConfiguraVolt = ':CONF:VOLT:DC AUTO'
            return True
        except:
            return False
        

    def Enviar(self,comando):
        try:
            self.inst.write(comando)
            return True
        except:
            return False

    def Ler(self):
        try:
##            leitura = self.inst.read(comando)
            leitura = self.inst.read_raw()
            var = leitura#[:-1]
        except:
            var = ''

        return var
    '''
    É possivel utilizar a função 'query' da nova blbioteca visa 1.8.
    Essa função possibilita escrever e ler o comando
    '''

    def Config(self):
        try:
            self.Enviar(self.Limpar)
            self.Enviar(self.Reset)
            self.Enviar(self.ConfiguraVolt)
            return True
        except:
            return False

    def Coleta(self):
        try:
            self.Enviar(self.LerVolt)
            time.sleep(.45)
            dado = self.Ler()
            return float(dado)
        except:
            dado = ''
            return dado


            
        
