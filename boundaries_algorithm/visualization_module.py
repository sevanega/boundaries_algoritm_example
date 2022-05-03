"""
A module for visualizing GIS data
"""
import numpy as np
import folium
from boundaries_algorithm.preprocessing_module import (
    crs_transformer,
    crs_transformation,
)

def plot_folium(loc_hull, loc_tree, df, name):
    """
    """
    crs_4686 = "epsg:4686"
    crs_3116 = "epsg:3116"
    transformer = crs_transformer(crs_4686, crs_3116)
    mapa_x, mapa_y = df[["latitud", "longitud"]].mean().values
    m = folium.Map(location=(mapa_x, mapa_y), zoom_start=12, tiles="cartodbpositron")
    colors = ["chocolate","blue","grey","purple"]
    for key, value in loc_hull.items():
        color = colors.pop()
        cluster = folium.FeatureGroup(name=key, show=False).add_to(m)
        x, y = value.exterior.coords.xy
        transformer = crs_transformer(crs_3116, crs_4686)
        lat, lon = crs_transformation(transformer, x, y)
        pts = np.vstack((np.array(lat), np.array(lon))).T
        cluster.add_child(folium.PolyLine(pts, color=color, weight=2.5, opacity=1))
        T = loc_tree[key]
        for i, j in T.edges:
            latitud_i = df.loc[i, "latitud"]
            longitud_i = df.loc[i, "longitud"]
            latitud_j = df.loc[j, "latitud"]
            longitud_j = df.loc[j, "longitud"]
            cluster.add_child(
                folium.PolyLine(
                    [(latitud_i, longitud_i), (latitud_j, longitud_j)],
                    color="black",
                    weight=2.5,
                    opacity=1,
                )
            )
        df_aux = df.loc[df['zona']==key].copy()
        for key, value in df_aux[['latitud','longitud']].iterrows():
            lat, lon = value
            cluster.add_child(
                folium.Circle(radius=50, location=[lat, lon], color=color, fill=True)
            )

    folium.LayerControl(name="Layer Control", collapsed=True).add_to(m)
    m.save('maps/' + name + '.html')


def plot_folium_final(loc_hull, loc_tree, df, df_good, df_bad, name):
    """
    """
    crs_4686 = "epsg:4686"
    crs_3116 = "epsg:3116"
    transformer = crs_transformer(crs_4686, crs_3116)
    mapa_x, mapa_y = df[["latitud", "longitud"]].mean().values
    m = folium.Map(location=(mapa_x, mapa_y), zoom_start=12, tiles="cartodbpositron")
    colors = ["chocolate","blue","grey","purple"]
    for key, value in loc_hull.items():
        color = colors.pop()
        cluster = folium.FeatureGroup(name=key, show=False).add_to(m)
        x, y = value.exterior.coords.xy
        transformer = crs_transformer(crs_3116, crs_4686)
        lat, lon = crs_transformation(transformer, x, y)
        pts = np.vstack((np.array(lat), np.array(lon))).T
        cluster.add_child(folium.PolyLine(pts, color=color, weight=2.5, opacity=1))
        T = loc_tree[key]
        for i, j in T.edges:
            latitud_i = df.loc[i, "latitud"]
            longitud_i = df.loc[i, "longitud"]
            latitud_j = df.loc[j, "latitud"]
            longitud_j = df.loc[j, "longitud"]
            cluster.add_child(
                folium.PolyLine(
                    [(latitud_i, longitud_i), (latitud_j, longitud_j)],
                    color="black",
                    weight=2.5,
                    opacity=1,
                )
            )
        df_aux_good = df_good.loc[df_good['zona']==key].copy()
        for key_1, value in df_aux_good[['latitud','longitud']].iterrows():
            lat, lon = value
            cluster.add_child(
                folium.Circle(radius=50, location=[lat, lon], color='lime', fill=True)
            )
        df_aux_bad = df_bad.loc[df_bad['zona']==key].copy()
        for key_2, value in df_aux_bad[['latitud','longitud']].iterrows():
            lat, lon = value
            cluster.add_child(
                folium.Circle(radius=50, location=[lat, lon], color='red', fill=True)
            )

    folium.LayerControl(name="Layer Control", collapsed=True).add_to(m)
    m.save('maps/' + name + '.html')
