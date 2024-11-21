from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
import json
from datetime import datetime

from flask_cors import CORS
from OpenSSL import SSL
import os
import pandas as pd
from datetime import datetime

# context = SSL.Context(SSL.P)
# context.use_privatekey_file('key.pem')
# context.use_certificate_file('cert.pem')

CANT_HITOS_USER = 10

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)  # Esto permite CORS para todas las rutas

# Datos iniciales
data_initial = [
    {'user':0,"anio": 1970,'hito':0 ,"mes": 5, "dia":1, "name": "Centro Nacional Patagónico (CENPAT) comenzó a funcionar"},    
    {'user':0,"anio":1972, "hito":1, "mes":8, "dia":22, 'name': 'Masacre de Trelew'},
    {'user':0,"anio":1974, "hito":2,  "mes": 11, "dia":1, "name": "Inicio de actividades de ALUAR"},
    {'user':0,"anio":1980, "hito":3,  "mes":2, 'dia':25, "name": "Fundación UNPSJB"},
    {'user':0,"anio":1982, "hito":4,  "mes": 11, "dia":1, "name": "Guerra de Malvinas"},
    {'user':0,"anio":1984, "hito":5,  'mes': 9, "dia":10, "name": "Madrynazo"},
    {'user':0,"anio":1984, "hito":6,  'mes':12, "dia":14, "name": "Se creó la Sede Puerto Madryn de la UNPSJB"},
    {'user':0,"anio":1994, "hito":7,  "mes": 11, "dia":1, "name": "Primer CENPAT abierto"},
    {'user':0,"anio":2001, "hito":8,  "mes": 11, "dia":1, "name": "Crisis"},
    {'user':0,"anio":2020, "hito":9, "mes":3,  'dia':1, "name": "Pandemia de COVID-19"},
    
    # {'user':0,"anio": 1991,'hito':1 ,"mes": 5, "dia":1, "name": "Inauguración edificio actual UNPSBJ sede Madryn"},
    {'user':0,"anio": 2024,'hito':10, "mes": 11, "dia":1, "name": "Hoy - Festival"}
]

# Crear nombre de archivo con horario
ahora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nombre_archivo = f"hitos_{ahora}.xlsx"
ruta_archivo = "./"+nombre_archivo

def guardar_hito(diccionario):
    global ruta_archivo
    nueva_fila = pd.DataFrame([diccionario])
    if os.path.exists(ruta_archivo):
        # Cargar archivo existente
        df = pd.read_excel(ruta_archivo)
        # Agregar nueva fila
        df = pd.concat([df, nueva_fila], ignore_index=True)
    else:
        # Crear nuevo archivo con la primera fila
        df = nueva_fila
    
    # Guardar DataFrame en el archivo Excel
    df.to_excel(ruta_archivo, index=False)
    

data = []
hitos_n = 12

# Buscar archivos Excel en la carpeta que coincidan con el nombre base
archivos_existentes = [
    archivo for archivo in os.listdir(".")
    if archivo.startswith('hitos_') and archivo.endswith(".xlsx")
]

if archivos_existentes:
    print('LEVANTË UN ARCHIVO')
    # Obtener el archivo más reciente basado en el nombre
    archivos_existentes.sort()  # Asegura el orden cronológico por nombre
    ruta_archivo = os.path.join('./', archivos_existentes[-1])

    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo)

    df['hito'] = range(0, df.shape[0])
    # Convertir filas a una lista de diccionarios
    data = df.to_dict(orient="records")[-CANT_HITOS_USER:]
    hitos_n = data[-1]['hito'] + 1

cant_hitos= len(data)

@app.route('/', methods=['GET'])
def get_inicio():
    # Devuelve los datos iniciales como JSON
    return render_template('index.html')

@app.route('/hito', methods=['GET'])
def get_hito():
    # Devuelve los datos iniciales como JSON
    return render_template('agregar_hito.html')


@app.route('/data', methods=['GET'])
def get_data():
    # Devuelve los datos iniciales como JSON
    return jsonify(data_initial+data)

@socketio.on('connect')
def handle_connect():
    # Envía los datos iniciales al cliente cuando se conecta
    emit('update_data', data_initial+data)

@socketio.on('new_data')
def handle_new_data(new_data):
    # Agrega nuevos datos y emite el evento a todos los clientes conectados
    global hitos_n, cant_hitos
    new_data['hito'] = hitos_n
    new_data['user'] = 1
    hitos_n+=1
    cant_hitos+=1
    data.append(new_data)
    guardar_hito(new_data)
    if cant_hitos>CANT_HITOS_USER:
        data.remove(data[0])
    emit('update_data', data_initial+data, broadcast=True)
    # data_sorted = sorted(data, key=lambda x: x["anio"])

    # emit('update_data', data_sorted, broadcast=True)

if __name__ == '__main__':
    socketio.run(app,
                 #host='0.0.0.0',
                 port='5000',
                 debug=True)
