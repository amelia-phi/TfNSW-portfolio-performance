"""Configuration and reference mappings for the project register."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "infrastructure_pipeline_transport_raw.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "project_register.csv"
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
    "$": {"label": "$50M to $100M", "minimum": 50, "maximum": 100},
    "$$": {"label": "$100M to $250M", "minimum": 100, "maximum": 250},
    "$$$": {"label": "$250M to $500M", "minimum": 250, "maximum": 500},
    "$$$$": {"label": "$500M to $1B", "minimum": 500, "maximum": 1000},
    "$$$$$": {"label": "Over $1B", "minimum": 1000, "maximum": None},
    "TBA": {"label": "To be advised", "minimum": None, "maximum": None},
    "TBC": {"label": "To be confirmed", "minimum": None, "maximum": None},
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
    "Strategic Planning": "Preparation and approval of strategic business case",
    "Final Business Case": "Preparation and approval of final business case",
    "Design": "Preparation and approval of project design",
    "Construction Procurement": (
        "Preparation, approval and release of procurement documents"
    ),
    "Rolling Program": "Rolling program with ongoing procurement and delivery",
}

COLUMN_NAMES = {
    "Sector": "sector",
    "Project name": "project_name",
    "Estimated Value": "estimated_value_code",
    "Procurement Strategy": "procurement_strategy_code",
    "Current Phase": "current_phase",
    "Procurement Start Date (est.)": "procurement_start_period",
    "Procurement End Date (est.)": "procurement_end_period",
    "Construction Start Date (est.)": "construction_start_period",
    "Construction End Date (est.)": "construction_end_period",
    "Project Link": "project_url",
    "Source Lifecycle": "pipeline_category",
}

FINAL_COLUMN_ORDER = (
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
)

EXPECTED_SOURCE_RECORDS = 99
EXPECTED_PROJECTS = 98
EXPECTED_DUPLICATE_NAMES = {"Parramatta Light Rail Stage 2 Main Works"}
