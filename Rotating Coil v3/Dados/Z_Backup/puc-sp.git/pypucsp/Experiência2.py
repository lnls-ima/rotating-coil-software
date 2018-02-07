#!/usr/bin/python
# -*- coding: utf-8 -*-

import PUC_2v6
import sys
import time
import serial
import numpy as np
import math
import matplotlib.pyplot as plt

p=PUC_2v6.Serial_PUC()

def gera_curva_senoidal(Amp,nPontos,offset=0):

    option = int(input('1 = 16-Bit ; 2 = 18-Bit'))
    if option ==2:
      
    flashPoints = 32768
    nCiclos = int((
    
