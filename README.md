# TP SIM FINAL - Zapateria

Simulador de sistema de colas para una zapateria, desarrollado en Python con Streamlit.

## Descripcion

El sistema simula, por eventos discretos, el funcionamiento diario de una zapateria donde:
- Llegan clientes con tiempos entre llegadas exponenciales.
- La atencion al cliente tiene tiempo uniforme.
- Parte de los clientes retira zapatos listos.
- Parte de los clientes deja zapatos para reparar.
- El empleado alterna entre atender clientes y reparar, pudiendo pausar reparaciones cuando llega un cliente.

La app muestra metricas globales y una tabla de eventos del dia 1 para analizar el vector de estado.

## Estructura del proyecto

- `TP SIM FINAL/app.py`: aplicacion principal en Streamlit.
- `.gitignore`: exclusiones basicas para entorno Python.

## Requisitos

- Python 3.10 o superior
- Paquetes:
	- streamlit
	- pandas

## Instalacion

```bash
pip install streamlit pandas
```

## Ejecucion

Desde la carpeta raiz del repositorio:

```bash
streamlit run "TP SIM FINAL/app.py"
```

Luego abrir en navegador la URL local que muestra Streamlit (normalmente `http://localhost:8502`).

## Parametros configurables

En la barra lateral de la app:
- Dias a simular
- Media de llegadas (distribucion exponencial)
- Tiempo de atencion minimo y maximo (uniforme)
- Tiempo de reparacion minimo y maximo (uniforme)
- Stock inicial de zapatos listos

## Salidas principales

- Tiempo promedio de reparacion
- Maximo historico de clientes en cola
- Instantes donde se alcanza el maximo de cola
- Tabla de eventos del dia 1 con el detalle del estado del sistema
