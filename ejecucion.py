# Importamos los paquetes de interes
import warnings
import time
from shapely.errors import ShapelyDeprecationWarning
import pandas as pd
# Importamos de nuestro subpaquete los modulos importantes
from boundaries_algorithm.preprocessing_module import coordinates_projection
from boundaries_algorithm.validation.validation import (
    polygons_init, 
    poly_no_inter, 
    smooth_polygons, 
    ident_good_proj
)
from boundaries_algorithm.visualization_module import plot_folium, plot_folium_final

# Desactivamos los warnings
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter("ignore", UserWarning)

inicio = time.time()

# Parametros
actual_epsg = 'epsg:4686'
convert_epsg = 'epsg:3116'
column_id = 'zona'
actual_1="latitud"
actual_2="longitud" 
convert_1="X"
convert_2="Y"
threshold_N = 0.90
buffer_area = 0.15
N = 100

# Importamos el df
df = pd.read_csv('data.csv')

# Proyectamos las coordenadas del df al sistema euclidiano
df = coordinates_projection(
    main_df=df,
    actual_epsg=actual_epsg,
    convert_epsg=convert_epsg,
    actual_1=actual_1, 
    actual_2=actual_2, 
    convert_1=convert_1,
    convert_2=convert_2
)

print(f'Proyección en \t\t {round(time.time()-inicio, 2)} segundos.')

# Inicializacion
init_loc_hull, init_loc_tree = polygons_init(
    main_df=df,
    column_id=column_id,
    threshold_N=threshold_N,
    buffer_area=buffer_area,
    convert_1=convert_1,
    convert_2=convert_2
)

print(f'Inicialización en \t {round(time.time()-inicio, 2)} segundos.')
inicio = time.time()

# Eliminacion intersecciones
inter_loc_hull, inter_loc_tree = poly_no_inter(
    main_loc_hull=init_loc_hull,
    main_loc_tree=init_loc_tree
)

print(f'Intersecciones en \t {round(time.time()-inicio, 2)} segundos.')
time.time()

# Creacion poligonos suaves
smooth_loc_hull = smooth_polygons(
    main_loc_hull=inter_loc_hull,
    N=N
)

print(f'Polígonos suaves en \t {round(time.time()-inicio, 2)} segundos.')
time.time()

# Identify good projects
df_good, df_bad, percentage = ident_good_proj(
    main_df=df,
    main_loc_hull=smooth_loc_hull,
    column_id=column_id,
    convert_1=convert_1,
    convert_2=convert_2
)

print(f'Validación en \t\t {round(time.time()-inicio, 2)} segundos.')
time.time()

df['Validado'] = 'NO'
df.loc[df_good.index, 'Validado'] = 'SI'
resumen = df.pivot_table(index=['zona'], columns='Validado', aggfunc='size', fill_value='')
resumen['Validación [%]'] = 100*round(resumen['SI']/(resumen['SI']+resumen['NO']), 4)

print('-'*12+' RESUMEN '+'-'*12)
print(resumen)
print('-'*34)

# PLOTS

plot_folium(
    loc_hull=init_loc_hull,
    loc_tree=init_loc_tree,
    df=df,
    name='001_inicializacion'
)

plot_folium(
    loc_hull=inter_loc_hull,
    loc_tree=inter_loc_tree,
    df=df,
    name='002_intersecciones'
)

plot_folium(
    loc_hull=smooth_loc_hull,
    loc_tree=inter_loc_tree,
    df=df,
    name='003_smooth'
)

plot_folium_final(
    loc_hull=smooth_loc_hull,
    loc_tree=inter_loc_tree,
    df=df,
    df_good=df_good,
    df_bad=df_bad,
    name='004_final'
)
