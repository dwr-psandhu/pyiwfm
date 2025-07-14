import numpy as np
from scipy.sparse import lil_matrix, vstack, identity
from scipy.sparse.linalg import lsqr
from scipy.spatial import Delaunay


def barycentric_weights(tri_coords, pt):
    """
    Compute barycentric coordinates of a point within a triangle.
    """
    T = np.vstack((tri_coords.T, np.ones(3)))  # 3x3
    bary = np.linalg.solve(T, np.append(pt, 1))
    return bary


def build_least_squares_system(nodes, elements, obs_pts, obs_vals, reg_weight=1e-3):
    """
    Constructs and solves a least squares system to infer node values
    that best match observed values at interior points using linear interpolation.
    Includes optional Tikhonov (L2) regularization for smoothness.

    Parameters:
    - nodes: (N, 2) array of node coordinates
    - elements: (M, 3) array of triangle vertex indices
    - obs_pts: (K, 2) array of observation coordinates
    - obs_vals: (K,) array of observed values
    - reg_weight: regularization weight (float)
    """
    n_nodes = len(nodes)
    n_obs = len(obs_pts)
    A = lil_matrix((n_obs, n_nodes))
    b = np.zeros(n_obs)

    for i, (pt, val) in enumerate(zip(obs_pts, obs_vals)):
        for tri in elements:
            tri_coords = nodes[tri]  # 3x2
            tri_delaunay = Delaunay(tri_coords)
            if tri_delaunay.find_simplex(pt) >= 0:
                bary = barycentric_weights(tri_coords, pt)
                for k, node_idx in enumerate(tri):
                    A[i, node_idx] = bary[k]
                b[i] = val
                break
        else:
            print(f"Observation point {pt} not found in any triangle.")

    # Regularization term: minimize ||x||^2 (identity regularization)
    L = identity(n_nodes)
    A_reg = reg_weight * L
    b_reg = np.zeros(n_nodes)

    # Stack observation and regularization systems
    A_total = vstack([A, A_reg])
    b_total = np.concatenate([b, b_reg])

    result = lsqr(A_total.tocsr(), b_total)
    return result[0]  # inferred node values


# Example usage (for testing)
if __name__ == "__main__":
    # Define a simple triangular mesh (2 triangles)
    nodes = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    elements = np.array([[0, 1, 2], [1, 3, 2]])

    # Observations inside triangles
    obs_pts = np.array(
        [[0.25, 0.25], [0.75, 0.25], [0.5, 0.75], [0.6, 0.4], [0.3, 0.6]]
    )
    obs_vals = np.array([1.0, 2.0, 1.5, 1.8, 1.2])

    inferred_vals = build_least_squares_system(
        nodes, elements, obs_pts, obs_vals, reg_weight=1e-2
    )

    print("Inferred node values:", inferred_vals)
