from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "infrastructure_pipeline_transport_raw.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_register.csv"
)

VALIDATION_OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "data_quality_exceptions.csv"
)


REQUIRED_COLUMNS = {
    "Sector",
    "Project name",
    "Estimated Value",
    "Procurement Strategy",
    "Current Phase",
    "Procurement Start Date (est.)",
    "Procurement End Date (est.)",
    "Construction Start Date (est.)",
    "Construction End Date (est.)",
    "Project Link",
    "Source Lifecycle",
}


LIFECYCLE_PRIORITY = {
    "Pipeline": 1,
    "In Planning": 2,
}


VALUE_BANDS = {
    "$": {
        "label": "$50M to $100M",
        "minimum": 50,
        "maximum": 100,
    },
    "$$": {
        "label": "$100M to $250M",
        "minimum": 100,
        "maximum": 250,
    },
    "$$$": {
        "label": "$250M to $500M",
        "minimum": 250,
        "maximum": 500,
    },
    "$$$$": {
        "label": "$500M to $1B",
        "minimum": 500,
        "maximum": 1000,
    },
    "$$$$$": {
        "label": "Over $1B",
        "minimum": 1000,
        "maximum": None,
    },
    "TBA": {
        "label": "To be advised",
        "minimum": None,
        "maximum": None,
    },
    "TBC": {
        "label": "To be confirmed",
        "minimum": None,
        "maximum": None,
    },
}


PROCUREMENT_STRATEGIES = {
    "ECI": "Early Contractor Involvement",
    "VECI": "Very Early Contractor Involvement",
    "CO": "Construct Only",
    "CD&C": "Collaborative Design and Construct",
    "D&C": "Design and Construct",
    "D&C+": "Disaggregated Design and Construct",
    "DF&C": "Design, Finalisation and Construct",
    "DP": "Delivery Partner",
    "MC": "Managing Contractor",
    "ITC": "Incentivised Target Cost",
    "A": "Alliance",
    "Alliance": "Alliance",
    "PPP": "Public Private Partnership",
    "Various": "Various",
    "TBA": "To be advised",
    "TBC": "To be confirmed",
}


CURRENT_PHASES = {
    "Strategic Planning": (
        "Preparation and approval of strategic business case"
    ),
    "Final Business Case": (
        "Preparation and approval of final business case"
    ),
    "Design": (
        "Preparation and approval of project design"
    ),
    "Construction Procurement": (
        "Preparation, approval and release of "
        "procurement documents"
    ),
    "Rolling Program": (
        "Rolling program with ongoing procurement and delivery"
    ),
}


COLUMN_NAMES = {
    "Sector": "sector",
    "Project name": "project_name",
    "Estimated Value": "estimated_value_code",
    "Procurement Strategy": "procurement_strategy_code",
    "Current Phase": "current_phase",
    "Procurement Start Date (est.)":
        "procurement_start_period",
    "Procurement End Date (est.)":
        "procurement_end_period",
    "Construction Start Date (est.)":
        "construction_start_period",
    "Construction End Date (est.)":
        "construction_end_period",
    "Project Link": "project_url",
    "Source Lifecycle": "pipeline_category",
}


FINAL_COLUMN_ORDER = [
    "project_id",
    "project_name",
    "sector",
    "pipeline_category",
    "estimated_value_code",
    "estimated_value_band",
    "value_minimum_aud_m",
    "value_maximum_aud_m",
    "procurement_strategy_code",
    "procurement_strategy_name",
    "current_phase",
    "current_phase_definition",
    "procurement_start_period",
    "procurement_end_period",
    "construction_start_period",
    "construction_end_period",
    "project_url",
]


def validate_input(data):
    """Validate the interim extraction before transformation."""

    missing_columns = REQUIRED_COLUMNS.difference(
        data.columns
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"Missing required columns: {missing_text}"
        )

    if len(data) != 99:
        raise ValueError(
            "Expected 99 source records, "
            f"but found {len(data)}."
        )

    if data["Project name"].isna().any():
        raise ValueError(
            "One or more records have a missing project name."
        )

    invalid_sectors = data.loc[
        data["Sector"] != "Transport",
        "Sector",
    ].dropna().unique()

    if len(invalid_sectors) > 0:
        invalid_text = ", ".join(
            sorted(invalid_sectors)
        )

        raise ValueError(
            f"Non-Transport records found: {invalid_text}"
        )

    valid_lifecycles = set(
        LIFECYCLE_PRIORITY
    )

    actual_lifecycles = set(
        data["Source Lifecycle"]
        .dropna()
        .unique()
    )

    invalid_lifecycles = (
        actual_lifecycles.difference(
            valid_lifecycles
        )
    )

    if invalid_lifecycles:
        invalid_text = ", ".join(
            sorted(invalid_lifecycles)
        )

        raise ValueError(
            f"Unexpected source lifecycles: {invalid_text}"
        )


def identify_duplicates(data):
    """Return all rows whose project name occurs more than once."""

    duplicate_mask = data.duplicated(
        subset=["Project name"],
        keep=False,
    )

    duplicates = data[
        duplicate_mask
    ].sort_values(
        by=[
            "Project name",
            "Source Lifecycle",
        ]
    )

    return duplicates


def validate_duplicates(duplicates):
    """Confirm that only the reviewed duplicate is present."""

    expected_duplicate_names = {
        "Parramatta Light Rail Stage 2 Main Works"
    }

    actual_duplicate_names = set(
        duplicates["Project name"].unique()
    )

    if actual_duplicate_names != expected_duplicate_names:
        raise ValueError(
            "The duplicate projects differ from the reviewed "
            "source condition. Review them before continuing."
        )


def add_category_priority(data):
    """Prioritise Pipeline over In Planning for duplicate records."""

    data = data.copy()

    data["lifecycle_priority"] = (
        data["Source Lifecycle"]
        .map(LIFECYCLE_PRIORITY)
        .fillna(99)
    )

    return data


def consolidate_projects(data):
    """Create one primary record per unique project."""

    project_register = data.sort_values(
        by=[
            "Project name",
            "lifecycle_priority",
        ]
    )

    project_register = (
        project_register.drop_duplicates(
            subset=["Project name"],
            keep="first",
        )
    )

    project_register = project_register.drop(
        columns=["lifecycle_priority"]
    )

    return project_register


def build_duplicate_log(duplicates):
    """Document the reviewed cross-category duplicate."""

    duplicate_summary = (
        duplicates.groupby("Project name")
        .size()
        .rename("records_found")
        .reset_index()
        .rename(columns={"Project name": "project_name"})
    )

    duplicate_summary.insert(0, "rule_id", "DQ001")

    duplicate_summary["issue"] = (
        "Project appears in both Pipeline and In Planning"
    )

    duplicate_summary["resolution"] = (
        "Retained the Pipeline record because it contains the "
        "more complete phase, procurement and timeline information"
    )

    duplicate_summary["validation_evidence"] = (
        "Infrastructure NSW live In Planning search returned no "
        "matching project on 2026-08-29"
    )

    return duplicate_summary


def standardise_column_names(data):
    """Rename source columns for Python and Tableau."""

    return data.rename(
        columns=COLUMN_NAMES
    )


def decode_reference_values(data):
    """Add readable value, procurement and phase definitions."""

    data = data.copy()

    data["estimated_value_band"] = (
        data["estimated_value_code"]
        .map(
            lambda code: VALUE_BANDS.get(
                code,
                {},
            ).get("label")
        )
    )

    data["value_minimum_aud_m"] = (
        data["estimated_value_code"]
        .map(
            lambda code: VALUE_BANDS.get(
                code,
                {},
            ).get("minimum")
        )
    )

    data["value_maximum_aud_m"] = (
        data["estimated_value_code"]
        .map(
            lambda code: VALUE_BANDS.get(
                code,
                {},
            ).get("maximum")
        )
    )

    data["procurement_strategy_name"] = (
        data["procurement_strategy_code"]
        .map(PROCUREMENT_STRATEGIES)
    )

    data["current_phase_definition"] = (
        data["current_phase"]
        .map(CURRENT_PHASES)
    )

    return data


def add_project_ids(data):
    """Sort the register and generate readable Project IDs."""

    data = data.sort_values(
        by="project_name"
    ).reset_index(drop=True)

    project_ids = [
        f"PRJ-{number:04d}"
        for number in range(
            1,
            len(data) + 1,
        )
    ]

    data.insert(
        0,
        "project_id",
        project_ids,
    )

    return data


def validate_reference_values(data):
    """Detect source codes missing from the lookup dictionaries."""

    unknown_value_codes = data.loc[
        data["estimated_value_code"].notna()
        & data["estimated_value_band"].isna(),
        "estimated_value_code",
    ].unique()

    if len(unknown_value_codes) > 0:
        unknown_text = ", ".join(
            sorted(unknown_value_codes)
        )

        raise ValueError(
            f"Unknown value codes: {unknown_text}"
        )

    unknown_procurement_codes = data.loc[
        data["procurement_strategy_code"].notna()
        & data["procurement_strategy_name"].isna(),
        "procurement_strategy_code",
    ].unique()

    if len(unknown_procurement_codes) > 0:
        unknown_text = ", ".join(
            sorted(unknown_procurement_codes)
        )

        raise ValueError(
            "Unknown procurement strategies: "
            f"{unknown_text}"
        )

    unknown_phases = data.loc[
        data["current_phase"].notna()
        & data["current_phase_definition"].isna(),
        "current_phase",
    ].unique()

    if len(unknown_phases) > 0:
        unknown_text = ", ".join(
            sorted(unknown_phases)
        )

        raise ValueError(
            f"Unknown current phases: {unknown_text}"
        )


def validate_output(data):
    """Validate the final project-register structure."""

    if len(data) != 98:
        raise ValueError(
            "Expected 98 unique projects, "
            f"but found {len(data)}."
        )

    if not data["project_id"].is_unique:
        raise ValueError(
            "Project IDs are not unique."
        )

    if not data["project_name"].is_unique:
        raise ValueError(
            "Project names are not unique."
        )

    if data["project_name"].isna().any():
        raise ValueError(
            "The final register contains a missing project name."
        )


def main():
    """Build the processed Transport project register."""

    data = pd.read_csv(INPUT_FILE)

    validate_input(data)

    duplicates = identify_duplicates(data)

    validate_duplicates(duplicates)

    data = add_category_priority(data)

    project_register = consolidate_projects(data)

    duplicate_log = build_duplicate_log(duplicates)

    project_register = standardise_column_names(
        project_register
    )

    project_register = decode_reference_values(
        project_register
    )

    project_register = add_project_ids(
        project_register
    )

    validate_reference_values(
        project_register
    )

    validate_output(
        project_register
    )

    project_register = project_register[
        FINAL_COLUMN_ORDER
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    project_register.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    VALIDATION_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    duplicate_log.to_csv(
        VALIDATION_OUTPUT_FILE,
        index=False,
    )

    duplicate_project_count = (
        duplicates["Project name"].nunique()
    )

    print(
        f"Input validation passed: {len(data)} records."
    )

    print(
        "Duplicate check passed: "
        f"{len(duplicates)} source rows across "
        f"{duplicate_project_count} project."
    )

    print(
        "Final register created: "
        f"{len(project_register)} unique projects."
    )

    print("Output file:", OUTPUT_FILE)
    print("Validation log:", VALIDATION_OUTPUT_FILE)


if __name__ == "__main__":
    main()
