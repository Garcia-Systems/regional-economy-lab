from decimal import Decimal

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.entities import BankingSystem
from regional_economy.reporting import banking_report, banking_trace, comparison
from regional_economy.scenarios import load_scenario


def test_deposits_lending_capacity_and_available_credit():
    result = BankingSystem(2, 2_000_00, 1_000_00, Decimal("0.80"), 100_00, 50_00, Decimal("1"), Decimal("0.99")).evaluate()
    assert result.total_deposits == 3_000_00
    assert result.lending_capacity == 2_400_00
    assert result.available_credit == 2_250_00


def test_payment_outage_interrupts_but_does_not_duplicate_activity():
    baseline = run_scenario(load_scenario("baseline"))
    outage = run_scenario(load_scenario("payment-outage"))
    assert outage.metrics.banking.payment_availability == Decimal("0.65")
    assert outage.metrics.completed_transactions < baseline.metrics.completed_transactions
    assert outage.metrics.interrupted_transactions > 0
    assert outage.metrics.completed_transactions + outage.metrics.interrupted_transactions == baseline.metrics.completed_transactions
    assert outage.metrics.sector_transactions.allocated.total_cents == outage.metrics.completed_transactions
    assert outage.metrics.business_revenue <= outage.metrics.completed_transactions


def test_banking_scenarios_reports_comparison_and_cli_are_deterministic(capsys):
    for name in ("payment-outage", "credit-tightening", "expanded-business-lending"):
        assert run_scenario(load_scenario(name)) == run_scenario(load_scenario(name))
        assert main([name]) == 0
        assert name in capsys.readouterr().out
    baseline = run_scenario(load_scenario("baseline"))
    outage = run_scenario(load_scenario("payment-outage"))
    assert "Interrupted activity:" in banking_report(outage)
    assert "Completed transactions" in comparison(baseline, outage)
    assert "not payment-network mechanics" in banking_trace(baseline)
    assert main(["banking-report", "baseline"]) == 0
    assert "BANKING REPORT" in capsys.readouterr().out
