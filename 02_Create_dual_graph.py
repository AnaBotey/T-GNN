
import pandas as pd
import glob
import pickle
import osmnx as ox




def join_all_files(path):

    pd_sensor=pd.DataFrame()
    for i in glob.glob(path+"*.csv"):

        df = pd.read_csv(str(i)).drop(['Unnamed: 0'], axis=1)
        pd_sensor = pd.concat([df, pd_sensor],axis=0)

    pd_sensor = pd_sensor.drop(['Unnamed: 0.1'],axis=1)    
    pd_sensor['u'] = pd_sensor['from_to_graph'].apply(lambda x: eval(x)[0])
    pd_sensor['v'] = pd_sensor['from_to_graph'].apply(lambda x: eval(x)[1])
    pd_sensor['uv'] = pd_sensor['from_to_graph'].apply(lambda x: (eval(x)[0], eval(x)[1]))
    pd_sensor['distance'] = pd_sensor['from_to_graph'].apply(lambda x: eval(x)[2])
    pd_sensor = pd_sensor.drop(['from_to_graph', 'distance'], axis=1)
    pd_sensor['sensor']=True
    print(pd_sensor.drop_duplicates().shape, pd_sensor.shape)
    
    return pd_sensor


def read_pd_edges_graph(path_pd_edges):

    pd_edges= pd.read_csv(path_pd_edges).drop_duplicates()
    pd_edges['name_node']=['X'+str(i) for i in range(pd_edges.shape[0])]
    pd_edges['pd_edges']=True
    pd_edges = pd_edges[(pd_edges["name_node"].str.contains('X', na=True))]
    
    return pd_edges

def join_pd_edges_sensor(pd_edges, pd_sensor): 
    
    pd_edges_f= pd_edges.merge(pd_sensor, on=['u','v'],how='left')
    pd_edges_f = pd_edges_f[(pd_edges_f["name_node"].str.contains('X', na=True))]
    return pd_edges_f



def convert_to_dual_graph(path, path_pd_edges):
    
    print("== Uniendo todos los ficheros de sensores")
    pd_sensor=join_all_files(path)
    print(pd_sensor.shape)
    print("== Leyendo dataset final de sensores")
    pd_edges = read_pd_edges_graph(path_pd_edges)
    print("== Leyendo dataset final de sensores")
    pd_edges_f = join_pd_edges_sensor(pd_edges, pd_sensor)
    print(pd_edges_f.shape)
    print("== Convirtiendo a dual el grafo original")
    pd_edges_dual = pd.DataFrame()
    pd_edges_dual['from']=list(range(pd_edges_f.shape[0]))
    pd_edges_dual['to']=list(range(pd_edges_f.shape[0]))

    for i in range(pd_edges.shape[0]):

        pd_edges_dual['from'].iloc[i]=pd_edges_f['name_node'].iloc[i]
        pd_edges_dual['to'].iloc[i]=str(list(pd_edges_f['name_node'][pd_edges_f['u']==pd_edges_f['v'].iloc[i]].values))
        
    pd_edges_dual = pd_edges_dual[(pd_edges_dual["from"].str.contains('X', na=False))]
    print("== Operaciones para hacer explode a la tabla de aristas")
    # print(pd_edges_dual['to'].head())
    pd_edges_dual['to'] = pd_edges_dual['to'].apply(lambda x: eval(x))
    pd_edges_dual_final = pd_edges_dual.explode('to').drop_duplicates()
    pd_nodes_dual_final = pd_edges.copy()
    
    return pd_edges_dual_final, pd_nodes_dual_final


def proc_save_dual_graph_nodes_edges(path, path_pd_edges, path_save_dual_nodes, path_save_dual_edges):
    
    pd_edges_dual_final, pd_nodes_dual_final = convert_to_dual_graph(path, path_pd_edges)
    pd_nodes_dual_final.to_csv(path_save_dual_nodes)
    pd_edges_dual_final.to_csv(path_save_dual_edges)
    
    return pd_edges_dual_final, pd_nodes_dual_final


if __name__=="__main__":

    path_match_sensor_edge = "../../Codigo/data_output/match_sensor_edge/"
    path_graph='../data_output/graph/graph.pickle'
    path_pd_edges='../data_output/graph/graph_edges.csv'

    path_save_dual_nodes = C.path_tablas_intermedias+"pd_nodes_dual.csv"  
    path_save_dual_edges = C.path_tablas_intermedias+"pd_edges_dual.csv"
    pd_edges_dual_final, pd_nodes_dual_final = proc_save_dual_graph_nodes_edges(path_match_sensor_edge, path_pd_edges, 
                                                                            path_save_dual_nodes, path_save_dual_edges)