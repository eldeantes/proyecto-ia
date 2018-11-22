#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets  import QMainWindow, QWidget, QPushButton, QLineEdit, QInputDialog, QApplication,QMessageBox
import sys
import random
from deap import base, creator, tools, algorithms
import numpy
import networkx as nx
import matplotlib.pyplot as plt

#Variables globales
entradas_generales = []
puertas = []
puertas_ideal = []
salida_ideal = []
salidas = []
puertas_defectuosas_general = []
conexiones_defectuosas_general = []
salon_fama1 = []
soluciones = []
fitness_soluciones = []

class Puerta:
    def __init__(self, index, tipo, conexiones, defectuosa):
        self.index = index
        self.tipo = tipo
        self.conexiones = conexiones
        self.defectuosa = defectuosa

    def get_salida(self):
        if(self.es_defectuosa()):
            return 0
        else:
            return self.salida

    def es_defectuosa(self):
        return self.defectuosa
    
    def asignar_salida(self, entrada1, entrada2):
        a = entrada1
        b = entrada2
        if(self.es_defectuosa()):
            self.salida = 0
        else:
            tipos_puerta = {0:a or b, #OR
                           1:a and b, #AND
                            #Solo coge la primera conexion si es NOT
                           2:not a, #NOT
                           3:not(a and b), #NAND
                           4:a and not(b) or not(a) and b, #XOR
                           5:not(a or b), #NOR
                           6:not(a and not(b) or not(a) and b)} #XNOR

            self.salida = tipos_puerta.get(self.tipo, 'default')
    
    def get_tipo(self):
        tipos_puerta = {0:'OR', #OR
                       1:'AND', #AND
                        #Solo coge la primera conexion si es NOT
                       2:'NOT', #NOT
                       3:'NAND', #NAND
                       4:'XOR', #XOR
                       5:'NOR', #NOR
                       6:'XNOR'} #XNOR
            
        return tipos_puerta.get(self.tipo, 'ERROR')

    def __str__(self):
        return 'Puerta {}, Conexiones: {}, Defectuosa: {}, Tipo: {}, Salida: {}'.format(self.index, self.conexiones, self.defectuosa, self.get_tipo(), self.get_salida())


#Genera 10 entradas de tamano n para probarlas con los circuitos.
def generar_entradas(n):
    for i in range(0,10):
        entrada = numpy.random.choice([0, 1], size=(int(n),))
        entradas_generales.append(entrada)


#Dibuja el circuito en una imagen y lo escribe en un fichero
def representa_circuito(entradas,puertas,imagen,archivo,c_def=[]):
    
    #Para la representacion en imagen
    c = nx.DiGraph()
    
    colores = []

    for e in range(len(entradas)):
        color = 'bisque'
        if(entradas[e]==1):
            color = 'blue'
        c.add_node('E{}'.format(e),pos=(-1,e))
        colores.append(color)

    for p in puertas:
        color = 'bisque'
        capa_puerta = p.index//len(entradas)
        y = p.index-capa_puerta*len(entradas)
        if(p.salida==1):
            color = 'blue'
        if(p.defectuosa==1):
            color = 'red' 
        
        c.add_node('{} {}'.format(p.index,p.get_tipo()),pos=(capa_puerta,y))
        colores.append(color)

    for p in puertas:  
        puerta1 = p.conexiones[0]
        if(puerta1>=0):
            puerta1 = '{} {}'.format(puerta1,puertas[puerta1].get_tipo())
        else:
            puerta1 = 'E{}'.format((puerta1+1)*-1)
        puerta2 = p.conexiones[1]
        if(puerta2>=0):
            puerta2 = '{} {}'.format(puerta2,puertas[puerta2].get_tipo())
        else:
            puerta2 = 'E{}'.format((puerta2+1)*-1)

        if not c_def:
            c.add_edges_from([(puerta1,'{} {}'.format(p.index,p.get_tipo())),(puerta2,'{} {}'.format(p.index,p.get_tipo()))],color='black')
        else:
            #Puede que el algoritmo haga uso de una conexion defectuosa
            for x in range(0, len(c_def)):
                #Puerta z a Puerta j
                if(c_def[x][0]==str(p.conexiones[0]) and c_def[x][1]==str(p.index)):
                    c.add_edge(puerta1,'{} {}'.format(p.index,p.get_tipo()),color='pink')
                #Puerta w a Puerta j
                if(c_def[x][0]==str(p.conexiones[1]) and c_def[x][1]==str(p.index)):
                    c.add_edge(puerta2,'{} {}'.format(p.index,p.get_tipo()),color='pink')          
            if (puerta1,'{} {}'.format(p.index,p.get_tipo())) not in c.edges():
                c.add_edge(puerta1,'{} {}'.format(p.index,p.get_tipo()),color='black')
            if (puerta2,'{} {}'.format(p.index,p.get_tipo())) not in c.edges():
                c.add_edge(puerta2,'{} {}'.format(p.index,p.get_tipo()),color='black')
            
    colores_conex = [c[u][v]['color'] for u,v in c.edges()]
    pos = nx.get_node_attributes(c,'pos')
    nx.draw(c,pos,node_color=colores,edge_color=colores_conex,node_size=1200,with_labels=True)

    #Para mostrar la leyenda
    plt.plot([],[],'blue',label="Salida = 1")
    plt.plot([],[],'bisque',label="Salida = 0")  
    plt.plot([],[],'red',label="Puerta defectuosa")
    plt.plot([],[],'pink',label="Conexion defectuosa")
    plt.legend(bbox_to_anchor=(1,1), loc="best")
    
    #Para la representacion en texto
    file = open(archivo,"w") 

    for i in range(0,len(puertas)):
        print('PUERTA NUMERO: {}'.format(puertas[i].index))
        print('TIPO PUERTA: {}'.format(puertas[i].get_tipo()))
        print('CONEXIONES: {}'.format(puertas[i].conexiones))
        print('SALIDA: {}'.format(puertas[i].get_salida()))
    
        file.write('------------------------------------------------------PUERTA NUMERO: {} \n'.format(puertas[i].index)) 
        file.write('TIPO PUERTA: {} \n'.format(puertas[i].get_tipo()))
        file.write('CONEXIONES: {} \n'.format(puertas[i].conexiones))
        file.write('SALIDA: {} \n\n'.format(puertas[i].get_salida()))

    file.close()
    
    #Guardamos la imagen
    plt.savefig(imagen,bbox_inches="tight")
    plt.close()



#Representar circuito a partir de cromosoma
def reconstruct(individuo, entradas, puertas_defectuosas, conexiones_defectuosas,sf_index=0):
    diferencia = 0
    i=0
    puertas_algoritmo = []
    salidas_algoritmo = []
    entradas_algoritmo = entradas
    n = int(len(entradas))
    m = int(len(individuo)/(3*len(entradas)))
    
    entrada1 = 0
    entrada2 = 0
    while i < (3*n*m):
        j = i//3
        
        tipo = int(individuo[i].strip())%6
        i+=1
        conexion1 = int(individuo[i].strip())
        i+=1
        conexion2 = int(individuo[i].strip())
        i+=1
        
        #Las conexiones no se pueden repetir
        if(conexion1 == conexion2):
            diferencia = 1000
            break
        
        puerta_origen1 = -1
        puerta_origen2 = -1
        
        #Primera capa
        if(j<n):
            if((conexion1-n) == conexion2 or (conexion2-n) == conexion1):
                    diferencia = 1000
                    break
            if(conexion1 < n):
                entrada1 = entradas_algoritmo[conexion1]
                puerta_origen1 = -1*(conexion1+1)
            else:
                entrada1 = entradas_algoritmo[conexion1-n]
                puerta_origen1 = -1*(conexion1-n+1)
                
            if(conexion2 < n):
                entrada2 = entradas_algoritmo[conexion2]
                puerta_origen2 = -1*(conexion2+1)
            else:
                entrada2 = entradas_algoritmo[conexion2-n]
                puerta_origen2 = -1*(conexion2-n+1)
                
        #Segunda capa    
        elif(j>=n and j<2*n):
            
            if(conexion1 < n):
                entrada1 = entradas_algoritmo[conexion1]
                puerta_origen1 = -1*(conexion1+1)
            else:
                entrada1 = puertas_algoritmo[conexion1-n].get_salida()
                puerta_origen1 = conexion1-n
                
            if(conexion2 < n):
                entrada2 = entradas_algoritmo[conexion2]
                puerta_origen2 = -1*(conexion2+1)
            else:
                entrada2 = puertas_algoritmo[conexion2-n].get_salida()
                puerta_origen2 = conexion2-n
    

        #Resto de capas
        else:
            capa_actual = j//n
            
            
            if(conexion1 < n):
                puerta_origen1 = ((capa_actual-2)*n)+conexion1
                entrada1 = puertas_algoritmo[puerta_origen1].get_salida()
            else:
                puerta_origen1 = ((capa_actual-1)*n)+(conexion1-n)
                entrada1 = puertas_algoritmo[puerta_origen1].get_salida()
                
            if(conexion2 < n):
                puerta_origen2 = ((capa_actual-2)*n)+conexion2
                entrada2 = puertas_algoritmo[puerta_origen2].get_salida()
            else:
                puerta_origen2 = ((capa_actual-1)*n)+(conexion2-n)
                entrada2 = puertas_algoritmo[puerta_origen2].get_salida()
                
                
        
        #Comprobamos si el indice de la puerta se corresponde a una defectuosa
        defectuosa = 0
        if (len(puertas_defectuosas)!=0 and str(j) in puertas_defectuosas):
            defectuosa = 1
        
        #Comprobamos si la conexion es defectuosa
        for x in range(0, len(conexiones_defectuosas)):
            #Conexion1 a Puerta j
            if(conexiones_defectuosas[x][0]==str(puerta_origen1) and conexiones_defectuosas[x][1]==str(j)):
                entrada1 = 0
                
            #Conexion2 a Puerta j
            if(conexiones_defectuosas[x][0]==str(puerta_origen2) and conexiones_defectuosas[x][1]==str(j)):
                entrada2 = 0
        
        #Se crea la puerta, se le asigna la salida y se anade a la lista de puertas
        puerta = Puerta(j, tipo, [puerta_origen1,puerta_origen2], defectuosa)
        puerta.asignar_salida(entrada1,entrada2)
        puertas_algoritmo.append(puerta)

        
    salidas_algoritmo = []
    if(diferencia!=1000):
        for i in range(m*n-n, m*n):
            salidas_algoritmo.append(puertas_algoritmo[i].get_salida()) 
    
    #Representación en imagen y texto
    img_path = 'docs/circuito_reconstruido{}.png'.format(sf_index)
    txt_path = 'docs/circuito_reconstruido{}.txt'.format(sf_index)

    representa_circuito(entradas,puertas_algoritmo, img_path, txt_path ,c_def=conexiones_defectuosas)

    return puertas_algoritmo



#Partiendo de un conjunto de puertas que forman el circuito, y un vector entrada, simula
#el comportamiento del circuito, con la posibilidad de incluir puertas y conexiones defectuosas
def simula_circuito(entrada, puertas, conexiones_defectuosas):
    i=0
    salidas_algoritmo = []
    entradas_algoritmo = entrada
    puertas_algoritmo = puertas
    n = int(len(entradas_algoritmo))
    m = int(len(puertas_algoritmo)/(len(entradas_algoritmo)))
    
    entrada1 = 0
    entrada2 = 0
    while i < (n*m):

        conexion1 = puertas_algoritmo[i].conexiones[0]
        conexion2 = puertas_algoritmo[i].conexiones[1]
        
        #Primera capa
        if(i<n):
            puerta_origen1 = -1*(conexion1+1)
            entrada1 = entradas_algoritmo[puerta_origen1]
            puerta_origen2 = -1*(conexion2+1)
            entrada2 = entradas_algoritmo[puerta_origen2]
                
        #Segunda capa    
        elif(i>=n and i<2*n):
            
            if(conexion1 < 0):
                puerta_origen1 = -1*(conexion1+1)
                entrada1 = entradas_algoritmo[puerta_origen1]
            else:
                entrada1 = puertas_algoritmo[conexion1].get_salida()
                
            if(conexion2 < 0):
                puerta_origen2 = -1*(conexion2+1)
                entrada2 = entradas_algoritmo[puerta_origen2]
            else:
                entrada2 = puertas_algoritmo[conexion2].get_salida()
    

        #Resto de capas
        else:
            entrada1 = puertas_algoritmo[conexion1].get_salida()
            entrada2 = puertas_algoritmo[conexion2].get_salida()
        
        #Comprobamos si la conexion es defectuosa
        for x in range(0, len(conexiones_defectuosas)):
            #Conexion1 a Puerta j
            if(conexiones_defectuosas[x][0]==str(conexion1) and conexiones_defectuosas[x][1]==str(i)):
                entrada1 = 0
                
            #Conexion2 a Puerta j
            if(conexiones_defectuosas[x][0]==str(conexion2) and conexiones_defectuosas[x][1]==str(i)):
                entrada2 = 0
        
        #Se actualiza la salida
        puertas_algoritmo[i].asignar_salida(entrada1,entrada2)

        i = i+1

    for i in range(m*n-n, m*n):
        salidas_algoritmo.append(puertas_algoritmo[i].get_salida())

    return salidas_algoritmo


#Algoritmo genético
def algoritmo(entradas,puertas_defectuosas,conexiones_defectuosas,poblacion_input,generaciones_input):

    #Longitud del vector entradas es n
    #Longitud del vector capas es m
    #Longitud del vector puertas es de m*n
    m = len(puertas)//len(entradas)
    n = len(entradas)
    file = open("docs/resultado_algoritmo.txt","w") 

    creator.create('FitnessM', base.Fitness, weights=(-1.0,))
    creator.create('IndividuoM', list, fitness = creator.FitnessM)
    toolbox1 = base.Toolbox()


    toolbox1.register("gen", random.randint, 0, 2*n-1)
    toolbox1.register('individuo', tools.initRepeat,
                                  container=creator.IndividuoM, func=toolbox1.gen, n=3*m*n)

    toolbox1.register('poblacion', tools.initRepeat,
                      container=list, func=toolbox1.individuo, n=int(poblacion_input))



    def fenotipo(individuo):
        diferencia = 0
        i=0
        puertas_algoritmo = []
        salidas_algoritmo = []
        entradas_algoritmo = entradas
        
        entrada1 = 0
        entrada2 = 0
        while i < 3*m*n:
            j = i//3
            
            tipo = individuo[i]%6
            i+=1
            conexion1 = individuo[i]
            i+=1
            conexion2 = individuo[i]
            i+=1
            
            #Las conexiones no se pueden repetir
            if(conexion1 == conexion2):
                diferencia = 1000
                break
            
            puerta_origen1 = -1
            puerta_origen2 = -1
            
            #Primera capa
            if(j<n):
                if((conexion1-n) == conexion2 or (conexion2-n) == conexion1):
                    diferencia = 1000
                    break
                if(conexion1 < n):
                    entrada1 = entradas_algoritmo[conexion1]
                    puerta_origen1 = -1*(conexion1+1)
                else:
                    entrada1 = entradas_algoritmo[conexion1-n]
                    puerta_origen1 = -1*(conexion1-n+1)
                    
                if(conexion2 < n):
                    entrada2 = entradas_algoritmo[conexion2]
                    puerta_origen2 = -1*(conexion2+1)
                else:
                    entrada2 = entradas_algoritmo[conexion2-n]
                    puerta_origen2 = -1*(conexion2-n+1)
                    
            #Segunda capa    
            elif(j>=n and j<2*n):
                
                if(conexion1 < n):
                    entrada1 = entradas_algoritmo[conexion1]
                    puerta_origen1 = -1*(conexion1+1)
                else:
                    entrada1 = puertas_algoritmo[conexion1-n].get_salida()
                    puerta_origen1 = conexion1-n
                    
                if(conexion2 < n):
                    entrada2 = entradas_algoritmo[conexion2]
                    puerta_origen2 = -1*(conexion2+1)
                else:
                    entrada2 = puertas_algoritmo[conexion2-n].get_salida()
                    puerta_origen2 = conexion2-n
        

            #Resto de capas
            else:
                capa_actual = j//n
                
                
                if(conexion1 < n):
                    puerta_origen1 = ((capa_actual-2)*n)+conexion1
                    entrada1 = puertas_algoritmo[puerta_origen1].get_salida()
                else:
                    puerta_origen1 = ((capa_actual-1)*n)+(conexion1-n)
                    entrada1 = puertas_algoritmo[puerta_origen1].get_salida()
                    
                if(conexion2 < n):
                    puerta_origen2 = ((capa_actual-2)*n)+conexion2
                    entrada2 = puertas_algoritmo[puerta_origen2].get_salida()
                else:
                    puerta_origen2 = ((capa_actual-1)*n)+(conexion2-n)
                    entrada2 = puertas_algoritmo[puerta_origen2].get_salida()
                    
                    
            #Creamos la puerta y asignamos la salida a partir de entrada1 y entrada2
            
            #Comprobamos si el índice de la puerta se corresponde a una defectuosa
            defectuosa = 0
            if (len(puertas_defectuosas)!=0 and str(j) in puertas_defectuosas):
                defectuosa = 1
            
            #Comprobamos si la conexion es defectuosa
            for x in range(0, len(conexiones_defectuosas)):
                #Conexion1 a Puerta j
                if(conexiones_defectuosas[x][0]==str(puerta_origen1) and conexiones_defectuosas[x][1]==str(j)):
                    entrada1 = 0
                    
                #Conexion2 a Puerta j
                if(conexiones_defectuosas[x][0]==str(puerta_origen2) and conexiones_defectuosas[x][1]==str(j)):
                    entrada2 = 0
            
            #Se crea la puerta, se le asigna la salida y se añade a la lista de puertas
            puerta = Puerta(j, tipo, [puerta_origen1,puerta_origen2], defectuosa)
            puerta.asignar_salida(entrada1,entrada2)
            puertas_algoritmo.append(puerta)

            
        salidas_algoritmo = []
        
        if(diferencia!=1000):
            for i in range(m*n-n, m*n):
                salidas_algoritmo.append(puertas_algoritmo[i].get_salida())

        return salidas_algoritmo, puertas_algoritmo, diferencia
            
    def evaluar_individuo(individuo):
        salidas_individuo, puertas_individuo, diferencia_individuo = fenotipo(individuo)
        

        #Calcula la diferencia entre el circuito individuo y el circuito ideal para varias entradas
        #diferencia_individuo representa el número de entradas para las cuales el circuito individuo
        #no es igual al circuito ideal.
        if(diferencia_individuo==0):
            for i in range(0, len(entradas_generales)):
                salida_ideal_entrada = simula_circuito(entradas_generales[i], puertas_ideal, [])
                salida_entrada = simula_circuito(entradas_generales[i], puertas_individuo, conexiones_defectuosas_general)
            
                if salida_ideal_entrada != salida_entrada:
                    diferencia_individuo = diferencia_individuo+1
    
        return [diferencia_individuo,]

    toolbox1.register('evaluate', evaluar_individuo)


    toolbox1.register('mate', tools.cxOnePoint)
    toolbox1.register('mutate', tools.mutUniformInt, low=0, up=2*n-1, indpb=0.2)
    toolbox1.register('select', tools.selTournament, tournsize=3)
    global salon_fama1
    salon_fama1 = tools.HallOfFame(3)

    estadisticas = tools.Statistics(lambda ind: ind.fitness.values)
    estadisticas.register("mínimo", numpy.min)
    estadisticas.register("media", numpy.mean)
    estadisticas.register("máximo", numpy.max)

    poblacion_inicial = toolbox1.poblacion()
    poblacion_final, registro = algorithms.eaSimple(poblacion_inicial,
                                                    toolbox1,
                                                    cxpb=0.3,  # Probabilidad de cruzamiento
                                                    mutpb=0.2,  # Probabilidad de mutación
                                                    ngen=int(generaciones_input),  # Número de generaciones
                                                    verbose=False,
                                                    stats=estadisticas,
                                                    halloffame=salon_fama1)

    for individuo in poblacion_final:
        file.write('{}, {}'.format(individuo, toolbox1.evaluate(individuo)))
        file.write('\n')

    file.write('Las tres mejores soluciones encontradas han sido:\n')

    sf=1
    for individuo in salon_fama1:
        file.write('Individuo con fitness: {0}\n{1}\n'.format(individuo.fitness.values[0],individuo))
        ind = str(individuo).replace("[","")
        ind = ind.replace("]","")
        puertas_individuo = reconstruct(ind.split(","), entradas, puertas_defectuosas, conexiones_defectuosas,sf)
        
        soluciones.append(list(puertas_individuo))
        fitness_soluciones.append(individuo.fitness.values[0])
        sf+=1

    file.write(str(registro))
    file.write('\n')
    file.close()



#INTERFAZ GRÁFICA:

class Interfaz(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      


        #Primer botón, para generar el circuito e inicializar el problema
        btn1 = QPushButton("Generar circuito", self)
        btn1.move(30, 50)

        #Segundo botón, para diagnosticar si el circuito tiene algún error
        btn2 = QPushButton("Diagnosticar", self)
        btn2.move(150, 50)

        #Tercer botón, para comprobar la salida esperada y la obtenida en el circuito principal para cada entrada
        btn3 = QPushButton("Test entradas", self)
        btn3.move(270, 50)

        #Cuarto botón, para comprobar las salidas esperadas y obtenidas en los tres mejores circuito solución
        btn4 = QPushButton("Test soluciones", self)
        btn4.move(390, 50)
      
        btn1.clicked.connect(self.genera_circuito)            
        btn2.clicked.connect(self.diagnosticar)         
        btn3.clicked.connect(self.prueba_entradas)      
        btn4.clicked.connect(self.prueba_soluciones)
        
        self.statusBar()

        
        self.setGeometry(600, 600, 520, 150)
        self.setWindowTitle('Reparación de circuitos')
        self.show()


    #Comprueba las soluciones obtenidas por el algoritmo genético y su rendimiento
    def prueba_soluciones(self):
        if(len(soluciones) == 0):
            QMessageBox.question(self, 'PyQt5 message', "No se han encontrado soluciones. Primero hay que diagnosticar el circuito.", QMessageBox.Ok)
        else:
            for i in range(len(soluciones)):
                for j in range(len(entradas_generales)):
                    salida_ideal = simula_circuito(entradas_generales[j], puertas_ideal, [])
                    salida = simula_circuito(entradas_generales[j], soluciones[i], conexiones_defectuosas_general)
                    funciona = 'Funciona para la siguiente entrada'
                    if(salida_ideal!=salida):
                        funciona = 'No funciona para la siguiente entrada'
                    QMessageBox.question(self, 'PyQt5 message', "Solución {}: Es capaz de simular {} de 10 entradas.\n {}.\nEntrada: {}, Salida ideal: {}, Salida obtenida: {}".format(i, (10-int(fitness_soluciones[i])), funciona, entradas_generales[j], salida_ideal, salida), QMessageBox.Ok)        

    
    #Comprueba las salidas obtenidas y las esperadas en el circuito base
    def prueba_entradas(self):
        for i in range(len(entradas_generales)):
            salida_ideal = simula_circuito(entradas_generales[i], puertas_ideal, [])
            salida = simula_circuito(entradas_generales[i], puertas, conexiones_defectuosas_general)
            QMessageBox.question(self, 'PyQt5 message', "Entrada: {}, Salida ideal: {}, Salida obtenida: {}".format(entradas_generales[i], salida_ideal, salida), QMessageBox.Ok)        


    #Comprueba si hay errores. En caso de haberlos, permite inicializar el algoritmo genético.
    def diagnosticar(self):

       diferencia_diagnostico = 0
       for i in range(0, len(entradas_generales)):
        salida_ideal_entrada = simula_circuito(entradas_generales[i], puertas_ideal, [])
        salida_entrada = simula_circuito(entradas_generales[i], puertas, conexiones_defectuosas_general)
        
        if salida_ideal_entrada != salida_entrada:
            diferencia_diagnostico = diferencia_diagnostico+1

       if diferencia_diagnostico!=0:
          buttonReply = QMessageBox.question(self, 'PyQt5 message', "Circuito dañado. Salida esperada: {}. Salida obtenida: {}. ¿Reparar circuito?".format(salida_ideal,salidas), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
          if buttonReply == QMessageBox.Yes:
              poblacion_input, ok = QInputDialog.getText(self, 'Configuración', 
               'Número de población:')
              generaciones_input, ok = QInputDialog.getText(self, 'Configuración', 
               'Número de generaciones:')
              algoritmo(entradas_generales[0],puertas_defectuosas_general,conexiones_defectuosas_general,poblacion_input,generaciones_input)
          else:
              print('No.')
       else:
          QMessageBox.question(self, 'PyQt5 message', "El circuito funciona correctamente. Comprueba las imágenes.", QMessageBox.Ok)


       return diferencia_diagnostico           


    #Genera el circuito y obtiene las puertas y conexiones defectuosas.
    def genera_circuito(self, defecto):
       global puertas_defectuosas_general
       global conexiones_defectuosas_general
       global puertas_ideal
       defecto = 0
       buttonReply = QMessageBox.question(self, 'PyQt5 message', "¿Usar la versión de prueba? (En caso negativo, se preguntarán los parámetros)", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
       if buttonReply == QMessageBox.Yes:
              defecto = 1


       if(defecto==0):     
           m, ok = QInputDialog.getText(self, 'Configuración', 
                   'Número de capas:')

           n, ok = QInputDialog.getText(self, 'Configuración', 
                   'Número de puertas:')

           puertas_defectuosas, ok = QInputDialog.getText(self, 'Configuración', 
                   'Índice de las puertas defectuosas SEPARADAS POR COMAS (Ej:52,33,22):')

           conexiones_defectuosas, ok = QInputDialog.getText(self, 'Configuración', 
                   'Indique las conexiones defectuosas (Ej: 3,4;4,6;12,16):')

           generar_entradas(n)



           if(len(puertas_defectuosas)!=0):
             puertas_defectuosas = puertas_defectuosas.split(",")
           else:
             puertas_defectuosas = []


           if(len(conexiones_defectuosas)!=0):
               conexiones_defectuosas = conexiones_defectuosas.split(";")
               for i in range(len(conexiones_defectuosas)):
                   conexiones_defectuosas[i] = conexiones_defectuosas[i].split(",")

           else:
             conexiones_defectuosas = []

           m = int(m)
           n = int(n)



           #Primero se crea el circuito funcionando para obtener la salida ideal
           entradas = entradas_generales[0]

           for i in range(m*n):
               tipo = random.randint(0,6)
               if(i<n):
                   conexion1,conexion2 = random.sample(range(0,n),2)
                   entrada1,entrada2 = entradas[conexion1],entradas[conexion2]
                   conexion1 = -1*(conexion1+1)
                   conexion2 = -1*(conexion2+1)

               elif(i>=n and i<n*2):
                   selector1 = random.randint(0,1)
                   selector2 = random.randint(0,1)
                   conexion1,conexion2 = random.sample(range(0,n),2)

                   if(selector1==0):
                       entrada1 = entradas[conexion1]
                       conexion1 = -1*(conexion1+1)
                   else:
                       entrada1 = puertas[conexion1].get_salida()

                   if(selector2==0):
                       entrada2 = entradas[conexion2]
                       conexion2 = -1*(conexion2+1)
                   else:
                       entrada2 = puertas[conexion2].get_salida()


               else:
                   minimo = ((i//n)-2)*n
                   maximo = (i//n)*n-1
                   conexion1,conexion2 = random.sample(range(minimo,maximo+1),2)
                   entrada1 = puertas[conexion1].get_salida()
                   entrada2 = puertas[conexion2].get_salida()

               
               puerta = Puerta(i, tipo, [conexion1,conexion2], 0)
               puerta.asignar_salida(entrada1,entrada2)
               puertas.append(puerta)


           
           puertas_ideal = list(puertas)
           
           for i in range(m*n-n, m*n):
               salida_ideal.append(puertas[i].get_salida())

           representa_circuito(entradas,puertas, 'docs/circuito_ideal.png', 'docs/circuito_ideal.txt')




           #Se repite el proceso anterior, pero ahora con las puertas y conexiones defectuosas
           for i in range(m*n):
               tipo = puertas[i].tipo
               conexion1 = puertas[i].conexiones[0]
               conexion2 = puertas[i].conexiones[1]
               if(i<n):
                   conexion1 = -1*(conexion1+1)
                   conexion2 = -1*(conexion2+1)
                   
                   entrada1 = entradas[conexion1]
                   entrada2 = entradas[conexion2]

                   conexion1 = -1*(conexion1+1)
                   conexion2 = -1*(conexion2+1)

               elif(i>=n and i<n*2):

                   if(conexion1 < 0):
                      conexion1 = -1*(conexion1+1)
                      entrada1 = entradas[conexion1]
                      conexion1 = -1*(conexion1+1)
                   else:
                       entrada1 = puertas[conexion1].get_salida()

                   if(conexion2 < 0):
                      conexion2 = -1*(conexion2+1)
                      entrada2 = entradas[conexion2]
                      conexion2 = -1*(conexion2+1)
                   else:
                       entrada2 = puertas[conexion2].get_salida()


               else:
                   entrada1 = puertas[conexion1].get_salida()
                   entrada2 = puertas[conexion2].get_salida()

               for x in range(0, len(conexiones_defectuosas)):
                    #Conexion1 a Puerta j
                    if(conexiones_defectuosas[x][0]==str(conexion1) and conexiones_defectuosas[x][1]==str(i)):
                        entrada1 = 0
                        
                    #Conexion2 a Puerta j
                    if(conexiones_defectuosas[x][0]==str(conexion2) and conexiones_defectuosas[x][1]==str(i)):
                        entrada2 = 0   

               defectuosa = 0
               if(str(i) in puertas_defectuosas):
                defectuosa = 1
               puerta = Puerta(i, tipo, [conexion1,conexion2], defectuosa)
               puerta.asignar_salida(entrada1,entrada2)
               puertas[i] = puerta

           for i in range(m*n-n, m*n):
               salidas.append(puertas[i].get_salida())
           
               
            
           puertas_defectuosas_general = puertas_defectuosas
            
           conexiones_defectuosas_general = conexiones_defectuosas
           
           representa_circuito(entradas,puertas,'docs/circuito_defectuoso.png', 'docs/circuito_defectuoso.txt',conexiones_defectuosas)
       else:

           m = 3

           n = 3

           puertas_defectuosas = ['0','3','5']

           conexiones_defectuosas = [['1','4'],['3','8']]
           entradas_generales.extend([[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1],[0,0,0],[0,0,0]])

           #Primero se crea el circuito funcionando para obtener la salida ideal
           entradas = entradas_generales[0]

           #Puerta 0 ----------------------------------------------
           puerta0 = Puerta(0, 0, [-1,-3], 0)
           puerta0.asignar_salida(entradas[0],entradas[2])
           puertas.append(puerta0)

           #Puerta 1 ----------------------------------------------
           puerta1 = Puerta(1, 1, [-2,-1], 0)
           puerta1.asignar_salida(entradas[0],entradas[2])
           puertas.append(puerta1)

           #Puerta 2 ----------------------------------------------
           puerta2 = Puerta(2, 2, [-3,-2], 0)
           puerta2.asignar_salida(entradas[2],entradas[1])
           puertas.append(puerta2)

           #Puerta 3 ----------------------------------------------
           puerta3 = Puerta(3, 3, [-1,1], 0)
           puerta3.asignar_salida(entradas[0],puertas[1].get_salida())
           puertas.append(puerta3)

           #Puerta 4 ----------------------------------------------
           puerta4 = Puerta(4, 4, [1,-3], 0)
           puerta4.asignar_salida(puertas[1].get_salida(),entradas[2])
           puertas.append(puerta4)

           #Puerta 5 ----------------------------------------------
           puerta5 = Puerta(5, 5, [-2,2], 0)
           puerta5.asignar_salida(entradas[1],puertas[2].get_salida())
           puertas.append(puerta5)

           #Puerta 6 ----------------------------------------------
           puerta6 = Puerta(6, 6, [3,4], 0)
           puerta6.asignar_salida(puertas[3].get_salida(),puertas[4].get_salida())
           puertas.append(puerta6)

           #Puerta 7 ----------------------------------------------
           puerta7 = Puerta(7, 1, [5,2], 0)
           puerta7.asignar_salida(puertas[5].get_salida(),puertas[2].get_salida())
           puertas.append(puerta7)

           #Puerta 8 ----------------------------------------------
           puerta8 = Puerta(8, 0, [3,0], 0)
           puerta8.asignar_salida(puertas[3].get_salida(),puertas[0].get_salida())
           puertas.append(puerta8)


           
           puertas_ideal = list(puertas)
           
           for i in range(m*n-n, m*n):
               salida_ideal.append(puertas[i].get_salida())

           representa_circuito(entradas,puertas, 'docs/circuito_ideal.png', 'docs/circuito_ideal.txt')

           #Puerta 0 ----------------------------------------------
           puerta0 = Puerta(0, 0, [-1,-3], 1)
           puerta0.asignar_salida(entradas[0],entradas[2])
           puertas[0] = puerta0

           #Puerta 1 ----------------------------------------------
           puerta1 = Puerta(1, 1, [-2,-1], 0)
           puerta1.asignar_salida(entradas[0],entradas[2])
           puertas[1] = puerta1

           #Puerta 2 ----------------------------------------------
           puerta2 = Puerta(2, 2, [-3,-2], 0)
           puerta2.asignar_salida(entradas[2],entradas[1])
           puertas[2] = puerta2

           #Puerta 3 ----------------------------------------------
           puerta3 = Puerta(3, 3, [-1,1], 1)
           puerta3.asignar_salida(entradas[0],puertas[1].get_salida())
           puertas[3] = puerta3

           #Puerta 4 ----------------------------------------------
           puerta4 = Puerta(4, 4, [1,-3], 0)
           puerta4.asignar_salida(0,entradas[2])
           puertas[4] = puerta4

           #Puerta 5 ----------------------------------------------
           puerta5 = Puerta(5, 5, [-2,2], 1)
           puerta5.asignar_salida(entradas[1],puertas[2].get_salida())
           puertas[5] = puerta5

           #Puerta 6 ----------------------------------------------
           puerta6 = Puerta(6, 6, [3,4], 0)
           puerta6.asignar_salida(puertas[3].get_salida(),puertas[4].get_salida())
           puertas[6] = puerta6

           #Puerta 7 ----------------------------------------------
           puerta7 = Puerta(7, 1, [5,2], 0)
           puerta7.asignar_salida(puertas[5].get_salida(),puertas[2].get_salida())
           puertas[7] = puerta7

           #Puerta 8 ----------------------------------------------
           puerta8 = Puerta(8, 0, [3,0], 0)
           puerta8.asignar_salida(0,puertas[0].get_salida())
           puertas[8] = puerta8

           for i in range(m*n-n, m*n):
               salidas.append(puertas[i].get_salida())
           
               
           puertas_defectuosas_general = puertas_defectuosas
           conexiones_defectuosas_general = conexiones_defectuosas
           
           representa_circuito(entradas,puertas,'docs/circuito_defectuoso.png', 'docs/circuito_defectuoso.txt',conexiones_defectuosas)
       
 
    
        

#Inicio del programa
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interfaz()
    sys.exit(app.exec_())
