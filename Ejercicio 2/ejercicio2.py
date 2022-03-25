import sqlite3
import json
import pandas as pd

with open('./users.json') as file:
    # Transform json input to python objects
    data = json.load(file)


def sql_create_table(con):
    cursorObj = con.cursor()

    # TABLA PARA USUARIOS
    cursorObj.execute(
        "CREATE TABLE IF NOT EXISTS usuariosTable (nombre, telefono, contrasena, provincia, permisos, emailTotal, emailPhishing, emailCliclados)")
    for usuarios in range(len(data['usuarios'])):
        for name in data['usuarios'][usuarios].keys():
            telefono = str(data['usuarios'][usuarios][name]['telefono'])
            contra = str(data['usuarios'][usuarios][name]['contrasena'])
            provincia = str(data['usuarios'][usuarios][name]['provincia'])
            permisos = str(data['usuarios'][usuarios][name]['permisos'])
            emailTotal = str(data['usuarios'][usuarios][name]['emails']['total'])
            emailPhishing = str(data['usuarios'][usuarios][name]['emails']['phishing'])
            emailCliclados = str(data['usuarios'][usuarios][name]['emails']['cliclados'])

            cursorObj.execute(
                'INSERT INTO usuariosTable (nombre, telefono, contrasena, provincia, permisos, emailTotal, emailPhishing, emailCliclados) VALUES (?,?,?,?,?,?,?,?)',
                (name, telefono, contra, provincia, permisos, emailTotal, emailPhishing, emailCliclados))
            con.commit()

    # TABLA PARA FECHAS
    cursorObj.execute("CREATE TABLE IF NOT EXISTS fechasTable (nombre, fechas)")
    for usuarios in range(len(data['usuarios'])):
        for name in data['usuarios'][usuarios].keys():
            for fecha in data['usuarios'][usuarios][name]['fechas']:
                cursorObj.execute('''INSERT INTO fechasTable (nombre, fechas) VALUES (?,?)''', (name, str(fecha),))
                con.commit()

    # TABLA PARA IPS
    cursorObj.execute("CREATE TABLE IF NOT EXISTS ipsTable (nombre, ips)")
    for usuarios in range(len(data['usuarios'])):
        for name in data['usuarios'][usuarios].keys():
            for ip in data['usuarios'][usuarios][name]['ips']:
                cursorObj.execute('''INSERT INTO ipsTable (nombre, ips) VALUES (?,?)''', (name, str(ip),))
                con.commit()


def sql_print(con):
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM usuariosTable')
    rowsUser = cursorObj.fetchall()
    for rowUser in rowsUser:
        print(rowUser)

    cursorObj.execute('SELECT * FROM fechasTable')
    rowsFecha = cursorObj.fetchall()
    for rowFecha in rowsFecha:
        print(rowFecha)

    cursorObj.execute('SELECT * FROM ipsTable')
    rowsIp = cursorObj.fetchall()
    for rowIp in rowsIp:
        print(rowIp)


def sql_delete_table(con):
    cursorObj = con.cursor()
    cursorObj.execute('DROP TABLE IF EXISTS usuariosTable')
    con.commit()
    cursorObj.execute('DROP TABLE IF EXISTS fechasTable')
    con.commit()
    cursorObj.execute('DROP TABLE IF EXISTS ipsTable')
    con.commit()


def dataframe():
    df = pd.read_sql_query("SELECT * FROM usuariosTable GROUP BY nombre", con)
    df["fechas"] = pd.read_sql_query("SELECT COUNT(fechas) FROM fechasTable GROUP BY nombre", con)
    df["ips"] = pd.read_sql_query("SELECT COUNT(ips) FROM ipsTable GROUP BY nombre", con)
    return df


con = sqlite3.connect('ejercicio2.db')
sql_create_table(con)
# sql_print(con)

df = dataframe()

# print(df)

# EJERCICIO 2

# Número de muestras (valores distintos de missing)
missing = 0
for index, row in df.iterrows():
    if row["telefono"] == "None":
        missing += 1
    if row["provincia"] == "None":
        missing += 1
    if row["ips"] == "None":
        missing += 1

missing += 1
not_missing = (len(df) * len(df.columns)) - missing
print("Número de muestras: ", not_missing)

# Media y desviación estándar del total de fechas que se ha iniciado sesión
# Todos los usuarios tienen al menos una fecha
mediaFechas = df["fechas"].mean()
print("La media del total de fechas que han iniciado sesion: ", mediaFechas)
desviacionFechas = df["fechas"].std()
print("La desviación estandar del total de fechas que han iniciado sesion: ", desviacionFechas)

# Media y desviación estándar del total de IPs que se han detectado
# Hay un usuario que no tiene niguna dirección Ip - restar este usuario
df["ips"] = df["ips"].fillna(0)
mediaIPs = df["ips"].mean()
print("La media del total de IPs: ", mediaIPs)
desviacionIPs = df["ips"].std()
print("La desviacion estandar del total de IPs: ", desviacionIPs)

# Media y desviación estándar del número de emails recibidos : columna emailsTotal
# Entendemos que los emails de Phishing y los emails Cliclados se encuentran contenidos en los emails totales
df["emailTotal"] = df["emailTotal"].astype(int)
mediaEmail = df["emailTotal"].mean()
print("La media del numero de email recibidos: ", mediaEmail)
desviacionEmail = df["emailTotal"].std()
print("La desviacion estandar del numero de email recibidos: ", desviacionEmail)

# Valor mínimo y máximo del total de fechas que se ha iniciado sesión
minFechas = df["fechas"].min()
print("El valor minimo de fechas que se ha iniciado sesion: ", minFechas)
maxFechas = df["fechas"].max()
print("El valor maximo de fechas que se ha iniciado sesion: ", maxFechas)

# Valor mínimo y máximo del número de emails recibidos
minEmails = df["emailTotal"].min()
print("El valor minimo de emails recibidos: ", minEmails)
maxEmails = df["emailTotal"].max()
print("El valor maximo de emails recibidos: ", maxEmails)

# print(df)
sql_delete_table(con)
con.close()
