Read , lines 1 to 220
Completed with input: {
  "path": "/home/codespace/.vscode-remote/data/agentSessionData/68752de8-14bc-4949-a750-c65eb9aec880/attachments/37a330ba-3eaf-4744-8832-fc12ba39e19a/file_Semana_5SINC.ipynb",
  "view_range": [
    1,
    220
  ]
}

Read , lines 1 to 220
Completed with input: {
  "path": "/home/codespace/.vscode-remote/data/agentSessionData/68752de8-14bc-4949-a750-c65eb9aec880/attachments/bb635f0c-c4fd-4141-ad57-831485b19995/file_Semana_5SINC.ipynb output.json",
  "view_range": [
    1,
    220
  ]
}

Ran terminal command: python - <<'PY'
import json, pathlib
p = pathlib.Path('/workspaces/PI3_Analitica_EA3/src/sincronicas/Semana_5SINC.ipynb')
nb = json.loads(p.read_text())
print('cells', len(nb.get('cells', [])))
for i,cell in enumerate(nb.get('cells', [])):
    src=''.join(cell.get('source',[]))
    print(f'--- CELL {i} type={cell.get("cell_type")} ---')
    # print first 200 chars
    print(src[:500].replace('\n','\\n'))
    print()
PY

# Análisis de churn en telecom — Semana 5

> Trabajo realizado por: Jhonny Arley Tobon Acevedo y Javier Martinez Ceballos.

## Resumen ejecutivo

Este notebook tiene como objetivo ayudar a la gerencia comercial a entender por qué algunos clientes abandonan el servicio (churn) y cómo este comportamiento varía según características como el tipo de contrato, la antigüedad del cliente y sus servicios asociados. La idea principal es pasar de una toma de decisiones reactiva e intuitiva a un diagnóstico basado en evidencia empírica.

La problemática que se plantea es la siguiente: la empresa observa niveles continuos de cancelación de contratos al cierre de cada mes, pero las decisiones se toman sin un análisis cuantitativo claro sobre los patrones de uso, los montos facturados y los servicios asociados a los clientes que se van.

---

## Objetivo del notebook

El notebook busca responder la pregunta de negocio:

- ¿Cómo varía la tasa de abandono (churn rate) según el tipo de contrato?
- ¿Cuál es la antigüedad promedio crítica en la que ocurre la mayor deserción?
- ¿Qué segmentos de clientes tienen mayor riesgo de salir?

Para resolverlo, el análisis combina:

- carga de datos desde Hugging Face,
- revisión del dataframe,
- transformaciones de variables,
- análisis de abandono por tipo de contrato,
- generación de reportes descriptivos automáticos.

---

## 1. Preparación del entorno

La primera parte del notebook prepara el entorno para poder importar clases reutilizables del proyecto. En lugar de depender de que el proyecto esté instalado como paquete, se recorre hacia arriba desde el directorio actual hasta encontrar la carpeta `src` y se agrega al `sys.path`.

Esto permite importar una clase llamada `HFDatasetLoader`, que es la encargada de cargar el dataset desde Hugging Face.

Conceptualmente, esta celda hace lo siguiente:

- identifica la ruta raíz del proyecto,
- busca la carpeta con los módulos del proyecto,
- añade `src` a la ruta de Python,
- importa la clase para cargar datasets.

Esto es útil porque el notebook puede ejecutarse desde distintos directorios sin romper importaciones.

---

## 2. Carga del dataset

Luego se usa `HFDatasetLoader` con estos parámetros:

- `dataset_name="Zainab-Jamil30/telecom-churn-dataset"`
- `split="train"`
- `filename="datos/telco_churn.csv"`

Esto significa que:

- se descarga el dataset de Hugging Face,
- se toma la partición de entrenamiento,
- y además se guarda una copia local en formato CSV en la carpeta de datos del proyecto.

Después, la variable `df` store el DataFrame principal:

```python
df = loader.load()
df.head(10)
```

Con esto se valida que el dataset se haya cargado correctamente y que la estructura sea la esperada.

---

## 3. Exploración inicial del DataFrame

El notebook hace una revisión rápida de la estructura del dataset:

- número de filas,
- número de columnas,
- tipos de datos,
- memoria usada,
- valores no nulos,
- información general del DataFrame.

Esto es clave porque en análisis de datos, antes de modelar o sacar conclusiones, hay que verificar:

- si hay columnas vacías,
- si los tipos son correctos,
- si existen valores faltantes,
- si hay duplicados,
- si las variables están bien nombradas.

La celda principal hace esto con:

```python
print(f"Filas: {len(df)}")
print(f"Columnas: {len(df.columns)}")
df.info()
```

Con esta inspección se obtiene una visión general del conjunto y se detectan posibles problemas de calidad de datos.

---

## 4. Análisis exploratorio de variables clave

Después de la inspección inicial, el notebook revisa valores máximos y categorías de servicio, por ejemplo:

- `Age`
- `InternetService`
- otras columnas relevantes para entender el comportamiento del cliente

Ejemplo de la lógica:

```python
contador = df.loc[df["Age"]].max()
print(contador)
print("="*50)
print(df["InternetService"].unique())
```

Esto ayuda a verificar el rango de edades y los tipos de servicio de internet presentes en el dataset. Es una parte de la exploración descriptiva que orienta luego el análisis de churn.

---

## 5. Transformaciones para segmentación

El notebook realiza varias transformaciones para convertir variables continuas o raw en categorías más interpretables. Esto facilita la segmentación de clientes y la comparación entre grupos.

### 5.1. Segmentación por antigüedad

Se crea la columna `CategoriaAntiguedad` con `pd.cut`, dividiendo la antigüedad del cliente en rangos:

- Nuevo
- Estable
- Fiel
- Muy Fiel

Código conceptual:

```python
df["CategoriaAntiguedad"] = pd.cut(
    df["Tenure"],
    bins=[0, 12, 24, 48, 100],
    labels=["Nuevo", "Estable", "Fiel", "Muy Fiel"],
    include_lowest=True
)
```

Esto permite estudiar si los clientes más antiguos tienen menor churn o si los clientes nuevos muestran más riesgo.

### 5.2. Segmentación por edad

También se genera `GrupoEdad`:

- Joven
- Adulto
- Adulto Mayor

Esto ayuda a analizar si la edad está relacionada con la retención o cancelación del servicio.

Estas transformaciones son importantes porque permiten interpretar patrones de negocio en lenguaje más cercano a la gerencia, no solo en términos matemáticos.

---

## 6. Pregunta de negocio principal: churn vs tipo de contrato

La parte central del notebook responde esta pregunta:

> ¿Cómo varia la tasa de abandono según el tipo de contrato y cuál es la antigüedad crítica con mayor número de deserción?

### 6.1. Distribución del churn por tipo de contrato

Se calcula la proporción de clientes que abandonaron según el tipo de contrato:

```python
(
    df[df["Churn"] == 1]
    ["ContractType"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)
```

Esto genera un porcentaje de clientes que cancelaron, agrupados por tipo de contrato. La intención es medir qué clase de contrato tiene mayor riesgo de abandono.

### 6.2. Resumen por contrato: cantidad, porcentaje y tenure

Luego se agrupa por `ContractType` y se obtiene:

- cantidad de clientes que dejaron el servicio,
- porcentaje relativo,
- antigüedad promedio (`Tenure_Promedio`),
- antigüedad mínima,
- antigüedad máxima.

Código conceptual:

```python
resultado = (
    df[df["Churn"] == 1]
    .groupby("ContractType")
    .agg(
        Cantidad_Clientes=("Churn", "count"),
        Tenure_Promedio=("Tenure", "mean"),
        Tenure_Minimo=("Tenure", "min"),
        Tenure_Maximo=("Tenure", "max")
    )
)
```

Esto permite comparar si quienes abandonan tienen contratos de corta duración, mayor permanencia o si existe un punto crítico de antigüedad.

---

## 7. Interpretación de resultados

El notebook concluye que la mayoría de los clientes que abandonan tienen contratos de tipo **Month-to-month** (mensual). Esto indica que:

- los clientes con contratos de corta duración tienen mayor probabilidad de cancelar,
- los contratos de mayor duración parecen ofrecer más estabilidad,
- la retención está muy influenciada por el tipo de contrato.

También se observa que los clientes con contratos mensuales tienen una antigüedad promedio menor que la de quienes mantienen planes anuales o bianuales. Esto sugiere que el riesgo de cancelación se concentra en los usuarios recién incorporados o en quienes tienen menor lealtad.

En otras palabras, la deserción parece asociarse más con clientes menos comprometidos o con contratos más flexibles, no con clientes antiguos y estables.

---

## 8. Generación de reportes automáticos

El notebook también integra una clase llamada `Reportes`, diseñada para producir informes útiles sobre el dataset.

### 8.1. Reporte general

Se genera un reporte resumen con información como:

- número de filas,
- número de columnas,
- duplicados,
- tipos de dato,
- valores nulos,
- estadísticas descriptivas numéricas.

```python
from clases_po import Reportes

reportes = Reportes()
texto = reportes.generar_reporte(df)
print(texto)
```

### 8.2. Reporte descriptivo

También se genera un reporte más orientado a análisis exploratorio:

```python
descriptivo = reportes.generar_reporte_descriptivo(df)
print(descriptivo)
```

### 8.3. Impresión directa

Hay varias formas de mostrar los reportes:

```python
reportes.imprimir_reporte(df)
reportes.imprimir_reporte(df)
```

Esto permite visualizar en consola el resumen del dataset sin necesidad de exportarlo previamente.

---

## 9. Guardado de reportes en archivos

La última parte del notebook guarda los resultados en archivos de texto dentro de la carpeta de reportes.

### Ejemplo

```python
ruta = reportes.guardar_reporte(
    df,
    "reportes/telco_churn.txt",
)
```

Y luego:

```python
ruta = Path("reportes/Reporte_descriptivo_telco_churn.txt")
reportes.guardar_reporte_descriptivo(df, ruta)
```

Esto facilita que el análisis quede documentado y pueda revisarse después de la ejecución del notebook.

---

## 10. Valor del notebook para la empresa

Este notebook no solo hace análisis exploratorio; además conecta los datos con una decisión de negocio. Su valor es que ayuda a:

- detectar qué tipo de clientes abandonan más,
- identificar la relación entre antigüedad y churn,
- entender qué segmentación del cliente es más vulnerable,
- apoyar decisiones de retención comercial,
- generar evidencias para diseñar estrategias de servicio y marketing.

En términos de negocio, esto permite transformar la gestión comercial de un enfoque reactivo a uno basado en diagnóstico y datos.

---

## 11. Conclusión general

El notebook de la Semana 5 se enfoca en análisis de retención de clientes en telecomunicaciones usando datos reales del churn. A través de carga del dataset, exploración de variables, transformaciones para segmentación, análisis por tipo de contrato y la generación de reportes, se obtiene una visión útil de quiénes abandonan y bajo qué condiciones.

La conclusión más clara es que:

- los clientes con contratos mensuales son los que más deserción presentan,
- la antigüedad es un factor clave,
- la toma de decisiones puede apoyarse en evidencia empírica para diseñar mejores estrategias preventivas.

Si quieres, puedo ayudarte a convertir este contenido en una versión aún más formal y lista para usar en un README, informe académico o presentación.
