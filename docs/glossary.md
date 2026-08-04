# Glossary

- **External income:** money entering the modeled boundary from outside.
- **Local spending:** customer spending received by a modeled regional business.
- **Leakage:** a modeled payment leaving the boundary: external housing, nonlocal household
  spending, or external business purchasing.
- **Business revenue:** customer transaction flow recorded by a business, not its ending balance.
- **Wages:** a business use of operating revenue paid for labor.
- **Taxes:** modeled sales and lodging amounts collected by local government.
- **Retained funds:** cash not spent during this time step.
- **Simulated local economic activity:** unique modeled customer transactions, equal here to
  business revenue and explicitly not GDP.
- **Scenario:** a validated YAML set of entities and assumptions.
- **Deterministic simulation:** a run with no randomness whose identical inputs yield identical output.
- **Event:** a typed, integer-time record in the inspectable timeline.
- **Reconciliation:** proof that classified final uses equal external sources.

- **External household income:** household funds originating outside the modeled boundary, recorded once at entry.
- **Visitor spending:** fictional external customer payments allocated by sector.
- **Local household spending:** household customer payments received by modeled businesses.
- **Household leakage:** household nonlocal spending; housing is separately shown as an externally paid cost.
- **Business external purchases:** business input payments leaving the boundary.
- **Economic leakage:** housing costs + household nonlocal spending + business external purchases, each counted once.
- **Wages paid:** an after-tax business-revenue use; wages do not recirculate in v0.1.0.
- **Taxes collected:** tax-inclusive sales and lodging amounts remitted by businesses and retained by modeled government.
- **Retained household funds:** household funds not spent during the month.
- **Retained business funds:** after-tax business revenue not allocated to wages or purchases.
- **Event timeline:** deterministic, integer-time ordering of the month's modeled steps.
