"""Unit tests for Continuous Monitoring & Degradation Detection."""

import os
import pytest
from monitoring.models import MonitoringTarget
from monitoring.scheduler import MonitoringScheduler
from storage.database import (
    delete_monitoring_target,
    get_monitoring_history,
    get_monitoring_targets,
    init_db,
    save_monitoring_target,
)


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_nta.db")
    init_db(db_file)
    return db_file


def test_monitoring_target_crud(temp_db):
    target = MonitoringTarget(
        name="Test Target",
        host="127.0.0.1",
        port=80,
        service_type="http",
        interval_seconds=30
    )
    save_monitoring_target(target, db_path=temp_db)

    retrieved = get_monitoring_targets(db_path=temp_db)
    assert len(retrieved) == 1
    assert retrieved[0].name == "Test Target"
    assert retrieved[0].interval_seconds == 30

    delete_monitoring_target(target.target_id, db_path=temp_db)
    assert len(get_monitoring_targets(db_path=temp_db)) == 0


def test_monitoring_check_execution(temp_db):
    scheduler = MonitoringScheduler(db_path=temp_db)
    target = MonitoringTarget(
        name="Loopback Test",
        host="127.0.0.1",
        port=65432,
        service_type="tcp",
        interval_seconds=10
    )
    save_monitoring_target(target, db_path=temp_db)

    check_record = scheduler.execute_check(target)
    assert check_record.target_id == target.target_id
    assert check_record.status in ("DOWN", "DEGRADED", "HEALTHY")

    history = get_monitoring_history(target_id=target.target_id, db_path=temp_db)
    assert len(history) == 1
