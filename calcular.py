import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use('seaborn-dark')
# Función mean: calcula la media 
# in df: DataFrame de elementos de donde se obtiene la media
# in col: la columna a considerar para obtener el promedio
# out: flotante que representa el promedio de los elementos en la columna de la lista
def mean(df, col):
    return np.sum(df[col]) / df.shape[0]

# Función median: obtiene la mediana de una lista ordenada
# in df: DataFrame de elementos ordenados de donde se obtiene la mediana
# out: fila(s) en representación del valor medio
def median(df):
    mid = int(df.shape[0]/2)
    return df.iloc[[mid]] if df.shape[0] % 2 == 1 else df.iloc[[mid - 1, mid]]

# Función mode: obtiene el elemento que más se repite
# in df: DataFrame de elementos de donde se obtiene la moda
# in col: la columna a considerar para obtener la moda
# out: el valor con mayor cantidad de repeticiones
def mode(df, col):
    keys, values = np.unique(df[col], return_counts=True)
    return keys[np.where(values == [np.max(values)])][0]

# Función weighted_median: calcula la mediana ponderada de un listado de elementos
# in df: DataFrame de elementos a utilizar, ordenados
# in wts: columna con los pesos asociados a la columna de interés
# out: fila(s) en representación del valor medido bajo los pesos indicados
def weighted_median(df, wts):
    idx = 0
    acc = 0
    even = False
    total = np.sum(df[wts])
    df.reset_index()
    for index, row in df.iterrows():
        idx = index
        acc += row[wts]
        if acc >= total / 2:
            even = True if acc == total / 2 else False
            break
    return df.iloc[[idx, idx+1]] if even else df.iloc[[idx]]

# Función weighted_mean: calcula la media ponderada de un listado de elementos
# in df: DataFrame de elementos a utilizar
# in col: la columna a considerar para obtener el promedio
# in wts: columna con los pesos asociados a la columna de interés
# out: flotante que representa el promedio de los elementos bajo los pesos establecidos
def weighted_mean(df, col, wts):
    return np.sum(df[col] * df[wts]) / np.sum(df[wts])

# Se obtienen las incidencias y llamadas
df_incidencias = pd.read_csv ('incidencias.csv', sep=';')
df_llamadas = pd.read_csv ('llamadas.csv', sep=';')

# Se agrega una columna para diferenciar los tipos de reporte
df_incidencias['tipo'] = pd.Series([2 for _ in range(len(df_incidencias.index))])
df_llamadas['tipo'].replace({ 't': 1, 'f': 0}, inplace=True)

# Se modifican los datos vacíos por un texto alusivo o cero si son numéricos
for (columnName, columnData) in df_incidencias.iteritems():
	df_incidencias[columnName].replace(np.nan, 'Sin datos' if columnData.dtypes == 'object' else 0, inplace=True)
	if columnData.dtypes != 'object':
		df_incidencias[columnName] = df_incidencias[columnName].astype('int32', copy=False)
for (columnName, columnData) in df_llamadas.iteritems():
	df_llamadas[columnName].replace(np.nan, 'Sin datos' if columnData.dtypes == 'object' else 0, inplace=True)
	if columnData.dtypes != 'object':
		df_llamadas[columnName] = df_llamadas[columnName].astype('int32', copy=False)

# Se elimina la columna de id, en vista de que no es necesaria
df_incidencias.drop('id', axis=1, inplace=True)
df_llamadas.drop('id', axis=1, inplace=True)

# Se concatenan los DataFrames en uno solo
df_final = pd.concat([df_incidencias, df_llamadas], ignore_index=True)

# Se ordena el DataFrame por fecha, desde lo más viejo hasta lo más reciente
df_final['fecha'] = pd.to_datetime(df_final['fecha'], format='%Y-%m-%d %H:%M:%S')
df_final.sort_values(by=['fecha'], ascending=True, inplace=True)

pesos = [5, 6, 1, 2, 5, 3, 1, 3]

# Se obtienen las mediciones solicitadas
cuenta_final = pd.DataFrame({ 
    'cantidad': df_final['ambito'].value_counts().sort_index(),
    'peso': pesos
})
cuenta_final.reset_index(inplace=True)
print('Mediana: \n', median(df_final))
print('Mediana ponderada (ordenado de mayor a menor cantidad): \n', weighted_median(cuenta_final, 'peso'))
print('Moda (Ámbito): ', mode(df_final,'ambito'))
print('Moda (Clasificación): ', mode(df_final,'clasificacion'))
print('Moda (Estado): ', mode(df_final,'estado'))
print('Media (Ámbito)', mean(cuenta_final, 'cantidad'))
print('Media ponderada: ', weighted_mean(cuenta_final, 'cantidad', 'peso'))

# Como hay muchas filas sin datos (7603), se descartan del DataFrame para comparar con los totales
df_ambitos = df_final[df_final.ambito != 'Sin datos']
cuenta_ambitos = pd.DataFrame({ 
    'cantidad': df_ambitos['ambito'].value_counts().sort_index(),
    'peso': [x for i,x in enumerate(pesos) if i!=6]
})
cuenta_ambitos.reset_index(inplace=True)
print('Mediana (descartando ambitos sin datos): \n', median(df_ambitos))
print('Mediana ponderada (descartando ambitos sin datos, ordenado de mayor a menor cantidad): \n', weighted_median(cuenta_ambitos, 'peso'))
print('Moda (Ámbito, descartando ambitos sin datos): ', mode(df_ambitos,'ambito'))
print('Moda (Clasificación, descartando ambitos sin datos): ', mode(df_ambitos,'clasificacion'))
print('Moda (Estado, descartando ambitos sin datos): ', mode(df_ambitos,'estado'))
print('Media (Ámbito, descartando ambitos sin datos)', mean(cuenta_ambitos, 'cantidad'))
print('Media ponderada (descartando ambitos sin datos): ', weighted_mean(cuenta_ambitos, 'cantidad', 'peso'))

# Gráficas
# 1. Pie chart que compara incidencias, llamadas e intentos de llamada
plt.figure(0)
totales = df_final['tipo'].value_counts().sort_index()
plt.pie(totales, labels= ['Intentos', 'Llamadas', 'Incidencias'], autopct='%1.2f%%')
plt.title("Distribución de reportes")
#plt.show(block=False)
plt.savefig('plots/pie_reportes.png')

# 2. Stacked bar chart entre los tipos(incidencias/llamadas/intentos) y los códigos de ámbito
plt.figure(1)
ambitos_tipos = df_final.groupby('codigo')['tipo'].value_counts().sort_index()
lista_codigos = np.unique(ambitos_tipos.index.get_level_values('codigo'))
lista_tipos = np.unique(ambitos_tipos.index.get_level_values('tipo'))
lista_par_codigos_tipos = [(a, b) for a in lista_codigos for b in lista_tipos]
ambitos_tipos = ambitos_tipos.reindex(lista_par_codigos_tipos, fill_value=0)
ancho = 0.5
plt.bar(lista_codigos, ambitos_tipos[:, 2], ancho, label='Incidencias')
plt.bar(lista_codigos, ambitos_tipos[:, 1], ancho, label='Llamadas', bottom=ambitos_tipos[:, 2])
plt.bar(lista_codigos, ambitos_tipos[:, 0], ancho, label='Intentos', bottom=ambitos_tipos[:, 1])
plt.title("Distribución de ámbitos por reporte")
plt.ylabel('Total de reportes')
plt.xlabel('Códigos por ámbito')
plt.legend()
#plt.show(block=False)
plt.savefig('plots/bar_ambitos.png')

# 3. Radar chart entre estados y código de ámbito
plt.figure(2, figsize=(10, 10))
plt.subplot(polar=True)
ambitos_estados = df_final.groupby('estado')['codigo'].value_counts().sort_index()
lista_estados = np.unique(ambitos_estados.index.get_level_values('estado'))
lista_estados = [*lista_estados, lista_estados[0]]
lista_par_codigos_estados = [(a, b) for a in lista_estados for b in [x for i,x in enumerate(lista_codigos) if i!=6]]
ambitos_estados = ambitos_estados.reindex(lista_par_codigos_estados, fill_value=0)
theta = np.linspace(start=0, stop=2*np.pi, num=len(lista_estados))
for i in [x for i,x in enumerate(lista_codigos) if i!=6]:
	plt.plot(theta, ambitos_estados[:, i], label=i, linestyle='dashed')
plt.title('Distribución de ámbitos por estado')
lines, labels = plt.thetagrids(np.degrees(theta), labels=lista_estados)
plt.legend(bbox_to_anchor=(1.12, 1.05), title="Ámbitos")
#plt.show(block=False)
plt.savefig('plots/radar_estados.png')
