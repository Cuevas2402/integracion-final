from os import getenv
from flask import Flask, request, Response, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_mysqldb import MySQL
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["MYSQL_HOST"] = getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = getenv("MYSQL_DB")
app.config["JWT_SECRET_KEY"] = getenv("APP_SECRET")

jwt = JWTManager(app)

mysql = MySQL(app)


def getColumns(table):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(f"SHOW COLUMNS FROM `{table}`;")
    except:
        cursor.close()
        return []
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns


def getJsonResponse(columns, datos):
    data = []
    for i in range(len(datos)):
        data.append({})
        for j in range(len(datos[i])):
            data[i][columns[j]] = str(datos[i][j])
    return jsonify(data=data, status=200, mimetype="application/json")


def getXmlResponse(columns, datos):
    entries = ET.Element("entradas")
    for i in range(len(datos)):
        entrie = ET.SubElement(entries, "entrada")
        for j in range(len(datos[i])):
            element = ET.SubElement(entrie, columns[j])
            element.text = str(datos[i][j])
    arbol = ET.ElementTree(entries)
    arbol = ET.tostring(arbol.getroot(), encoding="UTF-8")
    return Response(arbol, content_type="text/xml")


@app.route("/<table>", methods=["GET"])
@cross_origin()
def getTable(table):
    columns = getColumns(table)
    if not columns:
        return "Table not found", 404
    formato = request.args.get("format", "json")
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM `{table}`;")
    datos = cursor.fetchall()
    cursor.close()
    if formato == "json":
        return getJsonResponse(columns, datos)
    elif formato == "xml":
        return getXmlResponse(columns, datos)


@app.route("/<table>/<field>/<value>", methods=["GET"])
@cross_origin()
def getTableByField(table, field, value):
    columns = getColumns(table)
    if not columns:
        return "Table not found", 404
    if field not in columns:
        return "Field not found", 404
    formato = request.args.get("format", "json")
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM `{table}` WHERE `{field}` = %s;", (value,))
    datos = cursor.fetchall()
    cursor.close()
    if formato == "json":
        return getJsonResponse(columns, datos)
    elif formato == "xml":
        return getXmlResponse(columns, datos)


@app.route("/<table>", methods=["POST"])
@cross_origin()
@jwt_required()
def insertData(table):
    columns = getColumns(table)
    if not columns:
        return "Table not found", 404
    values_string = []
    placeholders_string = []
    values = []
    for column in columns:
        if request.form.get(column, None):
            values_string.append(column)
            placeholders_string.append("%s")
            values.append(request.form.get(column))
    query = f"INSERT INTO {table} ({','.join(values_string)}) VALUES ({','.join(placeholders_string)});"
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()
        return "OK", 201
    except:
        cursor.close()
        return "Error", 500


@app.route("/<table>/<id>", methods=["PATCH"])
@cross_origin()
@jwt_required()
def updateData(table, id):
    columns = getColumns(table)
    if not columns:
        return "Table not found", 404
    sets = []
    values = []
    for column in columns:
        if request.form.get(column, None):
            sets.append(column + " = %s")
            values.append(request.form.get(column))
    values.append(id)
    query = f"UPDATE {table} SET {','.join(sets)} WHERE id = %s;"
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()
        return "OK", 200
    except:
        cursor.close()
        return "Error", 500
    return "H\n"


if __name__ == "__main__":
    app.run(debug=True)
