import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Util  # Módulo de utilidades proporcionado por el docente en clase

def crear_grafo_desde_csv(archivo_csv):
    """
    Crea un grafo a partir de un archivo CSV.

    Args:
        archivo_csv (str): Ruta al archivo CSV que contiene las rutas y distancias.

    Returns:
        tuple: Grafo creado y DataFrame con los datos del CSV.
    """
    G = nx.Graph()
    # Leer el archivo CSV usando el delimitador correcto
    df = pd.read_csv(archivo_csv, encoding='latin-1', sep=';')
    df.columns = df.columns.str.strip()
    
    # Agregar las rutas al grafo
    for _, row in df.iterrows():
        ciudad1 = row['Ciudad1'].strip()
        ciudad2 = row['Ciudad2'].strip()
        distancia = row['Distancia']
        G.add_edge(ciudad1, ciudad2, weight=distancia)
        
    return G, df

def ruta_mas_corta(grafo, origen, destino):
    """
    Encuentra la ruta más corta entre dos nodos en un grafo.

    Args:
        grafo (networkx.Graph): Grafo en el cual buscar la ruta.
        origen (str): Nodo de origen.
        destino (str): Nodo de destino.

    Returns:
        tuple: Lista de nodos en la ruta más corta y la distancia total.
    """
    try:
        ruta = nx.shortest_path(grafo, source=origen, target=destino, weight='weight')
        distancia = nx.shortest_path_length(grafo, source=origen, target=destino, weight='weight')
        return ruta, distancia
    except nx.NetworkXNoPath:
        messagebox.showerror("Ruta No Encontrada", f"No hay ruta disponible entre {origen} y {destino}.")
        return [], None

def main():
    # Crear la ventana principal
    ventana = Util.crearVentana("Ruta Mínima Entre Ciudades", "800x800")

    # Definir función para manejar el cierre de la ventana
    def on_closing():
        ventana.destroy()
        plt.close('all')

    ventana.protocol("WM_DELETE_WINDOW", on_closing)

    # Crear el grafo desde el archivo CSV
    archivo_csv = 'rutas.csv'  # Asegúrate de que este archivo exista y esté en la misma carpeta
    G, df = crear_grafo_desde_csv(archivo_csv)

    # Lista de ciudades
    ciudades = list(G.nodes)

    # Contenedor para seleccionar ciudades
    frmSeleccion = tk.Frame(ventana)
    frmSeleccion.pack(side=tk.TOP, fill=tk.X, pady=10)
    Util.agregarEtiqueta(frmSeleccion, "Ciudad Origen:", 0, 0)
    cmbOrigen = Util.agregarLista(frmSeleccion, ciudades, 0, 1)
    Util.agregarEtiqueta(frmSeleccion, "Ciudad Destino:", 1, 0)
    cmbDestino = Util.agregarLista(frmSeleccion, ciudades, 1, 1)

    # Tabla para mostrar las rutas y distancias
    frmTabla = tk.Frame(ventana)
    frmTabla.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Treeview para mostrar los nodos del grafo
    tablaDatos = ttk.Treeview(frmTabla, columns=("Nodo 1", "Nodo 2", "Valor"), show='headings')
    tablaDatos.heading("Nodo 1", text="Nodo 1")
    tablaDatos.heading("Nodo 2", text="Nodo 2")
    tablaDatos.heading("Valor", text="Distancia (km)")
    tablaDatos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Rellenar la tabla con los datos del archivo CSV
    for _, row in df.iterrows():
        tablaDatos.insert("", "end", values=(row['Ciudad1'], row['Ciudad2'], row['Distancia']))

    # Scrollbar para la tabla de datos
    scrollbar = ttk.Scrollbar(frmTabla, orient="vertical", command=tablaDatos.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tablaDatos.configure(yscrollcommand=scrollbar.set)

    # Contenedor para los resultados de la ruta mínima
    frmResultados = tk.Frame(ventana)
    frmResultados.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=10)

    # Tabla para mostrar la ruta mínima
    tablaRuta = ttk.Treeview(frmResultados, columns=("Nombre", "Valor"), show='headings')
    tablaRuta.heading("Nombre", text="Ciudad")
    tablaRuta.heading("Valor", text="Distancia Acumulada (km)")
    tablaRuta.pack(fill=tk.BOTH, expand=True)

    # Función para mostrar la ruta
    def mostrar_ruta():
        origen = cmbOrigen.get()
        destino = cmbDestino.get()
        if origen == "" or destino == "":
            messagebox.showerror("Error", "Por favor selecciona una ciudad de origen y una de destino.")
        elif origen == destino:
            messagebox.showerror("Error", "El origen y destino no pueden ser iguales.")
        else:
            ruta, distancia = ruta_mas_corta(G, origen, destino)
            if ruta and distancia is not None:
                # Limpiar la tabla de ruta mínima
                for item in tablaRuta.get_children():
                    tablaRuta.delete(item)
                distancia_acumulada = 0
                tablaRuta.insert("", "end", values=(ruta[0], distancia_acumulada))  # Mostrar origen con distancia 0
                # Mostrar cada paso de la ruta y la distancia acumulada
                for i in range(len(ruta) - 1):
                    ciudad_actual = ruta[i]
                    ciudad_siguiente = ruta[i + 1]
                    distancia_segmento = G[ciudad_actual][ciudad_siguiente]['weight']
                    distancia_acumulada += distancia_segmento
                    tablaRuta.insert("", "end", values=(ciudad_siguiente, distancia_acumulada))
                dibujar_grafo(ruta)
                messagebox.showinfo("Ruta Mínima", f"La distancia mínima total es: {distancia_acumulada} km")

    # Función para limpiar la búsqueda
    def limpiar_busqueda():
        cmbOrigen.set('')  # Limpiar el ComboBox de origen
        cmbDestino.set('')  # Limpiar el ComboBox de destino
        # Limpiar la tabla de la ruta mínima
        for item in tablaRuta.get_children():
            tablaRuta.delete(item)
        dibujar_grafo()

    # Cargar y redimensionar las imágenes para los botones
    img_original = Image.open("./iconos/calcular.png")
    img_redimensionada = img_original.resize((30, 30), Image.LANCZOS)
    img_icono = ImageTk.PhotoImage(img_redimensionada)

    img_original_limpiar = Image.open("./iconos/limpiar.png")
    img_redimensionada_limpiar = img_original_limpiar.resize((25, 25), Image.LANCZOS)
    img_icono_limpiar = ImageTk.PhotoImage(img_redimensionada_limpiar)

    # Crear la barra con los botones
    frmBarra = tk.Frame(ventana)
    frmBarra.pack(side=tk.TOP, fill=tk.X)

    btnCalcular = tk.Button(frmBarra, image=img_icono, text="Calcular Ruta",
                            compound="left", command=mostrar_ruta)
    btnCalcular.image = img_icono  # Mantener referencia a la imagen
    btnCalcular.pack(side=tk.LEFT, padx=2, pady=2)

    btnLimpiar = tk.Button(frmBarra, image=img_icono_limpiar, text="Limpiar Búsqueda",
                           compound="left", command=limpiar_busqueda)
    btnLimpiar.image = img_icono_limpiar
    btnLimpiar.pack(side=tk.LEFT, padx=5, pady=5)

    # Contenedor para el gráfico del grafo
    frmGrafo = tk.Frame(ventana)
    frmGrafo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Crear la figura de matplotlib para mostrar el grafo
    fig, ax = plt.subplots(figsize=(6, 6))
    canvas = FigureCanvasTkAgg(fig, master=frmGrafo)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Función para dibujar el grafo
    def dibujar_grafo(ruta_resaltada=None):
        ax.clear()  # Limpiar el contenido del eje
        
        # Definir posiciones manualmente según la descripción
        pos = {
            'Medellín': (0, 4),           # Parte superior izquierda
            'Puerto Berrío': (6, 6),      # Parte superior derecha
            'Puerto Triunfo': (5, 4),     # Debajo de Puerto Berrío, diagonal derecha de Medellín
            'Manizales': (-2, 2),         # Hacia la izquierda debajo de Medellín
            'Honda': (3, 2),              # Izquierda debajo de Puerto Triunfo
            'Ibagué': (1, 0),             # Izquierda de Girardot y al sur de Manizales
            'Girardot': (4, 0),           # Debajo de Honda
            'Bogotá': (6, 0)              # Diagonal derecha, al mismo nivel de Ibagué
        }
        
        # Dibujar todos los nodos y aristas
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray',
                node_size=500, ax=ax)
        
        # Dibujar etiquetas de las distancias en las aristas
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
        
        # Resaltar la ruta si existe
        if ruta_resaltada:
            ruta_edges = list(zip(ruta_resaltada, ruta_resaltada[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=ruta_edges, edge_color='red',
                                   width=2.5, ax=ax)
        
        canvas.draw()

    # Dibujar el grafo inicial
    dibujar_grafo()

    ventana.mainloop()
    plt.close('all')  # Cerrar todas las figuras de matplotlib

if __name__ == "__main__":
    main()