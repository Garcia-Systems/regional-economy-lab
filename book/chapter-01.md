# Chapter 1 — What Is a Regional Economy?

Around Williamsburg and the Historic Triangle, a visitor may pay for a room, a household may buy
dinner, a shop may pay an employee, and government may collect tax. A **regional economy** is the
connected system formed by those decisions within a chosen boundary—not merely a list of firms.
Our small fictional case makes those connections visible.

Households receive external or wage income, pay housing, shop locally or elsewhere, and retain
funds. Tourism/hospitality, retail, and food-service businesses receive local customer revenue and
use it for wages, purchases, tax, and retention. Visitors bring external spending. Government
collects simplified sales and lodging taxes. **Classified external outflows** identify only the
completed exits currently captured; they are not a complete regional ledger.

```mermaid
flowchart LR
  Outside[Outside income] --> Households
  Visitors --> Businesses
  Households -->|local spending| Businesses
  Households -->|nonlocal + housing| Leakage
  Businesses -->|wages| Workers
  Businesses -->|tax| Government
  Businesses -->|external purchases| Leakage
  Businesses -->|local purchases| LocalSuppliers
```

## Baseline walkthrough

Run `regional-sim baseline`. `MonthStarted` precedes external household income and visitors.
Household allocation then completes; combined household and visitor customer payments become
sector demand; capacity- and supply-served demand becomes recorded business revenue; wages and taxes
follow. `MonthCompleted` reports implemented allocation and transfer checks.
The dashboard distinguishes population context, external inflows, unique customer revenue, later
uses, ending positions, classified external outflows, and recorded business revenue. Revenue is not an ending local cash
balance, and wages are not added to revenue to manufacture a larger activity number.

## Debugging laboratory

Select **Run Baseline Scenario** and break in `run_scenario` at `business.record_and_allocate(...)`. Inspect `household_by_sector`, the
visitor's `spending_by_category`, and `revenue_by_sector`. Verify for each sector that household plus
visitor spending becomes exactly the recorded customer revenue. Step into the business method and
watch that flow split into taxes and operating uses.

## Scenario experiment

Copy `baseline.yml`, change one household sector share while preserving a total of one, and rerun.
Which sector's revenue changes? Does total revenue change? Then raise a visitor category amount
without exceeding capacity. Predict the dashboard before running it.

## Interpretation questions

1. Which agents introduce money and which redistribute it?
2. Why is a wage both a business use and household income in a broader model?
3. Why does this one-month model avoid respending that wage?
4. Why is revenue different from retained operating funds?

## Limitations and summary

Representative groups hide household and firm diversity. There are no prices, inventories,
commuting, housing market, workforce dynamics, multiplier rounds, or forecasts. Yet the experiment
establishes inspectable subsystem allocations and one matched tax transfer. Institutional flows,
housing recipients, suppliers, and financial positions are not consolidated, so regional sources
and uses remain **NOT YET CONSOLIDATED**.


The canonical relationship diagram is [`docs/diagrams/entity-relationships.mmd`](../docs/diagrams/entity-relationships.mmd); the canonical money-flow source is [`docs/diagrams/money-flow.mmd`](../docs/diagrams/money-flow.mmd).

### Complete debugging exercise

1. **Launch configuration:** **Run Baseline Scenario**.
2. **Breakpoint:** `engine.py`, the call `business.record_and_allocate(...)`.
3. **Expected variables:** for the current `business`, `revenue_by_sector[business.sector]` equals
   household sector spending plus visitor category spending; `sales_taxes` is nonnegative.
4. **Question / incorrect behavior to inspect:** temporarily reduce that business's `monthly_capacity` below
   its revenue and observe the capacity error rather than a silent truncation.
5. **Correct behavior:** capacity is at least revenue; stepping into `record_and_allocate` records
   the complete payment and divides after-tax funds into mutually exclusive uses.
6. **Economic importance:** silently dropping demand would understate customer activity and break
   the connection between household/visitor payments and business receipts.

## Auditing a transaction path

The monthly model preserves customer-source identity through a canonical transaction pipeline. A reduction belongs to the single transition where it occurs, preventing the same unrealized demand from being described twice.
