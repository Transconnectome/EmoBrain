"""Representation-comparison metrics."""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler


def standardize(values):
    return StandardScaler().fit_transform(np.asarray(values, dtype=np.float64))


def linear_cka(left, right):
    left, right = standardize(left), standardize(right)
    cross = left.T @ right
    denominator = np.sqrt(
        np.sum((left.T @ left) ** 2) * np.sum((right.T @ right) ** 2)
    )
    return float(np.sum(cross**2) / denominator) if denominator > 0 else np.nan


def rsa_spearman(left, right):
    left_distance = pdist(standardize(left), metric="correlation")
    right_distance = pdist(standardize(right), metric="correlation")
    return float(spearmanr(left_distance, right_distance).statistic)


def neighbor_overlap(left, right, k=10):
    left_distance = squareform(pdist(standardize(left), metric="correlation"))
    right_distance = squareform(pdist(standardize(right), metric="correlation"))
    np.fill_diagonal(left_distance, np.inf)
    np.fill_diagonal(right_distance, np.inf)
    left_neighbors = np.argpartition(left_distance, k - 1, axis=1)[:, :k]
    right_neighbors = np.argpartition(right_distance, k - 1, axis=1)[:, :k]
    overlap = [
        len(set(a).intersection(b)) / k for a, b in zip(left_neighbors, right_neighbors)
    ]
    return float(np.mean(overlap))
