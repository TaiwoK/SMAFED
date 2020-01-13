import numpy as np

from sklearn.metrics.pairwise import cosine_similarity


class Cluster:
    """
    Class for cluster.
    """

    def __init__(self, shr_threshold, element):
        """
        :param shr_threshold: similarity threshold
        :params elements: elements which have to be added to cluster
        """
        self.cluster = element
        self.shr_threshold = shr_threshold

    def compute_similarities(self, candidate=None, similarities_old=None):
        """
        :param candidate: candidate to adding into cluster
        :param similarities_old: similarities which passed when calculate SHR['new']

        Return upper triangular matrix of similarities as row.
        """
        if candidate is not None:
            similarities = Cluster.calc_similarity(candidate, self.cluster)
            similarities = np.concatenate((similarities_old, similarities.reshape(-1, )))
        else:
            similarities = Cluster.calc_similarity(self.cluster, self.cluster)
            similarities = np.triu(similarities, k=1)
            similarities = similarities[np.where(similarities != 0)]
        return similarities

    @staticmethod
    def calc_similarity(a, b):
        """
        :param a, b: arrays which similarities have to be calculated

        Return calculated similarities.
        """
        return cosine_similarity(a, b)

    def compute_semantic_histogram(self, candidate=None, similarities_old=None):
        """
        :param candidate: candidate to inserting into cluster
        :param similarities_old: old similarities (passing when calculate SHR['new'])

        Return semantic histogram.
        """
        bins = [-np.inf, self.shr_threshold, np.inf]

        similarities = self.compute_similarities(candidate=candidate, similarities_old=similarities_old)
        sh, edges = np.histogram(similarities, bins=bins)

        return sh, edges, similarities

    def compute_semantic_histogram_dict(self, candidate=None):
        """
        :param candidate: candidate to inserting into cluster

        Return dictionary with two semantic histogram values: old and new.
        """
        hist, edges, similarities_old = self.compute_semantic_histogram()
        over_th = edges >= self.shr_threshold

        hist_over_th = np.array(hist)[over_th[:-1]]

        shr = {"old": np.sum(hist_over_th) / np.sum(hist)}

        if candidate is not None:
            hist, edges, _ = self.compute_semantic_histogram(candidate=candidate, similarities_old=similarities_old)
            over_th = edges >= self.shr_threshold
            hist_over_th = np.array(hist)[over_th[:-1]]
            shr["new"] = np.sum(hist_over_th) / np.sum(hist)

        return shr

    def add_element(self, candidate=None):
        """
        :param candidate: candidate to inserting into cluster

        Add element to cluster.
        """
        self.cluster = np.append(self.cluster, candidate, axis=0)

    def __len__(self):
        """
        Return number of element in cluster.
        """
        return self.cluster.shape[0]
