import random
import math
import tkinter as tk
from tkinter import messagebox

def generarGrafo(n):
    grafo = {}
    for i in range(n):
        grafo[i] = {}
    return grafo

def generarAristas(grafo, prob_arista=0.4):
    n = len(grafo)
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < prob_arista:
                peso = random.randint(1, 20)
                grafo[i][j] = peso
    return grafo

def inicializarDistancias(grafo, origen):
    dist = {}
    for nodo in grafo:
        dist[nodo] = float('inf')
    dist[origen] = 0
    return dist

def nodoNoVisitadoCercano(dist, visitados):
    mejorNodo = None
    mejorDistancia = float('inf')
    for nodo in dist:
        if nodo not in visitados:
            if dist[nodo] < mejorDistancia:
                mejorDistancia = dist[nodo]
                mejorNodo = nodo
    return mejorNodo

def dijkstra(grafo, origen):
    n = len(grafo)
    dist = inicializarDistancias(grafo, origen)
    padres = {nodo: [] for nodo in grafo}
    cuenta = {nodo: 0 for nodo in grafo}
    cuenta[origen] = 1
    visitados = set()
    pasos = []

    while len(visitados) < n:
        actual = nodoNoVisitadoCercano(dist, visitados)
        if actual is None:
            break
        visitados.add(actual)
        paso = {"nodoVisitado": actual, "distancia": dist[actual], "actualizaciones": []}
        for vecino, peso in grafo[actual].items():
            nuevaDistancia = dist[actual] + peso
            if nuevaDistancia < dist[vecino]:
                dist[vecino] = nuevaDistancia
                padres[vecino] = [actual]
                cuenta[vecino] = cuenta[actual]
                paso["actualizaciones"].append((vecino, "mejora", nuevaDistancia))
            elif nuevaDistancia == dist[vecino]:
                padres[vecino].append(actual)
                cuenta[vecino] += cuenta[actual]
                paso["actualizaciones"].append((vecino, "empate", nuevaDistancia))
        pasos.append(paso)
    return dist, padres, cuenta, pasos

def reconstruirCaminos(padres, origen, destino):
    if destino == origen:
        return [[origen]]
    if not padres[destino]:
        return []
    caminos = []
    for p in padres[destino]:
        for parcial in reconstruirCaminos(padres, origen, p):
            caminos.append(parcial + [destino])
    return caminos

ANCHO,ALTO,RADIO = 700,560,22
INFINITO = float("inf")

def ruta(camino):
    texto = ""
    for i in range(len(camino)):
        texto+=str(camino[i])
        if i < len(camino) - 1:
            texto += "->"
    return texto

def poner(entry, valor):
    entry.delete(0, "end")
    entry.insert(0, str(valor))

def botones(wi, lista, padx=4):
    for texto, comando in lista:
        tk.Button(wi, text=texto, command=comando).pack(side="left", padx=padx)

class App:
    def __init__(self):
        self.grafo = {}
        self.pasos = []
        self.caminos = [] 
        self.cantidadCaminos = {} 
        self.distanciasFinales = {}
        self.posiciones = {}
        self.origen = 0
        self.destino = 0
        self.pasosMostrados = 0
        self.caminoResaltado = -1

        self.ventanaPrincipal = tk.Tk()
        self.ventanaPrincipal.title("Dijkstra - Caminos minimos")
        Superior = tk.Frame(self.ventanaPrincipal)
        Superior.pack(padx=8, pady=6)
        casillas = []
        for texto, inicial in (("n (7-16):", ""), ("Origen:", "0"), ("Destino:", "")):
            tk.Label(Superior, text=texto).pack(side="left")
            casilla = tk.Entry(Superior, width=4)
            casilla.insert(0, inicial)
            casilla.pack(side="left", padx=(0,8))
            casillas.append(casilla)
        self.casillaN, self.casillaOrigen, self.casillaDestino = casillas

        botones(Superior, [("Grafo Aleatorio", self.aleatorio), ("Grafo manual", self.IngresoManual), ("Ejecutar Dijkstra", self.ejecutarDijkstra)])

        centro = tk.Frame(self.ventanaPrincipal)
        centro.pack(padx=8)
        self.lienzo= tk.Canvas(centro, width=ANCHO, height=ALTO, bg="white")
        self.lienzo.pack(side="left")
        tk.Label(centro, text="Resultados", font=("Arial", 11, "bold")).pack(side="top")
        self.cuadroResultados = tk.Text(centro, width=34, height=28, wrap="word", state="disabled")
        self.cuadroResultados.pack(side="left", fill="y", padx=(8,0))

        marcoInferior = tk.Frame(self.ventanaPrincipal)
        marcoInferior.pack(pady=6)
        botones(marcoInferior,[("<<Reiniciar", self.reiniciar), ("< Anterior", self.anterior), ("Siguiente >", self.siguiente), ("Ver caminos minimos", self.verCaminos)])
            
        self.Info = tk.Label(self.ventanaPrincipal, text="Genere un grafo para comenzar", justify="left", wraplength=ANCHO)
        self.Info.pack(padx=8, pady=(0,8))
        self.dibujar()

    def leerN(self):
        try:
            n = int(self.casillaN.get())
        except ValueError:
            n = 8
        if not 7 <= n <= 16:
            messagebox.showwarning("Aviso", "n fuera de rango. Se usara n = 8")
            n = 8
        poner(self.casillaN,n)
        return n

    def aleatorio(self):
        self.nuevoGrafo(generarAristas(generarGrafo(self.leerN())))

    def nuevoGrafo(self, grafo):
        CantidadNodos = len(grafo)
        self.grafo = grafo
        self.pasos = []
        self.caminos = []
        self.pasosMostrados = 0
        self.caminoResaltado = -1
        poner(self.casillaDestino, CantidadNodos - 1)
        radioCirculo = ALTO/2-60
        angulos = [2 * math.pi * i/CantidadNodos - math.pi / 2 for i in range(CantidadNodos)]
        self.posiciones = {i: (ANCHO/2 + radioCirculo * math.cos(a), ALTO/2 + radioCirculo * math.sin(a)) for i, a in enumerate(angulos)}
        self.Info.config(text="Grafo listo. Elija origen/destino y pulse 'Ejecutar Dijkstra'")
        self.dibujar()

    def IngresoManual(self):
        self.cantidadNodos = self.leerN()
        self.aristasManual = {}
        self.ventanaManual = tk.Toplevel(self.ventanaPrincipal)
        self.ventanaManual.title("Ingresar grafo manualmente")
        tk.Label(self.ventanaManual, justify="left", text=f"Los nodos van de 0 a {self.cantidadNodos-1}.\n"
                 "Cada arista va de un nodo MENOR a uno MAYOR.\n"
                 "El peso es un entero positivo").pack(padx=10, pady=6)
        filaCasilla = tk.Frame(self.ventanaManual)
        filaCasilla.pack(padx=10, pady=4)
        casillas = []
        for texto in ("Origen:", "Destino:", "Peso:"):
            tk.Label(filaCasilla, text=texto).pack(side="left")
            casilla = tk.Entry(filaCasilla, width=4)
            casilla.pack(side="left", padx=(0,8))
            casillas.append(casilla)
        self.manualOrigen, self.manualDestino, self.manualPeso = casillas
        botones(filaCasilla, [("Agregar arista", self.agregarArista)],0)
        self.manualPeso.bind("<Return>", self.teclaEnter)
        self.msg = tk.Label(self.ventanaManual, text="Escriba una arista y pulse 'Agregar arista'",
                            fg="gray", wraplength=360, justify="left")
        self.msg.pack(padx=10, pady=2)
        tk.Label(self.ventanaManual,text="Aristas agregadas:").pack()
        self.listaAristas = tk.Listbox(self.ventanaManual, width=32, height=10)
        self.listaAristas.pack(padx=10, pady=4)
        filaBotones = tk.Frame(self.ventanaManual)
        filaBotones.pack(pady=6)
        botones(filaBotones, [("Quitar ultima", self.quitarUltima), ("Borrar todas", self.borrarTodas),
                                ("Cargar ejemplo", self.cargarEjemplo)], 3)
        tk.Button(self.ventanaManual, text="Aceptar y dibujar grafo", command=self.aceptarGrafo).pack(pady=(0,10))
                
    def teclaEnter(self, evento):
        self.agregarArista()

    def aviso(self, texto, color="red"):
        self.msg.config(text=texto, fg=color)

    def actualizarLista(self, texto, color):
        self.listaAristas.delete(0, "end")
        for (origen, destino), peso in self.aristasManual.items():
            self.listaAristas.insert("end", f"{origen} -> {destino} (peso {peso})")
        self.aviso(texto, color)

    def agregarArista(self):
        try:
            origen = int(self.manualOrigen.get())
            destino = int(self.manualDestino.get())
            peso = int(self.manualPeso.get())
        except ValueError:
            return self.aviso("Escriba 3 numeros enteros: origen, destino y peso")
        if not (0 <= origen < self.cantidadNodos and 0 <= destino < self.cantidadNodos):
            return self.aviso(f"Los nodos deben estar entre 0 y {self.cantidadNodos -1}")
        if origen >= destino:
            return self.aviso("El origen debe ser Menor que el destino")
        if peso <= 0:
            return self.aviso("El peso debe ser un entero positivo")
        accion = "actualizada" if (origen, destino) in self.aristasManual else "agregada"
        self.aristasManual[(origen, destino)] = peso
        self.actualizarLista(f"Arista {origen}-> {destino} {accion} (peso {peso}). ","green")
        for casilla in (self.manualOrigen, self.manualDestino, self.manualPeso):
                        casilla.delete(0, "end")

    def quitarUltima(self):
        if self.aristasManual:
            self.aristasManual.popitem()
            self.actualizarLista("Ultima arista quitada", "gray")

    def borrarTodas(self):
        self.aristasManual = {}
        self.actualizarLista("Se borraron todas las aristas", "gray")

    def cargarEjemplo(self):
        self.aristasManual = {(0,1):2, (0,2): 2, (1,3):3, (2,3):3, (1,4):5, (3,5):2, (4,5):1, (5,6):4}
        self.actualizarLista("Ejemplo Cargado. Pruebe origen 0 y destino 6: 2 caminos minimos(distancia 11).", "green")

    def aceptarGrafo(self):
        if not self.aristasManual:
            return self.aviso("Agregue al menos una arista")
        hayOrigenCero = False
        for origen, destino in self.aristasManual:
            if origen == 0:
                hayOrigenCero = True
        if not hayOrigenCero:
            respuesta = messagebox.askyesno(
                "Nodo 0 sin conexiones",
                "Ninguna arista sale del nodo 0, el origen por defecto\n"
                "Tendra que elegir otro origen para poder ejecutar Dijkstra\n"
                "Desea continuar de todos modos?", parent=self.ventanaManual)
            if not respuesta:
                return
        grafo = generarGrafo(self.cantidadNodos)
        for (origen, destino), peso in self.aristasManual.items():
            grafo[origen][destino] = peso
        self.ventanaManual.destroy()
        self.nuevoGrafo(grafo)

    def ejecutarDijkstra(self):
        if not self.grafo:
            return messagebox.showinfo("Aviso", "Primero genere un grafo")
        cantidadNodos = len(self.grafo)
        try:
            origen = int(self.casillaOrigen.get())
            destino = int(self.casillaDestino.get())
        except ValueError:
            return messagebox.showerror("Error", "Origen y destino deben ser numeros")
        if not (0 <= origen < cantidadNodos and 0 <= destino < cantidadNodos):
            return messagebox.showerror("Error", f"Origen y destino deben estar entre 0 y {cantidadNodos - 1}")
        if not self.grafo[origen] and origen !=destino:
            return messagebox.showwarning("Origen sin conexiones",
                                          f"Ninguna arista sale del nodo {origen}\n"
                                          "Desde ahi no se puede llegar a ningun otro nodo\n"
                                          "Elija otro nodo de origen o agregue aristas que salgan de él")
        self.origen = origen
        self.destino = destino
        self.distanciasFinales, padres, self.cantidadCaminos, self.pasos = dijkstra(self.grafo, origen)
        self.caminos = reconstruirCaminos(padres, origen, destino)
        self.pasosMostrados = 0
        self.caminoResaltado = -1
        self.Info.config(text="Dijkstra ejecutado. Use 'Siguiente' para avanzar paso a paso")
        self.dibujar()

        if self.distanciasFinales[destino] == INFINITO:
            avisoExtra = ""
            if origen > destino:
                avisoExtra = ("\n Recuerde que las flechas solo van de un nodo menor a uno mayor " 
                              "asi que el origen debe ser menor que el destino")
            messagebox.showinfo("Sin camino",
                                f"No existe un camino del nodo {origen} al nodo {destino}. {avisoExtra}\n"
                                "Puede avanzar con 'Siguiente' para ver que nodos si se alcanzan.")
                            
    def siguiente(self):
        self.mover(1)

    def anterior(self):
        self.mover(-1)

    def mover(self, cambio):
        if self.pasos:
            self.caminoResaltado = -1
            self.pasosMostrados = max(0, min(len(self.pasos), self.pasosMostrados + cambio))
            self.dibujar()

    def reiniciar(self):
        self.pasosMostrados = 0
        self.caminoResaltado = -1
        self.dibujar()

    def verCaminos(self):
        if self.pasos:
            self.pasosMostrados = len(self.pasos)
            if self.caminos:
                self.caminoResaltado = (self.caminoResaltado + 1) % len(self.caminos)
            self.dibujar()
                
    def dibujar(self):
        self.lienzo.delete("all")
        if not self.grafo:
            return self.actualizarTextos(None)

        distancias = {nodo: INFINITO for nodo in self.grafo}
        visitados = []
        if self.pasos:
            distancias[self.origen] = 0
            for paso in self.pasos[:self.pasosMostrados]:
                visitados.append(paso["nodoVisitado"])
                for vecino, tipo, distancia in paso["actualizaciones"]:
                    distancias[vecino] = distancia
        pasoActual = None
        if self.pasos and self.pasosMostrados > 0:
            pasoActual = self.pasos[self.pasosMostrados -1]
        caminoMostrado = []
        if self.caminoResaltado != -1:
            caminoMostrado = self.caminos[self.caminoResaltado]
        aristasCamino = []
        for i in range(len(caminoMostrado)-1):
            aristasCamino.append((caminoMostrado[i], caminoMostrado[i+1]))
        aristasActualizadas = {}
        if pasoActual:
            for vecino, tipo, distancia in pasoActual["actualizaciones"]:
                aristasActualizadas[(pasoActual["nodoVisitado"], vecino)] = tipo

        for desde in self.grafo:
            for hasta, peso in self.grafo[desde].items():
                if self.caminoResaltado != -1:
                    if (desde, hasta) in aristasCamino:
                        color, grosor = ("red", 4) 
                    else: 
                        color, grosor = ("#999999", 1)
                elif (desde, hasta) in aristasActualizadas:
                    if aristasActualizadas[(desde, hasta)] == "mejora":
                        color, grosor = "green",3
                    else:
                        color, grosor = "orange", 3
                else:
                    color, grosor = "#999999", 1
                x1, y1 = self.posiciones[desde]
                x2, y2 = self.posiciones[hasta]
                largo = math.hypot(x2-x1, y2-y1)
                recorteX = (x2-x1) /largo * RADIO
                recorteY = (y2-y1) /largo * RADIO
                self.lienzo.create_line(x1 + recorteX, y1+recorteY, x2-recorteX, y2-recorteY,
                                        fill=color, width=grosor, arrow=tk.LAST)
                self.lienzo.create_text((x1 + x2)/2, (y1 + y2)/2, text=peso, font=("Arial", 10, "bold"))

        if pasoActual:
            nodoActual = pasoActual["nodoVisitado"] 
        else: 
            nodoActual = -1
        for nodo, (x,y) in self.posiciones.items():
            if nodo in caminoMostrado:
                colorRelleno = "#ff9999"
            elif nodo == nodoActual:
                colorRelleno = "#ffe066"
            elif nodo in visitados:
                colorRelleno = "#a8d0ff"
            else:
                colorRelleno = "#f0f0f0"
            if self.pasos and nodo in (self.origen, self.destino):
                grosorBorde = 4 
            else: 
                grosorBorde = 1
            self.lienzo.create_oval(x - RADIO, y - RADIO, x+RADIO, y+RADIO, fill=colorRelleno, outline="black", width=grosorBorde)
            self.lienzo.create_text(x,y,text=nodo, font=("Arial", 12, "bold"))
            if self.pasos:
                if distancias[nodo] == INFINITO:
                    texto = "inf" 
                else:
                    texto= f"d={distancias[nodo]}"
                self.lienzo.create_text(x,y + RADIO + 10, text=texto, font=("Arial", 9))
        self.actualizarTextos(pasoActual)

    def actualizarTextos(self, pasoActual):
        if self.pasos:
            totalPasos = len(self.pasos)
            if self.caminoResaltado != -1:
                texto=(f"Camino minimo {self.caminoResaltado + 1} de {len(self.caminos)}: "
                        f"{ruta(self.caminos[self.caminoResaltado])}\n"
                        f"Cantidad de caminos minimos: {self.cantidadCaminos[self.destino]}")
            elif self.pasosMostrados == 0:
                texto = f"Inicio: distancia de {self.origen} = 0, el resto = inf"
            else:
                textoActualizaciones = "Sin actualizaciones"
                if pasoActual["actualizaciones"]:
                    textoActualizaciones = "Actualizaciones: "
                    for vecino, tipo, distancia in pasoActual["actualizaciones"]:
                        textoActualizaciones += f"nodo {vecino} ({tipo}, d= {distancia});"
                texto = (f"Paso {self.pasosMostrados}/{totalPasos}: se visita el nodo "
                        f"{pasoActual['nodoVisitado']} (d={pasoActual['distancia']}).{textoActualizaciones}")
                if self.pasosMostrados == totalPasos:
                    if self.distanciasFinales[self.destino] == INFINITO:
                        texto += f"\nNo existe un camino entre {self.origen} y {self.destino}"
                    else:
                        texto += "\nTerminado. Pulse 'VER CAMINOS MINIMOS' para resaltarlos"
            self.Info.config(text=texto)
        if not self.pasos:
            texto = "Ejecute Dijkstra para ver aqui \n los caminos minimos."
        else:
            texto = f"RESUMEN\n Origen: {self.origen}\n Destino: {self.destino}\n"
            if self.distanciasFinales[self.destino] == INFINITO:
                texto += "\n No existe un camino entre estos nodos"
            else:
                texto += (f"Distancia minima: {self.distanciasFinales[self.destino]}\n"
                            f"Cantidad de caminos minimos: {self.cantidadCaminos[self.destino]}\n"
                            "CAMINOS MINIMOS\n")
                for i, camino in enumerate(self.caminos):
                    if i == self.caminoResaltado:
                        marca = "> " 
                    else: 
                        marca = " "
                    texto += f"{marca}{i+1}) {ruta(camino)}\n"
                texto += "\n (Use 'Ver caminos minimos' para resaltarlos en el grafo)"
        self.cuadroResultados.config(state="normal")
        self.cuadroResultados.delete("1.0", "end")
        self.cuadroResultados.insert("1.0", texto)
        self.cuadroResultados.config(state="disabled")

    def ejecutar(self):
        self.ventanaPrincipal.mainloop()
    
App().ejecutar()