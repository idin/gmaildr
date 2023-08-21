import pandas as pd
from gmaildr.datascience.clustering.k_selection import find_optimal_k


def test_find_optimal_k_two_clusters_on_easy_data():
    # Two obvious blobs + a non-numeric column
    df = pd.DataFrame(
        {
            "x": [0.0, 0.1, -0.1, 8.0, 8.2, 7.9],
            "y": [0.0, 0.1, -0.2, 8.0, 7.9, 8.1],
            "tag": list("abcdef"),
        }
    )

    k, diag = find_optimal_k(df, max_k=5, method="silhouette", random_state=0)
    assert k == 2
    assert 2 in diag["candidate_ks"]
    assert isinstance(diag["inertias"], dict)
