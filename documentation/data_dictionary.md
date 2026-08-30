# Data Dictionary

## Dataset: Project Register

**File:** [`project_register.csv`](../data/processed/project_register.csv)

**Description:**  
A consolidated register of publicly listed NSW Transport infrastructure
projects extracted from the Infrastructure NSW Pipeline workbook.

**Source:**  
[Infrastructure NSW Pipeline](https://www.infrastructure.nsw.gov.au/industry/construction-industry/pipeline-of-projects/)

**Source file:**  
[`Pipeline-28-08-2026.xlsx`](..data/raw/Pipeline-28-08-2026.xlsx)

**Dataset grain:**  
One row per unique Transport infrastructure project.

**Row count:**  
98 projects.

**Primary key:**  
`project_id`

**Source categories:**

- `Pipeline`: projects included in the procurement and delivery pipeline.
- `In Planning`: projects for which the NSW Government has committed to commence planning.

**Important limitation:**  
Fields relating to current phase, procurement strategy and delivery periods
are not published for projects in the `In Planning` category. These values
are therefore blank and should not be interpreted as zero or not applicable.

### Field Definitions

| Field | Type | Description | Source or derived | Nulls allowed |
|---|---|---|---|---|
| `project_id` | Text | Unique project identifier generated for this analysis | Derived | No |
| `project_name` | Text | Published project name | Source | No |
| `sector` | Category | Infrastructure sector; all records are Transport | Source | No |
| `pipeline_category` | Category | Broad Infrastructure NSW category: Pipeline or In Planning | Source/derived from worksheet | No |
| `estimated_value_code` | Category | Published symbolic estimated-value code | Source | No |
| `estimated_value_band` | Category | Readable estimated-value range decoded from the published code | Derived from source definition | No |
| `value_minimum_aud_m` | Number | Lower boundary of the published value range, in AUD millions | Derived | Yes |
| `value_maximum_aud_m` | Number | Upper boundary of the published value range, in AUD millions | Derived | Yes |
| `procurement_strategy_code` | Category | Published procurement-strategy abbreviation | Source | Yes |
| `procurement_strategy_name` | Category | Full procurement-strategy name | Derived from source definition | Yes |
| `current_phase` | Category | Published current project phase | Source | Yes |
| `current_phase_definition` | Text | Official description of the published current phase | Derived from source definition | Yes |
| `procurement_start_period` | Text | Estimated start period for construction procurement of main works | Source | Yes |
| `procurement_end_period` | Text | Estimated end period for construction procurement of main works | Source | Yes |
| `construction_start_period` | Text | Estimated construction start period for main works | Source | Yes |
| `construction_end_period` | Text | Estimated construction end period for main works | Source | Yes |
| `project_url` | URL | Published webpage associated with the project | Source | No |