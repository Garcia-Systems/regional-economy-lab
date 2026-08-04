# Regional accounting boundary and reconciliation contract

## Purpose and boundary

This document is the accounting contract for the current release. The modeled regional boundary
includes households, modeled businesses, modeled local government, and explicitly integrated
institutions **only to the extent that their transactions enter the canonical economic-flow
pipeline**. A dashboard value does not enter the boundary merely because it is monetary.

| Participant | Boundary treatment | Current treatment |
|---|---|---|
| Households | Fully inside for monthly cash allocation | Gross cash is allocated; wage receipts are not fed back in the same month. |
| Modeled businesses | Fully inside for demand, revenue, operating allocation, and tax remittance | Local supplier recipients and wage-recipient households are not posted as second entries. |
| Local government | Fully inside for transaction-tax receipt and operating allocation; otherwise partial | Recurring revenue, capital budget, and reserves are aggregate values. Permits/fees proxy government demand. |
| Visitors | External | Completed visitor purchases are external inflows received by businesses; visitor counts are context. |
| University | Partially integrated | Student spending and accessible local procurement enter business demand. Payroll, external funding, and total procurement are descriptive; external procurement is classified canonically. |
| Healthcare institutions | Partially integrated | Accessible local procurement enters business demand. Spending, payroll, funding proxies, and external procurement remain descriptive and are not consolidated. |
| Housing recipients | Destination not modeled | Housing is a completed household cash use, but is neither assumed local nor classified as leakage. |
| Financial institutions | Contextual/descriptive | Payment availability affects completion. Deposits and loans are stocks; available credit is capacity, never income. |
| Local suppliers | Partially integrated | Business local purchasing remains internal, but supplier receipts and subsequent allocations are not modeled. |
| Regional/national/international suppliers | External | Canonical business external procurement leaves the boundary. Institutional omissions are disclosed below. |
| Commuters | Contextual | Accessibility affects labor/demand; commuter wages and household accounts are not posted. |
| External governments/funders | External | Intergovernmental and university funding are configured indicators; they are not all integrated into one sources-and-uses ledger. |

## Monetary vocabulary

* **External inflow** enters the declared boundary from an external participant.
* **Internal transfer** moves between participants represented on the boundary and is not new money.
* **External outflow** is a completed payment to an external participant.
* **Ending position or stock** is held at month end or measured at a point in time.
* **Unmet or interrupted amount** is demand, expense, or capacity that did not complete. It is not
  spending or leakage.
* **Descriptive indicator** is useful monetary context that is not a canonical ledger entry.

`MONETARY_METRICS` in `metrics.py` exposes these classifications, flow/position timing, and
canonical status to code and tests. “Canonical” means used by the current transaction pipeline; it
does not mean that a complete regional ledger exists.

## Monetary metric inventory

All units below are integer USD cents. “R” names an allocation or transfer reconciliation. A flow
is measured during the simulated month; a position is measured at its end. Related fields that are
aliases or stage indicators are retained for compatibility.

| Field / display label | Owner | Class | Source calculation | R | Timing | Status and limitation |
|---|---|---|---|---|---|---|
| `external_household_income` / External household income | Household | External inflow | Gross income × configured external share | No | Flow | Canonical entry indicator; gross income also contains sources not separately identified. |
| `gross_household_income` / Gross household income | Household | External inflow | Sum of cohort gross cash | Cash | Flow | Canonical cash source; currently treated as exogenous, so it is broader than the external-share indicator. |
| `household_deductions` / Deductions outside local-government flow | Household | External outflow | Cohort deductions | Cash | Flow | Destination is mixed/unknown and is not matched to modeled local government. |
| `after_tax_household_income` / After-deduction income | Household | Descriptive | Gross less deductions | No | Flow subtotal | Derived, not an additional inflow. |
| `housing_costs` / Housing payments | Household | Descriptive | Actual priority payment | Cash/required | Flow | Completed cash use; recipient destination is not modeled. |
| `essential_spending`, `discretionary_spending` | Household | Internal transfer | Actual cohort allocations | Cash | Flow | Aggregates include local/nonlocal allocation stages; do not add to business revenue as new activity. |
| `local_household_spending` / Local household demand | Household/business | Internal transfer | Actual local allocation before accessibility/payment adjustment | Customer | Flow | Canonical configured-origin amount, not necessarily completed or served revenue. |
| `household_nonlocal_spending` / Household external outflow | Household | External outflow | Actual “other” allocation | Cash | Flow | Canonical classified outflow. |
| `household_savings`, `retained_household_funds` | Household | Ending position | Named savings and allocation residual | Cash | Position | Not current-period activity. |
| `unmet_essential_expenses` | Household | Unmet amount | Required costs less actual payments | Required | Flow counterfactual | Not a cash use, debt, or leakage. |
| `disposable_income_after_required_expenses` | Household | Descriptive | After-deduction cash less actual housing/essential payments | No | Flow subtotal | Must not be added to activity. |
| `visitor_spending` / Accessible visitor demand | Visitors | External inflow | Configured visitor spending × access × utility factor | Customer | Flow | Enters payment-completed demand after a later payment factor. |
| `demanded_visitor_spending`, `unmet_visitor_demand`, `unmet_visitor_spending` | Visitors | Unmet/descriptive | Tourism subsystem demand/capacity indicators | No | Flow counterfactual | Legacy tourism-stage indicators; not spending or leakage. |
| `tourism_revenue`, `tourism_wages`, `tourism_tax_revenue`, `tourism_leakage` | Tourism | Descriptive | Legacy parallel tourism calculations | No | Flow | Noncanonical views; must not be added to canonical business totals. |
| `business_revenue` / Recorded business revenue | Business | Internal transfer | Capacity- and supply-served sector revenue | Business | Flow | Canonical activity indicator, not total regional activity or GDP. |
| `simulated_local_economic_activity` | Business | Descriptive | Compatibility copy of `business_revenue` | No | Flow | Legacy name; public reports use Recorded business revenue. |
| `household_derived_business_revenue` | Business | Descriptive | Compatibility copy of pre-adjustment local household spending | No | Flow | Name is imprecise and can differ from served household revenue. |
| `wages_paid`, `local_business_purchases` | Business | Internal transfer | Operating allocation | Business | Flow | Receiving household/supplier entries do not recur in this month. |
| `external_business_purchases` | Business | External outflow | Operating allocation after supplier mix | Business | Flow | Canonical business external procurement. |
| `taxes_collected`, `business_tax_outflow`, `government_transaction_tax_inflow` | Business/government | Internal transfer | Sector sales tax plus lodging levy | Business/tax transfer | Flow | Explicit matching sides; tax remains inside the boundary. |
| `retained_business_funds` | Business | Ending position | Operating allocation residual | Business | Position | Not current-period activity. |
| `economic_leakage` / Total classified external outflows | Region | External outflow | Deductions + household nonlocal + business external + university external procurement | No | Flow | Compatibility field; incomplete and excludes housing and healthcare external procurement. |
| `student_spending`, `university_local_procurement` | University/business | Internal transfer | Configured student spending and accessible procurement | Customer | Flow | Canonical business-demand inputs. |
| `university_procurement`, `university_payroll`, `external_university_funding` | University | Descriptive | Institution configuration | No | Flow | Not injected as household income or consolidated funding/use. |
| `university_business_impact`, `university_contribution` | University | Descriptive | Sums of selected university indicators | No | Flow | Not an accounting identity or impact estimate. |
| `healthcare_local_procurement` | Healthcare/business | Internal transfer | Accessible configured local procurement | Customer | Flow | Canonical business-demand input. |
| `healthcare_spending`, `healthcare_payroll`, `healthcare_procurement`, `healthcare_external_procurement`, `healthcare_business_activity` | Healthcare | Descriptive | Institution/cohort configuration and derived sums | No | Flow | Payroll is not injected; external procurement is omitted from canonical outflow total. |
| `government_revenue` | Government | Descriptive | Property tax + permits/fees + transfers + transaction taxes | No | Flow | Mixed external/internal sources; not reconciled to all uses. |
| `government_operating_budget` | Government | Internal transfer | Configured appropriation | Government | Flow | Reconciles only to departmental allocations, not total revenue. |
| `government_capital_budget` | Government | Descriptive | Configured aggregate appropriation | No | Flow | Projects/recipients are not represented. |
| `government_reserve_balance` | Government | Ending position | Starting reserve + revenue − appropriations | No | Position | Not activity. |
| `banking.household_deposits`, `banking.business_deposits`, `banking.total_deposits` | Banking | Ending position | Configured balances and sum | No | Stock | Never inflow or activity. |
| `banking.lending_capacity`, `banking.available_credit` | Banking | Descriptive | Deposit-derived capacity less loans | No | Capacity | Credit capacity is not income or money creation in this model. |
| `banking.business_lending`, `banking.consumer_lending` | Banking | Ending position | Configured outstanding lending | No | Stock | No loan origination cash flow is posted. |
| `completed_transactions` | Payments | Internal transfer | Accessible demand × payment availability | Customer | Flow | Sector-allocated demand, before business capacity/supply service. |
| `interrupted_transactions` | Payments | Interrupted | Intended less completed demand | No | Flow counterfactual | Delayed/uncompleted, not spending or leakage. |
| `utility_constrained_activity`, `supply_constrained_business_activity` | Constraints | Unmet/descriptive | Earlier stage less constrained stage | No | Flow counterfactual | Approximate loss indicators, not cash outflows. |

`BusinessSectorResult` money (`demand`, `capacity`, `revenue`, `payroll`, local/external purchases,
taxes, retained surplus, unmet demand, and excess capacity) supplies the aggregate business rows;
capacity and unmet/excess values are descriptive rather than completed money flows.
`HouseholdAllocation` money supplies the household rows. Decision-report costs/benefits are scenario
comparison descriptors, not ledger entries. `AnnualSummary.household_income`, `tourism_spending`, and
`government_revenue` are sums of the corresponding monthly flows; annual reports do not sum deposits,
credit, or reserves.

## Canonical stages currently implemented

1. Configured household, visitor, institution, and government-proxy demand.
2. Accessibility- and utility-adjusted intended demand.
3. Payment-completed demand (`completed_transactions`); the residual is interrupted.
4. Sector-allocated demand (`business_demand_by_source`).
5. Capacity-served and supply-constrained recorded business revenue.
6. Business operating allocation to wages, local/external purchases, taxes, and retention.
7. Business tax remittance and local-government receipt.
8. Household/business/government ending positions.

Capacity service and supply constraint occur together in `Business.record_and_allocate`; the current
engine does not retain canonical records for every adjacent-stage loss. That is future work.

## Supported reconciliations

### Allocation reconciliations

* Gross household income = deductions + actual housing + actual essential + actual discretionary +
  savings + retained household funds. Unmet expenses are excluded.
* Configured required expenses = actual housing + actual essential + unmet required expenses.
* Payment-completed customer demand = sector-allocated demand. This does **not** assert that all
  demand becomes capacity-served revenue.
* Recorded business revenue = wages + local purchases + external purchases + remitted sales taxes +
  retained operating funds. The lodging levy is an additional business-to-government transfer and
  is not deducted by the sector operating allocator.
* Government operating budget = departmental operating allocations.

### Transfer reconciliations

Business transaction-tax outflow equals the transaction-tax amount recorded by local government.
No wage, local-procurement, or completed-spending transfer check is claimed because the receiving
side is not yet represented as an independent canonical entry at the same stage.

### Regional sources and uses

**Status: NOT YET CONSOLIDATED.** Passing allocation and tax-transfer checks does not prove a
complete regional identity. The CLI treats this disclosed limitation as non-failing while any
implemented allocation or transfer failure remains a runtime failure.

## Classified external outflows and known exclusions

The compatibility field `economic_leakage` now has one narrow public meaning: **total classified
external outflows**, equal to household deductions outside the modeled local-government flow,
household nonlocal spending, business external procurement, and university external procurement.
Housing has an unmodeled destination. Healthcare external procurement and legacy tourism external
purchases are descriptive and omitted. Interrupted payments, unmet demand/expenses, constrained
capacity, deposits, loans, credit, and retained positions are never leakage.

## Roadmap

Canonical transaction-stage records now calculate losses only between adjacent stages. A later
correction should post independently derived receiving entries for additional transfers and then
build a consolidated sources-and-uses ledger. It should preserve this vocabulary rather than
treating descriptive institutional totals as transactions.

## Transaction-stage boundary

Recorded business revenue is the single canonical customer-derived receipt inside the modeled region. It is tax-inclusive: sales tax is extracted from recorded sector revenue, not added on top, before operating revenue is allocated to wages, local purchases, external purchases, and retained operating funds. Lodging tax remains a separate tourism-category calculation pending the tourism accounting correction.

Configured, constrained, interrupted, and unmet demand are counterfactual or unsuccessful transactions, not spending and not external leakage. Only an actual purchase outside the regional boundary is an outflow.

For compatibility, `local_household_spending` and `household_derived_business_revenue` retain their historical meaning of configured household local spending. New source-attributed realized values use the `recorded_*_business_revenue_cents` properties. Likewise, `completed_transactions` means payment-completed demand, while `business_revenue` aliases canonical recorded revenue.
