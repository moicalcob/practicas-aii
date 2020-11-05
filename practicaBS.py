import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import dateutil.parser
from bs4 import BeautifulSoup
import datetime

def extraer_juegos():
    f = urllib.request.urlopen("https://zacatrus.es/juegos-de-mesa.html")
    s = BeautifulSoup(f,"lxml")
    resultados = []
    pagina = s.find("ol", class_= ["product-items"])

    cartel_juegos = pagina.find_all("li")

    for cartel_juego in cartel_juegos:
        enlace = cartel_juego.find("a")["href"]
        juego_resultado = urllib.request.urlopen(enlace)
        s = BeautifulSoup(juego_resultado, "lxml")
        resultado = {}
        resultado["titulo"] = s.find("span", itemprop='name').string.strip()
        votos = 0 if s.find("span", itemprop='ratingValue') is None else s.find("span", itemprop='ratingValue').string.strip()
        resultado["votos"] = votos
        resultado["precio"] = s.find("span", class_= ["price"]).string.strip().replace('\xa0', ' ')
        resultado["complejidad"] = '' if s.find("td",attrs={"data-th": "Complejidad"}) is None else s.find("td",attrs={"data-th": "Complejidad"}).string.strip()
        tematicas = '' if s.find("td",attrs={"data-th": "Temática"}) is None else s.find("td",attrs={"data-th": "Temática"}).string.strip()
        tematicas = tematicas.replace(',', '')
        tematicas = tematicas.replace(' ', ',')
        resultado["tematicas"] = tematicas
        resultados.append(resultado)
    return resultados

def almacenar_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS juegos")
    conn.execute('''CREATE TABLE juegos
       (titulo       TEXT NOT NULL,
       votos  INTEGER    NOT NULL,
       precio      TEXT    NOT NULL,
       tematicas        TEXT  NOT NULL,
       complejidad        TEXT NOT NULL);''')
    juegos = extraer_juegos()
    for l in juegos:
        conn.execute("""INSERT INTO juegos VALUES (?,?,?,?,?)""",(l["titulo"],l["votos"],l["precio"],l["tematicas"],l["complejidad"]))
        conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM juegos")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def imprimir_etiqueta_juegos(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,"Titulo: " + row[0])
        lb.insert(END,"Votos: " + str(row[1]))
        lb.insert(END,"Precio: " + row[2])
        lb.insert(END,"Tematicas: " + row[3])
        lb.insert(END,"Complejidad: " + row[4])
        lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH)
    sc.config(command = lb.yview)
    
def imprimir_etiqueta_juegos_busqueda(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,"Titulo: " + row[0])
        lb.insert(END,"Tematicas: " + row[1])
        lb.insert(END,"Complejidad: " + row[2])
        lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH)
    sc.config(command = lb.yview)

def listar_juegos_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str 
    cursor = conn.execute("SELECT titulo, votos, precio, tematicas, complejidad FROM juegos")
    imprimir_etiqueta_juegos(cursor)
    conn.close()

def listar_mejores_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str 
    cursor = conn.execute("SELECT titulo, votos, precio, tematicas, complejidad FROM JUEGOS WHERE votos >= 81")
    imprimir_etiqueta_juegos(cursor)
    conn.close()

def buscar_tematicas():

    def listar_busqueda(event):
        conn = sqlite3.connect('juegos.db')
        conn.text_factory = str
        s = sp.get()
        cursor = conn.execute("""SELECT titulo, tematicas, complejidad FROM juegos WHERE instr(tematicas, ?)""",(s,))
        imprimir_etiqueta_juegos_busqueda(cursor)
        conn.close()

    def listar_tematicas():
        conn = sqlite3.connect('juegos.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT tematicas FROM juegos""")
        tematicas = []
        for row in cursor:
            tematicas_split = row[0].split(",")
            for tematica in tematicas_split:
                tematicas.append(tematica)
        return tematicas
        conn.close()
        
    tematicas = listar_tematicas()
    v = Toplevel()
    lb = Label(v, text="Introduzca la tematica: ")
    lb.pack(side = LEFT)
    sp = Spinbox(v, values=tematicas)
    sp.bind("<Return>", listar_busqueda)
    sp.pack(side = LEFT)

def buscar_juego_complejidad():
    def listar_busqueda(event):
        conn = sqlite3.connect('juegos.db')
        conn.text_factory = str   
        cursor = conn.execute("SELECT TITULO, TEMATICAS, COMPLEJIDAD FROM JUEGOS WHERE COMPLEJIDAD LIKE '%" + str(entry.get())+"%'")
        imprimir_etiqueta_juegos_busqueda(cursor)
        conn.close()

    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT complejidad FROM JUEGOS")
    complejidad=set()
    for i in cursor:
        complejidad_juego = i[0].split(",")
        for c in complejidad_juego:
            complejidad.add(c.strip())
            
    v = Toplevel()
    lb = Label(v, text="Introduzca la complejidad: ")
    lb.pack(side = LEFT)
    entry = Spinbox(v, values=list(complejidad))
    entry.bind("<Return>", listar_busqueda)
    entry.pack()
    conn.close()

def ventana_principal():
    top = Tk()

    menu1 = Menu(top)
    top.config(menu = menu1)

    datos = Menu(menu1, tearoff=0)
    listar = Menu(menu1, tearoff=0)
    buscar = Menu(menu1, tearoff=0)

    menu1.add_cascade(label="Datos", menu=datos)
    menu1.add_cascade(label="Listar", menu=listar)
    menu1.add_cascade(label="Buscar", menu=buscar)

    datos.add_command(label="Cargar", command=almacenar_bd)
    datos.add_command(label="Salir", command=top.destroy)

    listar.add_command(label="Juegos", command=listar_juegos_bd)
    listar.add_command(label="Mejores Juegos", command=listar_mejores_bd)

    buscar.add_command(label="Juegos por tematica", command=buscar_tematicas)
    buscar.add_command(label="Juegos por complejidad", command=buscar_juego_complejidad)

    top.mainloop()

if __name__ == "__main__":

    ventana_principal()