
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, LineString
import folium
import glob
import pandas as pd
import shapely.wkt
import shapely.ops
import math
import numpy as np
import constantes as C
import pickle



class Create_graph:
    
    def osmnx_graph_street_roads(query_madrid):
        
        ox.config(log_console=True, use_cache=True)
        G = ox.graph_from_place(query_madrid, network_type='drive', simplify=False)
        nodes, edges=ox.graph_to_gdfs(G)
        
        return G, nodes, edges
    
    
    def proc_save_graph_street_roads(query_madrid, name_csv_nodes_graph, name_csv_edges_graph, name_graph_pickle):
        
        G, nodes, edges = Create_graph.osmnx_graph_street_roads(query_madrid)
        nodes.to_csv(C.path_output_data+name_csv_nodes_graph)
        edges.to_csv(C.path_output_data+name_csv_edges_graph)
        
        with open(C.path_output_data+name_graph_pickle, 'wb') as f:
            pickle.dump(G, f)
        
        return G, nodes, edges
    
    
    def graph_to_html_folium_geograph(G, nodes, edges, path_html=None):
        
        G_nooneway= G.copy()
        G_oneway= G.copy()

        oneway=[]
        no_oneway=[]

        m = ox.plot_graph_folium(G, graph_map = None, popup_attribute=None,
                                 tiles='cartodbpositron', line_weight=0.001, zoom=100, color='skyblue')

        for u,v,k,d in G.edges(keys=True, data=True):
            if d['oneway']:
                oneway.append((u,v,k))
            else:
                no_oneway.append((u,v,k))

        G_nooneway.remove_edges_from(no_oneway)
        G_oneway.remove_edges_from(oneway)

        m = ox.plot_graph_folium(G_nooneway, graph_map = m, popup_attribute=None,
                                tiles='cartodbpositron', line_weight=0.001, zoom=100, color='blue')
        m = ox.plot_graph_folium(G_oneway, graph_map = m, popup_attribute=None,
                                tiles='cartodbpositron', line_weight=0.001, zoom=100, color = 'black')

        geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in nodes.geometry]
        
        for coordinates in geo_df_list:
            
            m.add_child(folium.CircleMarker(location=coordinates, 
                                            color='green',
                                            radius=.05,
                                            fill_opacity=.5))
        if path_html is not None:
            
            m.save(path_html)
            
        return m

        
    def read_sensor_location(path_sensor_location, 
                             path_save_partition_csv=C.path_save_partition_csv, num_partitions=C.num_partitions_sensor_tbl):
        
        
        glued_data = pd.DataFrame()

        for file_name in glob.glob(C.path_sensor_location+'*.csv'):
            
            x = pd.read_csv(file_name, low_memory=False, sep=";")
            pd_initial_data_position_sensor = pd.concat([glued_data,x],axis=0)

        pd_position_sensor = pd_initial_data_position_sensor.drop_duplicates()
        pd_position_sensor['random_col'] = np.random.randint(0, 100, pd_position_sensor.shape[0])
        
        for i in range(100):
            pd_position_sensor[pd_position_sensor['random_col']==i]\
                .to_csv(path_save_partition_csv+'pd_position_sensor_part_'+str(i))

        return pd_position_sensor
    
    
    def join_graph_edges_to_sensor(G, path_save_partition_csv=C.path_save_partition_csv,
                                   start_partition=0, end_partition=100):
        
        
        for i in range(start_partition, end_partition):
            
            print("Iteracion numero: ", str(i))
            pd_position_sensor = pd.read_csv(path_save_partition_csv+'pd_position_sensor_part_'+str(i))
            pd_position_sensor = pd_position_sensor[pd_position_sensor['latitud'].notna()]
            print(pd_position_sensor.shape)
            pd_position_sensor['from_to_graph'] = \
                [ox.get_nearest_edge(G, (np.float32(pd_position_sensor['latitud'].loc[i]), 
                                         np.float32(pd_position_sensor['longitud'].loc[i])), return_dist=True) 
                 if ((pd_position_sensor['latitud'].loc[i] is not None) & ((pd_position_sensor['longitud'].loc[i]) is not None))
                 else (-99, -99, -99, -99)
                 for i in range(pd_position_sensor.shape[0])]
            
            pd_position_sensor.to_csv(C.path_output_data+C.path_sensor_position_from_to+'_part_'+str(i)+'.csv')
            
            
if __name__=="__main__":
    
    print("Inicio: creación del grafo, nodos y aristas y guardados en pickle")
    # G, nodes, edges = Create_graph.osmnx_graph_street_roads(C.query_madrid)
    G, nodes, edges = Create_graph.proc_save_graph_street_roads(C.query_madrid, C.name_csv_nodes_graph, 
                                                                C.name_csv_edges_graph, C.name_graph_pickle)
    
    print("Lectura y guardado de la localización de los sensores")
    Create_graph.read_sensor_location(C.path_sensor_location, path_save_partition_csv=C.path_checkpoint_tbl, 
                                      num_partitions=C.num_partitions_sensor_tbl)
    with open(C.path_output_data+C.name_graph_pickle, 'rb') as f:
        G = pickle.load(f)
    print("Comienzo de la busqueda de la arista mas cercana a cada punto")
    Create_graph.join_graph_edges_to_sensor(G, path_save_partition_csv=C.path_save_partition_csv,
                                   start_partition=88, end_partition=100)    
    
    print("FIN")
        