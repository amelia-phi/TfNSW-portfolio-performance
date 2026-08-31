"""Group accepted source records into project clusters."""

from collections.abc import Iterable

import pandas as pd


REQUIRED_SOURCE_COLUMNS = {
    "source_dataset",
    "source_project_id",
}


REQUIRED_MATCH_COLUMNS = {
    "left_source_dataset",
    "left_source_project_id",
    "right_source_dataset",
    "right_source_project_id",
}


def build_source_record_key(
    source_dataset: object,
    source_project_id: object,
) -> str:
    """Build a stable identity for one source project."""

    return (
        f"{str(source_dataset).strip()}"
        f"::{str(source_project_id).strip()}"
    )


def add_source_record_keys(
    source_records: pd.DataFrame,
) -> pd.DataFrame:
    """Add a unique cross-source key to every source project."""

    missing_columns = REQUIRED_SOURCE_COLUMNS.difference(
        source_records.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing source-record columns: "
            + ", ".join(sorted(missing_columns))
        )

    result = source_records.copy()

    missing_values = (
        result["source_dataset"].isna()
        | result["source_project_id"].isna()
        | result["source_dataset"]
        .astype("string")
        .str.strip()
        .eq("")
        | result["source_project_id"]
        .astype("string")
        .str.strip()
        .eq("")
    )

    if missing_values.any():
        raise ValueError(
            "One or more source identities are blank."
        )

    result["source_record_key"] = [
        build_source_record_key(
            source_dataset,
            source_project_id,
        )
        for source_dataset, source_project_id in zip(
            result["source_dataset"],
            result["source_project_id"],
            strict=True,
        )
    ]

    duplicate_keys = result[
        "source_record_key"
    ].duplicated(keep=False)

    if duplicate_keys.any():
        raise ValueError(
            "Duplicate source-record keys were found."
        )

    return result


class _DisjointSet:
    """Track connected source records using union-find."""

    def __init__(self, items: Iterable[str]) -> None:
        self._parent = {
            item: item
            for item in items
        }

    def find(self, item: str) -> str:
        """Return the root of the group containing an item."""

        while self._parent[item] != item:
            self._parent[item] = self._parent[
                self._parent[item]
            ]
            item = self._parent[item]

        return item

    def union(
        self,
        left_item: str,
        right_item: str,
    ) -> None:
        """Connect the groups containing two items."""

        left_root = self.find(left_item)
        right_root = self.find(right_item)

        if left_root == right_root:
            return

        preferred_root = min(
            left_root,
            right_root,
        )
        other_root = max(
            left_root,
            right_root,
        )

        self._parent[other_root] = preferred_root


def assign_match_groups(
    source_records: pd.DataFrame,
    accepted_matches: pd.DataFrame,
) -> pd.DataFrame:
    """Assign every source project to a connected match group."""

    missing_columns = REQUIRED_MATCH_COLUMNS.difference(
        accepted_matches.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing accepted-match columns: "
            + ", ".join(sorted(missing_columns))
        )

    records = add_source_record_keys(source_records)
    record_keys = set(records["source_record_key"])
    groups = _DisjointSet(record_keys)

    for match in accepted_matches.to_dict(
        orient="records"
    ):
        left_key = build_source_record_key(
            match["left_source_dataset"],
            match["left_source_project_id"],
        )
        right_key = build_source_record_key(
            match["right_source_dataset"],
            match["right_source_project_id"],
        )

        unknown_keys = {
            left_key,
            right_key,
        }.difference(record_keys)

        if unknown_keys:
            raise ValueError(
                "Accepted match contains unknown "
                "source-record keys: "
                + ", ".join(sorted(unknown_keys))
            )

        groups.union(left_key, right_key)

    records["match_group_root"] = records[
        "source_record_key"
    ].map(groups.find)

    unique_roots = sorted(
        records["match_group_root"].unique()
    )
    group_id_map = {
        root: f"GROUP-{number:04d}"
        for number, root in enumerate(
            unique_roots,
            start=1,
        )
    }

    records["match_group_id"] = records[
        "match_group_root"
    ].map(group_id_map)

    records["match_group_size"] = (
        records.groupby("match_group_id")[
            "source_record_key"
        ].transform("size")
    )

    records["has_cross_source_match"] = (
        records["match_group_size"] > 1
    )

    return records
