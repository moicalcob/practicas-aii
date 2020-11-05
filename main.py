import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import dateutil.parser
from bs4 import BeautifulSoup

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
       fecha        timestamp  NOT NULL,
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

def listar_bd():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT TITULO, PAIS, DIRECTOR FROM PELICULAS")
    imprimir_etiqueta(cursor)
    conn.close()

def salir_ventana():
    top = Tk()
    top.destroy()
    
def ventana_principal():
    top = Tk()
    
    cargar = Button(top, text = "Cargar", command = almacenar_bd)
    cargar.pack(side = LEFT)
    
    listar = Button(top, text = "Listar", command = listar_bd)
    listar.pack(side = LEFT)
    
    salir = Button(top, text = "Salir", command = salir_ventana)
    salir.pack(side = LEFT)
    
    top.mainloop()
    
if __name__ == "__main__":
    ventana_principal()

