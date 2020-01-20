import numpy as np
import os

from smafed.cluster import Cluster
from datetime import datetime
from helpers.cluster_utils import load_clusters

import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


class SemanticHistogramClusterization:
    """
    Class for semantic histogram clustering.
    """

    def __init__(self, folder_with_clusters, shr_min=0.9, shr_threshold=0.25, histogram_ratio_coefficient=100):
        """
        :param folder_with_clusters:folder where clusters are stored or would be stored
        :param shr_min: minimum semantic histogram ratio
        :param shr_threshold: similarity threshold
        :param histogram_ratio_coefficient: coefficient which would be used in calculating delta

        Load data if it exist.
        """
        self.shr_min = shr_min
        self.shr_threshold = shr_threshold
        self.histogram_ratio_coefficient = histogram_ratio_coefficient
        self.folder_with_clusters = folder_with_clusters
        self.histogram_ratio_coefficient = histogram_ratio_coefficient
        if os.path.exists(folder_with_clusters):
            self.clusters, self.clusters_creating_time = load_clusters(self.folder_with_clusters)
        else:
            self.clusters = {}
            self.clusters_creating_time = {}

    def add_element(self, element):
        """
        :param element: element which have to be inserted.

        Look for match cluster, if it don`t exist create new.
        Return cluster index.
        """
        idx_acceptable = []
        shr_new_list = []
        for cluster, vector in self.clusters.items():
            shr = vector.compute_semantic_histogram_dict(candidate=element)
            if self.is_acceptable(shr["old"], shr["new"]):
                idx_acceptable.append(cluster)
                shr_new_list.append(shr["new"])

        if not idx_acceptable:
            # shr_acceptable is empty, then make  new cluster
            self.make_new_cluster(element=element)
        else:
            # add the element into existing cluster
            # anyway, chose a cluster that have bigger SHR
            idx_biggest = np.argmax(np.array(shr_new_list))
            idx = idx_acceptable[idx_biggest]
            self.add_into_cluster(element, idx)

    def add_into_cluster(self, element, idx):
        """
        :param element: element which have to be inserted.
        :param idx: index of cluster.

        Add element in cluster.
        """
        self.clusters[idx].add_element(element)

    def is_acceptable(self, shr_old, shr_new):
        """
        :param shr_old: semantic histogram ratio old.
        :param shr_new: semantic histogram ratio new.

        Check condition for adding element in existing cluster.
        """
        delta = self.calc_delta(shr_old, shr_new)

        cond_graded = shr_old <= shr_new
        cond_shr_min = shr_new > self.shr_min
        cond_delta = shr_old - shr_new < delta

        if np.isnan(shr_old - shr_new):
            cond_delta = True
        return cond_graded or (cond_shr_min and cond_delta)

    def calc_delta(self, shr_old, shr_new):
        """
        :param shr_old: semantic histogram ratio old.
        :param shr_new: semantic histogram ratio new.

        Calculate delta.
        """
        delta = np.abs((shr_old - shr_new) / shr_old) * self.histogram_ratio_coefficient
        return delta

    def make_new_cluster(self, element):
        """
        :param element: element which have to be inserted.

        Create new cluster with element.
        Add current date and time(datetime object) to array of clusters creating date and time.
        """
        cluster_new = Cluster(element=element, shr_threshold=self.shr_threshold)
        try:
            idx_new = max(self.clusters.keys()) + 1
        except ValueError:
            idx_new = 0
        self.clusters[idx_new] = cluster_new
        self.clusters_creating_time[idx_new] = datetime.now()

    def clustering_elements(self, elements):
        """
        :param elements: elements which have to be clustered.

        Cluster elements.
        """
        for elem in elements:
            self.add_element(elem.reshape(1, -1))

    def __len__(self):
        """
        Return number of clusters.
        """
        return len(self.clusters)
