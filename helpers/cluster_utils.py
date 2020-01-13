import pickle
import os

from numpy import array_equal


def load_clusters(folder_with_clusters):
    """
    :param folder_with_clusters:folder where clusters are stored.

    Load clusters from folder.
    Load time of clusters creating from file.
    """
    cluster_files_list = os.listdir(folder_with_clusters)
    cluster_files_list.remove("clusters_creating_time.pcl")
    cluster_files_list = sorted(cluster_files_list, key=lambda string: int(string[:-4]))
    clusters = {}
    for cluster_file in cluster_files_list:
        with open(os.path.join(folder_with_clusters, cluster_file), 'rb') as file:
            clusters[int(cluster_file[:-4])] = pickle.load(file)
    with open(os.path.join(folder_with_clusters, "clusters_creating_time.pcl"), 'rb') as file:
        clusters_creating_time = pickle.load(file)
    return clusters, clusters_creating_time


def save_clusters(clusters, clusters_creating_time, folder_with_clusters):
    """
    :param clusters: dictionary where key - clusters id, value - array of vectors in cluster.
    :param clusters_creating_time: dictionary where key - clusters id, value - cluster creating time.
    :param folder_with_clusters:folder where clusters would be stored.

    Save clusters in folder.
    Save time of clusters creating in folder.
    """
    if not os.path.exists(folder_with_clusters):
        os.mkdir(folder_with_clusters)
    for cluster, vectors in clusters.items():
        with open(os.path.join(folder_with_clusters, f"{cluster}.pcl"), 'wb') as file:
            pickle.dump(vectors, file)
    with open(os.path.join(folder_with_clusters, f"clusters_creating_time.pcl"), 'wb') as file:
        pickle.dump(clusters_creating_time, file)


def find_cluster(clusters, element):
    """
    :param clusters: dictionary where key - clusters id, value - array of vectors in cluster.
    :param element: element which cluster have to be founded.

    Return cluster of element.
    """
    return [key for key, value in clusters.items() if any([array_equal(vector, element) for vector in value.cluster])][
        0]


def search_clusters_of_vectors(clusters, elements):
    """
    :param clusters: dictionary where key - clusters id, value - array of vectors in cluster.
    :param elements: elements which cluster have to be founded.

    Found cluster of elements.
    Return array of cluster ids.
    """

    return [find_cluster(clusters, element) for element in elements]
