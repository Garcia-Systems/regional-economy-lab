"""Safe, deterministic fixtures for the textbook debugging laboratories.

This module is deliberately separate from the simulation engine.  Learners may inspect
or repair its opt-in faulty observation without changing production economics.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StageIdentityObservation:
    configured_demand: int
    recorded_business_revenue: int
    constrained_amount: int
    identity_holds: bool


def inspect_stage_identity(faulty: bool = True) -> StageIdentityObservation:
    """Return an intentionally faulty or corrected transaction-stage identity."""
    configured_demand = 10_000
    constrained_amount = 2_500
    recorded_business_revenue = 8_000 if faulty else 7_500
    return StageIdentityObservation(
        configured_demand,
        recorded_business_revenue,
        constrained_amount,
        configured_demand == recorded_business_revenue + constrained_amount,
    )


def main() -> None:
    """Debugger entry point: compare the opt-in faulty and corrected observations."""
    faulty = inspect_stage_identity(faulty=True)
    corrected = inspect_stage_identity(faulty=False)
    print(f"faulty={faulty}")
    print(f"corrected={corrected}")


if __name__ == "__main__":
    main()
