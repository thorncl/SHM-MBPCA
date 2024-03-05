import dask.dataframe as daskdf
import numpy as np
from dask import delayed
from glob import glob

@delayed
def dot_p_b(X_b, t_T, n_rows, n_features, no_norm) -> np.ndarray:

    if X_b.shape != (n_rows, n_features):
        X_b = X_b.transpose()

    num = t_T.transpose().dot(X_b)
    denom = t_T.transpose().dot(t_T)
    p_b_delayed = num / denom

    if no_norm:
        return p_b_delayed
    else:
        return p_b_delayed/np.linalg.norm(p_b_delayed)
    
@delayed
def dot_t_b(X_b, p_b, n_rows, n_features) -> np.ndarray:

    p_b = p_b.reshape(-1, 1)

    if X_b.shape != (n_features, n_rows):
        X_b = X_b.transpose()

    num = p_b.transpose().dot(X_b)
    denom = np.sqrt(n_features)
    t_b_delayed = num / denom

    if t_b_delayed.shape != (n_rows, 1):
        t_b_delayed = t_b_delayed.transpose()

    return t_b_delayed

@delayed
def compute_variance_explained(res, block) -> float:
    
    trace_residuals = np.trace(res.transpose().dot(res))
    trace_blocks = np.trace(block.transpose().dot(block))

    return abs(1 - (trace_residuals/trace_blocks))*100
    
def read_hdfs(root, read_keys) -> daskdf:

    padded_files = []
    folders = glob(root + '/sensor_data_*')
    folders.sort()

    for folder in folders:
        key = folder.split('_', folder.count('_'))[-1]
        
        if key in read_keys:
            padded_files.extend(glob(root + '/sensor_data_' + key + '/scaled_*_parallel_padded.h5'))

    padded_files = sorted(padded_files, key = lambda x: (int(x.split('_')[-7]), int(x.split('_')[-5]), int(x.split('_')[-3])))
    return daskdf.read_hdf(padded_files, key = 'data', sorted_index = True)

