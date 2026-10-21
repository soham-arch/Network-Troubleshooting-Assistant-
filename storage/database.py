"""SQLite Database connection, schema migrations and repository pattern."""

import json
import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional

from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticRecommendation,
    DiagnosticSession,
    DiagnosticStage,
    RootCauseHypothesis,
    TestResult,
    TestStatus,
    VerificationOutcome,
)
from monitoring.models import (
    AlertNotification,
    MonitoringCheckRecord,
    MonitoringTarget,
)

logger = logging.getLogger(__name__)


def get_db_connection(db_path: str = "data/nta.db") -> sqlite3.Connection:
    """Safely connects to SQLite database, ensuring directory exists."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = "data/nta.db") -> None:
    """Initializes tables and indexes for Diagnostic Sessions and Evaluations."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                user_symptom TEXT NOT NULL,
                target_host TEXT,
                target_port INTEGER,
                service_type TEXT,
                is_simulated INTEGER NOT NULL DEFAULT 0,
                simulation_scenario_id TEXT,
                raw_json TEXT NOT NULL,
                top_hypothesis TEXT,
                top_confidence TEXT,
                verification_outcome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_evaluations (
                eval_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                expected_cause TEXT NOT NULL,
                predicted_cause TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                duration_seconds REAL,
                tests_executed INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(start_time DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_sim ON sessions(is_simulated)")

        # Continuous Monitoring Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_targets (
                target_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER DEFAULT 443,
                service_type TEXT DEFAULT 'https',
                interval_seconds INTEGER DEFAULT 60,
                enabled INTEGER DEFAULT 1,
                latency_threshold_ms REAL DEFAULT 150.0,
                packet_loss_threshold_pct REAL DEFAULT 5.0,
                alert_email TEXT,
                alert_slack_webhook TEXT,
                alert_generic_webhook TEXT,
                last_run TEXT,
                current_status TEXT DEFAULT 'UNKNOWN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_checks (
                check_id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                latency_ms REAL,
                packet_loss_pct REAL DEFAULT 0.0,
                session_id TEXT,
                summary TEXT,
                FOREIGN KEY (target_id) REFERENCES monitoring_targets (target_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                alert_id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                target_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                alert_channel TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checks_target ON monitoring_checks(target_id, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_time ON monitoring_alerts(timestamp DESC)")
        conn.commit()


def save_session(session: DiagnosticSession, db_path: str = "data/nta.db") -> None:
    """Saves or updates a diagnostic session in the database."""
    init_db(db_path)
    top_hypo = session.hypotheses[0].probable_root_cause if session.hypotheses else "None"
    top_conf = session.hypotheses[0].confidence.value if session.hypotheses else "LOW"
    verif = session.verification_outcome.value if session.verification_outcome else None

    raw_json = session.model_dump_json()

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (
                session_id, start_time, end_time, user_symptom,
                target_host, target_port, service_type,
                is_simulated, simulation_scenario_id, raw_json,
                top_hypothesis, top_confidence, verification_outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                end_time = excluded.end_time,
                raw_json = excluded.raw_json,
                top_hypothesis = excluded.top_hypothesis,
                top_confidence = excluded.top_confidence,
                verification_outcome = excluded.verification_outcome
        """, (
            session.session_id,
            session.start_time,
            session.end_time,
            session.user_symptom,
            session.target_host,
            session.target_port,
            session.service_type,
            1 if session.is_simulated else 0,
            session.simulation_scenario_id,
            raw_json,
            top_hypo,
            top_conf,
            verif
        ))
        conn.commit()


def get_session(session_id: str, db_path: str = "data/nta.db") -> Optional[DiagnosticSession]:
    """Retrieves a single session by its unique ID."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT raw_json FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DiagnosticSession.model_validate_json(row["raw_json"])


def list_sessions(
    limit: int = 50,
    is_simulated: Optional[bool] = None,
    search_query: Optional[str] = None,
    db_path: str = "data/nta.db"
) -> List[Dict[str, Any]]:
    """Lists sessions with summaries for UI history tables."""
    init_db(db_path)
    query = """
        SELECT session_id, start_time, end_time, user_symptom, target_host,
               target_port, is_simulated, simulation_scenario_id,
               top_hypothesis, top_confidence, verification_outcome
        FROM sessions
        WHERE 1=1
    """
    params: List[Any] = []

    if is_simulated is not None:
        query += " AND is_simulated = ?"
        params.append(1 if is_simulated else 0)

    if search_query:
        query += " AND (user_symptom LIKE ? OR target_host LIKE ? OR top_hypothesis LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY start_time DESC LIMIT ?"
    params.append(limit)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_session(session_id: str, db_path: str = "data/nta.db") -> bool:
    """Deletes an individual session by ID."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_sessions(db_path: str = "data/nta.db") -> None:
    """Wipes all sessions and evaluations cleanly."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM simulation_evaluations")
        cursor.execute("DELETE FROM sessions")
        conn.commit()


def record_evaluation(
    eval_id: str,
    session_id: str,
    scenario_id: str,
    expected_cause: str,
    predicted_cause: str,
    is_correct: bool,
    duration_seconds: float,
    tests_executed: int,
    timestamp: str,
    db_path: str = "data/nta.db"
) -> None:
    """Records an automated or user simulation run for evaluation metrics."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO simulation_evaluations (
                eval_id, session_id, scenario_id, expected_cause,
                predicted_cause, is_correct, duration_seconds,
                tests_executed, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            eval_id, session_id, scenario_id, expected_cause,
            predicted_cause, 1 if is_correct else 0, duration_seconds,
            tests_executed, timestamp
        ))
        conn.commit()


def get_evaluation_metrics(db_path: str = "data/nta.db") -> Dict[str, Any]:
    """Computes evaluation accuracy, confusion counts, average run durations, etc."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM simulation_evaluations ORDER BY timestamp DESC")
        rows = [dict(r) for r in cursor.fetchall()]

    total = len(rows)
    if total == 0:
        return {
            "total_runs": 0,
            "correct_runs": 0,
            "accuracy": 0.0,
            "avg_duration": 0.0,
            "avg_tests": 0.0,
            "category_breakdown": {},
            "recent_records": []
        }

    correct = sum(1 for r in rows if r["is_correct"] == 1)
    accuracy = round((correct / total) * 100, 1)
    avg_duration = round(sum(r["duration_seconds"] for r in rows) / total, 2)
    avg_tests = round(sum(r["tests_executed"] for r in rows) / total, 1)

    # Breakdown by scenario
    categories: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        scen = r["scenario_id"]
        if scen not in categories:
            categories[scen] = {"total": 0, "correct": 0, "expected": r["expected_cause"]}
        categories[scen]["total"] += 1
        if r["is_correct"] == 1:
            categories[scen]["correct"] += 1

    return {
        "total_runs": total,
        "correct_runs": correct,
        "accuracy": accuracy,
        "avg_duration": avg_duration,
        "avg_tests": avg_tests,
        "category_breakdown": categories,
        "recent_records": rows[:20]
    }


def save_monitoring_target(target: MonitoringTarget, db_path: str = "data/nta.db") -> None:
    """Saves or updates a continuous monitoring target."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO monitoring_targets (
                target_id, name, host, port, service_type,
                interval_seconds, enabled, latency_threshold_ms,
                packet_loss_threshold_pct, alert_email, alert_slack_webhook,
                alert_generic_webhook, last_run, current_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(target_id) DO UPDATE SET
                name = excluded.name,
                host = excluded.host,
                port = excluded.port,
                service_type = excluded.service_type,
                interval_seconds = excluded.interval_seconds,
                enabled = excluded.enabled,
                latency_threshold_ms = excluded.latency_threshold_ms,
                packet_loss_threshold_pct = excluded.packet_loss_threshold_pct,
                alert_email = excluded.alert_email,
                alert_slack_webhook = excluded.alert_slack_webhook,
                alert_generic_webhook = excluded.alert_generic_webhook,
                last_run = excluded.last_run,
                current_status = excluded.current_status
        """, (
            target.target_id, target.name, target.host, target.port, target.service_type,
            target.interval_seconds, 1 if target.enabled else 0, target.latency_threshold_ms,
            target.packet_loss_threshold_pct, target.alert_email, target.alert_slack_webhook,
            target.alert_generic_webhook, target.last_run, target.current_status
        ))
        conn.commit()


def get_monitoring_targets(enabled_only: bool = False, db_path: str = "data/nta.db") -> List[MonitoringTarget]:
    """Retrieves all monitored targets from SQLite."""
    init_db(db_path)
    query = "SELECT * FROM monitoring_targets"
    params: List[Any] = []
    if enabled_only:
        query += " WHERE enabled = 1"
    query += " ORDER BY name ASC"

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        targets = []
        for r in rows:
            d = dict(r)
            d["enabled"] = bool(d["enabled"])
            targets.append(MonitoringTarget(**d))
        return targets


def delete_monitoring_target(target_id: str, db_path: str = "data/nta.db") -> bool:
    """Deletes a monitored target and associated history."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM monitoring_checks WHERE target_id = ?", (target_id,))
        cursor.execute("DELETE FROM monitoring_targets WHERE target_id = ?", (target_id,))
        conn.commit()
        return cursor.rowcount > 0


def update_target_status(target_id: str, status: str, last_run: str, db_path: str = "data/nta.db") -> None:
    """Updates status and last execution timestamp of a monitoring target."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE monitoring_targets
            SET current_status = ?, last_run = ?
            WHERE target_id = ?
        """, (status, last_run, target_id))
        conn.commit()


def save_monitoring_check(record: MonitoringCheckRecord, db_path: str = "data/nta.db") -> None:
    """Records an individual monitoring run in the telemetry history."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO monitoring_checks (
                check_id, target_id, timestamp, status,
                latency_ms, packet_loss_pct, session_id, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.check_id, record.target_id, record.timestamp, record.status,
            record.latency_ms, record.packet_loss_pct, record.session_id, record.summary
        ))
        conn.commit()


def get_monitoring_history(target_id: Optional[str] = None, limit: int = 100, db_path: str = "data/nta.db") -> List[Dict[str, Any]]:
    """Retrieves check telemetry records for a target or all targets."""
    init_db(db_path)
    query = """
        SELECT c.*, t.name as target_name, t.host
        FROM monitoring_checks c
        LEFT JOIN monitoring_targets t ON c.target_id = t.target_id
    """
    params: List[Any] = []
    if target_id:
        query += " WHERE c.target_id = ?"
        params.append(target_id)
    query += " ORDER BY c.timestamp DESC LIMIT ?"
    params.append(limit)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def save_monitoring_alert(alert: AlertNotification, db_path: str = "data/nta.db") -> None:
    """Logs an incident alert dispatch."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO monitoring_alerts (
                alert_id, target_id, target_name, timestamp,
                alert_channel, status, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id, alert.target_id, alert.target_name, alert.timestamp,
            alert.alert_channel, alert.status, alert.message
        ))
        conn.commit()


def get_monitoring_alerts(limit: int = 50, db_path: str = "data/nta.db") -> List[Dict[str, Any]]:
    """Retrieves recent alert logs."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM monitoring_alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

