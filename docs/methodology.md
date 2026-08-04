# Methodology

## Deterministic simulation and events

YAML is validated into regional dataclasses. The one-month engine calculates explicit flows and
schedules typed events at integer times. A heap orders by `(time, insertion sequence)`, so events at
the same time remain in insertion order. A fresh scenario produces byte-for-byte stable reports.

## Flow and reconciliation

External household income first separates into housing, local customer spending, nonlocal spending,
and retention. Visitor category spending joins household customer spending as sector revenue.
Revenue then becomes taxes, wages, local purchases, external purchases, or business retention.

Cash balances are amounts held at a point; transaction flows move during the month. Revenue is the
customer flow received by businesses, income is an inflow to a receiving unit, and modeled activity
counts the unique customer transaction once. Reconciliation compares external sources with final
classified uses. It never equates revenue with money remaining locally.

This small accounting experiment is not an input-output model, official impact estimate, or
forecast. It deliberately excludes machine learning, stochastic methods, and calibration so a
reader can trace every cent and understand every assumption.

