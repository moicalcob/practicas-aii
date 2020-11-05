import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import dateutil.parser
from bs4 import BeautifulSoup
import datetime

def extraer_peliculas():
    f = urllib.request.urlopen("https://www.elseptimoarte.net/estrenos")
    s = BeautifulSoup(f,"lxml")
    resultados = []
    
    pagina = s.find("ul", class_= ["elements"])
    cartel_peliculas = pagina.find_all("li")
    for cartel_pelicula in cartel_peliculas:
        enlace = cartel_pelicula.find("a")["href"]
        url_base = "https://www.elseptimoarte.net"
        url_nueva = url_base + enlace
        pelicula_resultado = urllib.request.urlopen(url_nueva)
        s = BeautifulSoup(pelicula_resultado, "lxml")
        resultado = {}
        resultado["titulo"] = s.find("h2", id="main_titulo").string.strip()
        datos = s.find_all("dd")
        resultado["titulo_original"] = datos[1].string.strip()
        resultado["pais"] = datos[2].find("a").string.strip()
        resultado["fecha"] = datos[3].string.strip()
        resultado["director"] = s.find("span", itemprop='name').string.strip()
        resultado["genero"] = []
        categorias = s.find("p", class_=["categorias"])
        generos = categorias.find_all("a")
        for genero in generos:
            resultado["genero"].append(genero.string.strip())
        resultados.append(resultado)
    
    return resultados
 
def almacenar_bd():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS peliculas") 
    conn.execute('''CREATE TABLE peliculas
       (titulo       TEXT NOT NULL,
       titulo_original  TEXT    NOT NULL,
       pais      TEXT    NOT NULL,
       fecha        DATE  NOT NULL,
       director        TEXT NOT NULL,
       genero           TEXT);''')
    peliculas = extraer_peliculas()
    for l in peliculas:
        conn.execute("""INSERT INTO peliculas VALUES (?,?,?,?,?,?)""",(l["titulo"],l["titulo_original"],l["pais"],l["fecha"],l["director"],",".join(l["genero"])))
        conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM peliculas")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def imprimir_etiqueta(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,row[1])
        lb.insert(END,row[2])
        lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH)
    sc.config(command = lb.yview)
    
def imprimir_etiqueta_con_fecha(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,row[3])
        lb.insert(END,'')
    lb.pack(side = LEFT, fill = BOTH)
    sc.config(command = lb.yview)

def listar_bd():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT titulo, pais, director FROM PELICULAS")
    imprimir_etiqueta(cursor)
    conn.close()
    
def buscar_pelicula():
    def listar_busqueda(event):
        conn = sqlite3.connect('peliculas.db')
        conn.text_factory = str
        s =  en.get()        
        cursor = conn.execute("""SELECT * FROM PELICULAS WHERE instr("TITULO", ?)""",(s,)) 
        imprimir_etiqueta(cursor)
        conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca el título: ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side = LEFT)

def buscar_fecha():
    def listar_busqueda(event):
        conn = sqlite3.connect('peliculas.db')
        conn.text_factory = str
        s =  en.get()
        date = datetime.datetime.strptime(s,'%d-%m-%Y')
        cursor = conn.execute("""SELECT * FROM PELICULAS WHERE FECHA > ?""",(date,)) 
        imprimir_etiqueta_con_fecha(cursor)
        conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca la fecha ('dd-mm-aaaa'): ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side = LEFT)
    
def ventana_principal():
    top = Tk()
    
    cargar = Button(top, text = "Cargar", command = almacenar_bd)
    cargar.pack(side = LEFT)
    
    listar = Button(top, text = "Listar", command = listar_bd)
    listar.pack(side = LEFT)
    
    salir = Button(top, text = "Salir", command = top.destroy)
    salir.pack(side = LEFT)
    
    Buscar = Button(top, text="Buscar película", command = buscar_pelicula)
    Buscar.pack(side = TOP)
    
    Buscar = Button(top, text="Buscar por fecha", command = buscar_fecha)
    Buscar.pack(side = TOP)
    
    top.mainloop()
    
if __name__ == "__main__":
    ventana_principal()
