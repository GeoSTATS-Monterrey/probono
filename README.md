# Mapeo en python con extención web en streamlib

En este mapa se presentan los datos relacionados con el tercer sector separados por varias categorias importantes de cada una de las organizaciones de manera que se puedan resaltar como guste el usuario y pueda usar la herramienta para ajustar las categorias a su interes.

## Dependencias

> Para poder correr correctamente el codigo se necesita la version 3.11 de Python o versiones superiores.

La dependecia más importante en este proyecto es _pipenv_. _Pipenv_ es una herramienta utilizada en el ecosistema de Python para gestionar las dependencias y los entornos virtuales de proyectos de desarrollo, de esta manera podemos utilizar un archivo llamado **Pipfile** para rastrear y definir las dependencias del proyecto facilmente. La manera de instalar esta dependencia es muy sencilla, se utiliza el siguiente comando:
```bash
pip install pipenv
```

El prototipo depende de las librerias de _pandas_ y _geopandas_ para realizar el procseo de mapeo. Tambien se usan partes de la liberia estandar de Python como `re`, que es una libreria de expresiones regulares para facilitar la limpieza de datos.
Para que funcione la pagina web se necesita _streamlit_ y para dar un formato a los datos se necesita _pydeck_.
Todas estas dependecias se encuentran en un archivo __pipfile__, este es un archivo de configuración utilizado principalmente por pipenv, una herramienta que se utiliza para administrar dependencias y entornos virtuales en proyectos de Python.

```bash
pipenv install
```

## Correr el servidor localmente:


## Agregar una categoria:
Para ello se tendra que modificar el apartado en python de _multiselect_ donde se agregará la nueva categoria.

```python
active_modes = st.multiselect( 
    'Selecciona la información de interés que quieres ver: ', [
        'primera catergoria',
        'segunda catergoria',
        'nueva catergoria',
    ],
    default=[  #En este apartado se establece las categorias predeterminadas
        'primera categoria',
        'nueva categoria',
    ],
)
```
### Dar formato a la categoría:
En este caso se necesita declarar un formato especifico para los datos, al usar pydeck podemos usar los layers viendo directamente su documentación:

[Documentacion de formatos pydeck](https://deckgl.readthedocs.io/en/latest/index.html)

Una vez hecho eso, se podrá ver la categoría deseada con el formato dado.
