--Es necesaria la instalación de los módulos indicados en el código y en el documento pdf.

--Si se ejecuta el fichero "groot.py", se mostrará el menú de inicio.

--Primero se debe pulsar en generar circuito (a partir de ahí seguir los pasos que indique el programa).

--Para generar un circuito nuevo, se debe cerrar el programa e iniciarse de nuevo para un correcto funcionamiento.

--Una vez generado el circuito, se guardará la representación gráfica y textual en la carpeta "docs"
con el nombre de "circuito_defectuoso.png", "circuito_defectuoso.txt", "circuito_ideal.png" y "circuito_ideal.txt".

--Cuando se genere el circuito, se podrán probar las salidas esperadas y obtenidas pulsando "Test entradas".

--Si se pulsa en "Diagnosticar", si el circuito detecta fallos se podrá empezar con el algoritmo genético.

--Se puede modificar desde el programa el tamaño de la población y el número de generaciones, pero para cambiar la probabilidad
de mutación y de cruce, deberá escribirse en el código.

--El algoritmo puede tardar más o menos en función del circuito y los parámetros, por lo que si el programa no responde al ejecutar
el algoritmo habrá que esperar a que termine y vuelva a estar la ventana activa.

--Cuando el algoritmo genético acabe, se podrá probar el rendimiento de las soluciones pulsando en el botón "Test soluciones".

--Se representarán las tres mejores soluciones en la carpeta docs (tanto gráfica como textualmente), así como el resultado completo
del algoritmo en "resultado_algoritmo.txt".

--Puede ser que en los dibujos de los circuitos, una conexión vaya de una puerta A a una puerta C, existiendo una puerta B en mitad
del camino. En estos casos, parece que la conexión va de la puerta A a la B y de la B a la C, provocando cierta confusión.
En caso de que haya alguna inconsistencia, recomendamos comprobar el archivo de texto para aclarar las conexiones. Sin embargo,
esto no suele ocurrir.

--Los resultados completos de los experimentos están en la carpeta "Resultados experimentos".

--Los algoritmos más importantes están explicados en el documento pdf. Todo lo referente a la interfaz gráfica está al final del código fuente.

    -La clase Puerta está al principio.
    
    -generar_entradas(n) genera 10 entradas de tamaño n con valores aleatorios.

    -representa_circuito(entradas,puertas,imagen,archivo,c_def=[]) representa el circuito tanto en texto como en imagen.

    -reconstruct(individuo,entradas,puertas_defectuosas,conexiones_defectuosas,sf_index) reconstruye el circuito representado por un individuo. Se usa
para construir las tres mejores soluciones.

    -simula_circuito(entrada,puertas,conexiones_defectuosas) simula el comportamiento del circuito al suministrarle una entrada.

    -algoritmo(entradas, puertas_defectuosas,conexiones_defectuosas,poblacion_input,generaciones_input) comienza el algoritmo genético. La función fenotipo
y la función evalua_individuo están explicadas en el documento pdf.

    -Clase interfaz, que tiene definidos los botones y sus posiciones. También tiene definida los métodos que se ejecutan al pulsar los botones:

        -Genera circuito genera un circuito aleatorio o el circuito por defecto
        -Diagnostica comprueba si el circuito tiene fallos y da pie al algoritmo genético
        -Test entradas y test soluciones comprueban las salidas de los diferentes circuitos según las entradas suministradas
