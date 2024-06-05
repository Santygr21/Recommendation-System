from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Bienvenido a la API de recomendaciones de eventos!"

def importar_base_datos(ruta_archivo):
    if os.path.exists(ruta_archivo):
        return pd.read_csv(ruta_archivo, index_col='nombre')
    else:
        print(f"Archivo no encontrado: {ruta_archivo}")
        return None

def calcular_similitud_coseno(datos, usuario_referencia, k):
    usuario_referencia = datos.loc[usuario_referencia]
    datos = datos.drop(usuario_referencia.name)
    similitudes = cosine_similarity([usuario_referencia], datos)[0]
    indices_k_vecinos = np.argsort(similitudes)[-k:][::-1]
    similitudes_k_vecinos = similitudes[indices_k_vecinos]
    resultados = {}
    for i in range(len(indices_k_vecinos)):
        resultados[datos.index[indices_k_vecinos[i]]] = similitudes_k_vecinos[i]
    return resultados

def crear_protopersona(datos, vecinos):
    protopersona = datos.loc[vecinos].mean()
    return protopersona

def calcular_maximo(datos, protopersona):
    promedios = datos.mean()
    categorias_maximo = promedios[promedios > protopersona].index.tolist()
    return categorias_maximo

def calcular_minimo(datos, protopersona):
    valores_minimos = datos.min()
    categorias_minimo = valores_minimos[valores_minimos < protopersona].index.tolist()
    return categorias_minimo

def calcular_promedio(datos, protopersona):
    promedios = datos.mean()
    categorias_promedio = promedios[promedios > 3].index.tolist()
    return categorias_promedio

def calcular_desviacion_estandar(datos, protopersona):
    desviaciones = datos.std()
    categorias_desviacion = desviaciones[desviaciones < 1.1].index.tolist()
    return categorias_desviacion

def obtener_categorias(datos, protopersona, metodo):
    if metodo == 'maximo':
        categorias = calcular_maximo(datos, protopersona)
    elif metodo == 'minimo':
        categorias = calcular_minimo(datos, protopersona)
    elif metodo == 'promedio':
        categorias = calcular_promedio(datos, protopersona)
    elif metodo == 'desviacion':
        categorias = calcular_desviacion_estandar(datos, protopersona)
    else:
        raise ValueError("El método seleccionado no es válido.")
    categorias_dict = {categoria: protopersona[categoria] for categoria in categorias}
    return categorias_dict

@app.route('/user-data', methods=['POST'])
def create_data():
    data = request.get_json()
    print(data)
    usuario_referencia = data['usuario']
    k_vecinos = data['vecinos']
    metodo_aggregation = data['aggregation']
    N = data['N']

    
    
    df_usuarios = importar_base_datos('./dataBases/Base_usuarios.csv')
    if df_usuarios is None:
        return jsonify({'error': 'Base de datos de usuarios no encontrada'}), 400
    print(df_usuarios)
    usuarios = df_usuarios.index.tolist()
    print(usuarios)

    resultados_similitud = calcular_similitud_coseno(df_usuarios, usuario_referencia, k_vecinos)
    print(resultados_similitud)
    vecinos_cercanos = list(resultados_similitud.keys())

    protopersona = crear_protopersona(df_usuarios, vecinos_cercanos)
    print(protopersona)

    categorias_cumplen_requisito = obtener_categorias(df_usuarios, protopersona, metodo_aggregation)
    print(categorias_cumplen_requisito)

    df_eventos = importar_base_datos('./dataBases/Base_eventos.csv')
    if df_eventos is None:
        return jsonify({'error': 'Base de datos de eventos no encontrada'}), 400
    print(df_eventos)

    categorias = list(categorias_cumplen_requisito.keys())
    eventos_filtrados = df_eventos[df_eventos['categoria'].isin(categorias)]
    recomendaciones = eventos_filtrados.head(N)
    print(recomendaciones[['id_evento', 'categoria']])
    print(recomendaciones.head(10))  # Esto imprimirá las primeras 10 filas


    arreglo_recomendaciones = recomendaciones[['id_evento', 'categoria', 'fecha', 'descripcion']].values.tolist()
    print(type(arreglo_recomendaciones), 'Hola')
   

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    return jsonify({'resultados': arreglo_recomendaciones, 'vecinos': vecinos_cercanos})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
