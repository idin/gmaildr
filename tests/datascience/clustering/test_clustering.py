import pandas as pd
from gmaildr.datascience.clustering.cluster import cluster


def test_cluster_adds_column_and_partitions_rows():
    df = pd.DataFrame(
        {
            "x": [0.0, 0.1, -0.1, 8.0, 8.2, 7.9],
            "y": [0.0, 0.1, -0.2, 8.0, 7.9, 8.1],
            "tag": list("abcdef"),
        }
    )

    out = cluster(df, k=2, cluster_col="cluster", random_state=0, in_place=False)

    assert out is not df

    assert "cluster" in out.columns
    # labels are integers and exactly two clusters present
    assert out["cluster"].dtype.kind in {"i", "u"}
    assert out["cluster"].nunique() == 2
    # first three belong together, last three belong together (order of labels may differ)
    assert len({out.loc[0, "cluster"], out.loc[1, "cluster"], out.loc[2, "cluster"]}) == 1
    assert len({out.loc[3, "cluster"], out.loc[4, "cluster"], out.loc[5, "cluster"]}) == 1
    assert out.loc[0, "cluster"] != out.loc[3, "cluster"]
