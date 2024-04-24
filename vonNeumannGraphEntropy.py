# Name: VNGE
# Author: Reacubeth
# Time: 2021/1/25 16:01
# Mail: noverfitting@gmail.com
# Site: www.omegaxyz.com
# *_*coding:utf-8 *_*

#ligeramente modificado, para no siempre mostrar el tiempo de ejecución y regresar los valores H_vn

import time
import numpy as np
from scipy.sparse.linalg.eigen.arpack import eigsh


def normalized_laplacian(adj_matrix):
    nodes_degree = np.sum(adj_matrix, axis=1)
    nodes_degree_sqrt = 1/np.sqrt(nodes_degree)
    degree_matrix = np.diag(nodes_degree_sqrt)
    eye_matrix = np.eye(adj_matrix.shape[0])
    return eye_matrix - degree_matrix * adj_matrix * degree_matrix


def unnormalized_laplacian(adj_matrix):
    nodes_degree = np.sum(adj_matrix, axis=1)
    degree_matrix = np.diag(nodes_degree)
    return degree_matrix - adj_matrix


def VNGE_exact(adj_matrix, showTime=False):
    if showTime:
        start = time.time()
    nodes_degree = np.sum(adj_matrix, axis=1)
    c = 1.0 / np.sum(nodes_degree)
    laplacian_matrix = c * unnormalized_laplacian(adj_matrix)
    eigenvalues, _ = np.linalg.eig(laplacian_matrix)
    eigenvalues[eigenvalues < 0] = 0
    pos = eigenvalues > 0
    H_vn = - np.sum(eigenvalues[pos] * np.log2(eigenvalues[pos]))
    print('H_vn exact:', H_vn)
    if showTime:
        print('Time:', time.time() - start)
    return H_vn


def VNGE_FINGER(adj_matrix, showTime=False):
    if showTime:
        start = time.time()
    nodes_degree = np.sum(adj_matrix, axis=1)
    c = 1.0 / np.sum(nodes_degree)
    edge_weights = 1.0 * adj_matrix[np.nonzero(adj_matrix)]
    approx = 1.0 - np.square(c) * (np.sum(np.square(nodes_degree)) + np.sum(np.square(edge_weights)))
    laplacian_matrix = unnormalized_laplacian(adj_matrix)
    '''
    eigenvalues, _ = np.linalg.eig(laplacian_matrix)  # the biggest reduction
    eig_max = c * max(eigenvalues)
    '''
    eig_max, _ = eigsh(laplacian_matrix, 1, which='LM')
    if len(eig_max)==0:
        eig_max=[1/c] #esto es para evitar un error en el código de VNGE_FINGER cuando no se encuentran eigenvectores (si la gráfica es nula)
    else:
        eig_max = eig_max[0] * c
    H_vn = - approx * np.log2(eig_max)
    print('H_vn approx:', H_vn)
    if showTime:
        print('Time:', time.time() - start)
    return H_vn


"""Example:
nodes_num = 3000
sparsity = 0.01


tmp_m = np.random.uniform(0, 1, (nodes_num, nodes_num))
pos1 = tmp_m > sparsity
pos2 = tmp_m <= sparsity
tmp_m[pos1] = 0
tmp_m[pos2] = 1
tmp_m = np.triu(tmp_m)
adj_m = tmp_m + np.transpose(tmp_m)

VNGE_exact(adj_m)
VNGE_FINGER(adj_m)
"""