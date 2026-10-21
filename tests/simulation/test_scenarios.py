"""Simulation tests for all 10 predefined scenarios in the Fault Simulation Lab."""

import os
import pytest
from simulation.scenarios import SIMULATION_SCENARIOS, SimulationLabEngine
from storage.database import clear_all_sessions, get_evaluation_metrics, list_sessions


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = str(tmp_path / "test_sim.db")
    yield test_db



def test_all_10_simulation_scenarios(setup_test_db):
    test_db = setup_test_db
    engine = SimulationLabEngine(db_path=test_db)

    assert len(SIMULATION_SCENARIOS) == 10

    correct_predictions = 0

    for scenario in SIMULATION_SCENARIOS:
        session = engine.run_simulation(scenario)

        # Check session integrity
        assert session.is_simulated is True
        assert len(session.test_results) > 0
        assert len(session.hypotheses) > 0

        # Verify predicted title or probable cause matches scenario expected
        top_h = session.hypotheses[0]
        match = (
            scenario.expected_cause.lower() in top_h.probable_root_cause.lower()
            or scenario.expected_cause.lower() in top_h.title.lower()
            or top_h.title.lower() in scenario.expected_cause.lower()
        )
        if match:
            correct_predictions += 1

    # Accuracy must be 100% across the deterministic suite
    assert correct_predictions == 10

    # Verify evaluations metrics record in database
    metrics = get_evaluation_metrics(db_path=test_db)
    assert metrics["total_runs"] == 10
    assert metrics["correct_runs"] == 10
    assert metrics["accuracy"] == 100.0
