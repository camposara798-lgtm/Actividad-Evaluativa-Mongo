import os
import certifi
from dotenv import load_dotenv
from flask import Flask, jsonify
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
aprendices = db[COLLECTION_NAME]

COL = {"locale": "es", "strength": 1}

C = {
    "ficha": "FICHA",
    "identificacion": "NUMERO_DOCUMENTO",
    "nombre": "NOMBRE",
    "apellido1": "PRIMER_APELLIDO",
    "apellido2": "SEGUNDO_APELLIDO",
    "programa": "PROGRAMA",
    "nivel": "NIVEL_DE_FORMACION",
    "estado_aprendiz": "ESTADO_APRENDIZ",
    "estado_ficha": "ESTADO_FICHA",
}


def valor_ficha(ficha):
    if str(ficha).isdigit():
        return {"$in": [int(ficha), str(ficha)]}
    return ficha

@app.route("/api/cantidadAprendices")
def cantidad_aprendices():
    cantidad = aprendices.count_documents({})
    return jsonify({"CantidadAprendices": cantidad})

@app.route("/api/cantidadAprendices/<nivel>")
def cantidad_por_nivel(nivel):
    cantidad = aprendices.count_documents({C["nivel"]: nivel}, collation=COL)
    return jsonify({"CantidadAprendices": cantidad, "Nivel de formación": nivel})

@app.route("/api/programas/<nivel>")
def programas_por_nivel(nivel):
    programas = aprendices.distinct(
        C["programa"], {C["nivel"]: nivel}, collation=COL
    )
    programas = sorted(p for p in programas if p)
    return jsonify({"nivel de formación": nivel, "programas": programas})

@app.route("/api/certificados/<programa>")
def certificados_por_programa(programa):
    filtro = {C["programa"]: programa, C["estado_aprendiz"]: "CERTIFICADO"}
    proyeccion = {
        "_id": 0,
        C["ficha"]: 1,
        C["nombre"]: 1,
        C["apellido1"]: 1,
        C["apellido2"]: 1,
    }
    lista = list(aprendices.find(filtro, proyeccion, collation=COL))
    return jsonify({"Aprendices_Certificados": lista, "Programa": programa})

@app.route("/api/porCertificar/<ficha>/<int:cantidad>")
def por_certificar(ficha, cantidad):
    filtro = {C["ficha"]: valor_ficha(ficha), C["estado_aprendiz"]: "POR CERTIFICAR"}
    proyeccion = {
        "_id": 0,
        C["ficha"]: 1,
        C["programa"]: 1,
        C["identificacion"]: 1,
        C["nombre"]: 1,
        C["apellido1"]: 1,
        C["apellido2"]: 1,
    }
    lista = list(
        aprendices.find(
            filtro,
            proyeccion,
            collation=COL,
            sort=[(C["apellido1"], -1)],
            limit=cantidad,
        )
    )
    return jsonify({"Cantidad de Aprendices por Certificar": lista})

@app.route("/api/terminadaUnificacion/<programa>")
def terminada_por_unificacion(programa):
    filtro = {
        C["programa"]: programa,
        C["estado_ficha"]: "TERMINADA POR UNIFICACION",
    }
    proyeccion = {
        "_id": 0,
        C["ficha"]: 1,
        C["identificacion"]: 1,
        C["nombre"]: 1,
        C["apellido1"]: 1,
        C["apellido2"]: 1,
    }
    lista = list(aprendices.find(filtro, proyeccion, collation=COL))
    return jsonify({"Aprendices": lista, "Programa": programa})

@app.route("/api/aprendicesPrograma/<programa>")
def aprendices_por_programa(programa):
    proyeccion = {
        "_id": 0,
        C["programa"]: 1,
        C["ficha"]: 1,
        C["nombre"]: 1,
        C["apellido1"]: 1,
        C["apellido2"]: 1,
    }
    lista = list(aprendices.find({C["programa"]: programa}, proyeccion, collation=COL))
    return jsonify({"Aprendices": lista, "Programa": programa})

@app.route("/api/cantidadCertificados/<programa>")
def cantidad_certificados_programa(programa):
    filtro = {C["programa"]: programa, C["estado_aprendiz"]: "CERTIFICADO"}
    cantidad = aprendices.count_documents(filtro, collation=COL)
    return jsonify({"Programa": programa, "Estado": "CERTIFICADO", "CantidadAprendices": cantidad})

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)