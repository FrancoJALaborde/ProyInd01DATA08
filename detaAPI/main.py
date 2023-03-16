#Importo librerias 
from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional

#Creo una instancia de FastAPI
app = FastAPI()

#---- PRESENTACIÓN--------

@app.get("/")
def bienevenida():
    return "Bievenidos a mi PI_ML_OPS, aqui podra encontrar diferentes peliculas y series de distintas plataformas  gracias por pasar :D"

@app.get("/menu")
def menu():
    return "Las funciones que encontrara son las siguientes: (1) get_max_duration (2) get_score_count (3) get_count_platform (4) get_actor"

@app.get("/contacto")
def contacto():
    return "GitHub: FrancoJALaborde , Mail: jose_ariel_franco@hotmail.com"


#---------- Queries-----
#Primer consigna: Película con mayor duración con filtros opcionales de AÑO, PLATAFORMA Y TIPO DE DURACIÓN.
@app.get("/get_max_duratio/{year}/{platform}/{duration_type}")
def get_max_duration(year: Optional[int] = None, platform: Optional[str] = None, duration_type: Optional[str] = 'min'):
    #Lectura de la base de datos:
    df = pd.read_csv('plataformas_completo.csv')

    # Verificar que la plataforma sea una de las opciones válidas
    if platform is not None and platform.lower() not in ['disney', 'amazon', 'hulu', 'netflix']:
        raise ValueError("La plataforma debe ser una de las opciones válidas: Disney, Amazon, Hulu o Netflix.")
   
    if duration_type is not None and duration_type not in ['min', 'season']:
        return('Los valores validos son: min, season')
    
    canal= df[df['ID'].str.contains(platform[0], case= False)]

    #Aplico filtro para el año , el tipo, y e tipo de duracion
    filtro= canal[(canal.release_year == year) & (canal.type== 'movie') & (canal.duration_type == duration_type)]

    #Accedo a las columnas y tomo el indice mayor de cada columna
    duracion= filtro[['title','duration_int', 'duration_type']].loc[filtro.duration_int.idxmax()] 

    #El resultado lo paso a un formato de diccionario
    pelicula= duracion.T.to_dict() 

    return pelicula

#Segunda consigna: Cantidad de películas por plataforma con un puntaje mayor a XX en determinado año
@app.get("/get_score_count/{platform}/{scored}/{release_year}")
def get_score_count(platform : str, scored : float, release_year: int):
    #Lectura de la base de datos:
    df = pd.read_csv('plataformas_completo.csv')

    # Verificar que la plataforma sea una de las opciones válidas
    if platform is not None and platform.lower() not in ['disney', 'amazon', 'hulu', 'netflix']:
        raise ValueError("La plataforma debe ser una de las opciones válidas: Disney, Amazon, Hulu o Netflix.")
    
   # Filtrar las películas para la plataforma, año y puntaje especificados
    filtro = df[(df.platform == platform) & (df.score > scored) & (df.release_year == release_year) & (df.type == 'movie')]

   # Agrupar por plataforma y contar el número de filas resultantes
    count = filtro.groupby('platform').size()
    
    return count.to_dict()


#Tercer consigna: Cantidad de películas por plataforma con filtro de PLATAFORMA.
@app.get("/get_count_platform/{platform}")
def get_count_platform(platform: str):
    #Lectura de la base de datos:
    df = pd.read_csv('plataformas_completo.csv')

    # Verificar que la plataforma sea una de las opciones válidas
    if platform is not None and platform.lower() not in ['disney', 'amazon', 'hulu', 'netflix']:
        raise ValueError("La plataforma debe ser una de las opciones válidas: Disney, Amazon, Hulu o Netflix.")
    
    #Filtrar las películas para la plataforma
    filtro= df[df['ID'].str.contains(platform[0], case= False)]

    #luego hago un conteo del tamaño del filtro que hice
    conteo = len(filtro)

    return conteo


#Cuarta consigna: Actor que más se repite según plataforma y año.
@app.get("/get_actor/{platform}/{year}")
def get_actor(platform : str, year: int):
    #Lectura de la base de datos:
    df = pd.read_csv('plataformas_completo.csv')

    # Verificar que la plataforma sea una de las opciones válidas
    if platform is not None and platform.lower() not in ['disney', 'amazon', 'hulu', 'netflix']:
        raise ValueError("La plataforma debe ser una de las opciones válidas: Disney, Amazon, Hulu o Netflix.")
    
    filtro= df[(df.release_year == year) & (df.platform == platform)]
    # Poner el cast en un array para poder hacer el recorrido

    cast= filtro.assign(actor=df.cast.str.split(',')).explode('cast')
     # Contar la cantidad de apariciones de cada actor
    actor_counts = cast['cast'].value_counts()

    # Obtener el actor que más se repite y su cantidad de apariciones
    max_actor = actor_counts.index[0]
    max_count = int(actor_counts.iloc[0])

    # Creando un diccionario para poder ver los resultados 
    actor_repetido = {'actor': max_actor, 'count': max_count}
    
    return JSONResponse(content=jsonable_encoder(actor_repetido))
    