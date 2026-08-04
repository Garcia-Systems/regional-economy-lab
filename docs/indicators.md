# Indicator and reporting reference

This is the authoritative human-readable reference for report vocabulary. The executable authority is
`regional_economy.indicators`; dashboards and other reports reference it rather than copying definitions.

## Contract

Keys use `<subsystem>.<specific_metric>` (for example `business.recorded_revenue`). Keys are stable identifiers;
labels may only be changed centrally. Each definition declares units, accounting classification, precision,
comparison semantics, annual aggregation, direction where meaningful, a calculation note, and limitations.
Money is stored as integer USD cents and displayed with two decimal places. Rates are `Decimal` fractions and are
displayed as percentages without binary-float conversion.

Comparisons are alternative minus baseline. Currency and counts use absolute differences; rates use percentage-point
differences; indexes use index-point differences; relative percentage changes are used only when a definition opts in;
statuses show a transition. Positive changes have `+`; negative money uses `-$1.00`; negative zero is suppressed.

Annual aggregation is metadata-driven: flows are summed, stocks use month-end or an explicitly declared average,
rates use an explicitly declared average/minimum/maximum, and statuses are not summed. `NOT APPLICABLE`, `NOT
MODELED`, `UNAVAILABLE`, and `NOT YET CONSOLIDATED` are distinct from numeric zero.

## Sections and width

The deterministic section order is Overview, Transaction Pipeline, Households, Tourism, Institutions, Businesses,
Government, Housing, Workforce, Transportation, Utilities, Banking, Supply Chains, Shocks and Recovery, Resilience,
Reconciliation, and Assumptions and Limitations. Reports omit irrelevant placeholders. Terminal output targets 100
columns and uses vertical comparison layouts when four-column tables would be too wide.

## Exports

Dashboard CSV uses:

`scenario,month,section,indicator_key,label,value,formatted_value,units,note,type`

`value` remains machine-readable. Spreadsheet-facing text beginning with `=`, `+`, `-`, or `@` is prefixed with an
apostrophe; numeric raw-value cells are unchanged. This is a limited spreadsheet formula-interpretation mitigation,
not a general security boundary. Markdown uses stable headings, canonical keys and labels, explicit units, and no
terminal padding.

All reports use this notice once: **Educational simulation using fictional and assumed values; not an official
forecast.**

## Current catalog

Run Python to inspect the non-duplicated catalog:

```python
from regional_economy.indicators import INDICATORS
for key, definition in INDICATORS.items():
    print(key, definition.label, definition.units, definition.classification, definition.annual_aggregation)
```
