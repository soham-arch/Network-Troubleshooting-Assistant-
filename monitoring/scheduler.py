"""Background Monitoring Scheduler & Degradation Detector.

Runs bounded diagnostic sweeps periodically for enabled targets, detects
latency degradation / packet loss / service outages, stores historical metrics,
and triggers multi-channel alerts.
"""

from __future__ import annotations

import datetime
import logging
import threading
import time
from typing import Optional

from diagnostics.models import DiagnosticStage, TestStatus
from engine.orchestrator import DiagnosticOrchestrator
from integrations.alerter import alerter
from monitoring.models import MonitoringCheckRecord, MonitoringTarget
from storage.database import (
    get_monitoring_targets,
    save_monitoring_alert,
    save_monitoring_check,
    update_target_status,
)

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """Thread-safe background scheduler for continuous network monitoring."""

    def __init__(self, db_path: str = "data/nta.db"):
        self.db_path = db_path
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Starts background monitoring loop if not already running."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                logger.info("Monitoring scheduler already running.")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="NTAMonitoringDaemon")
            self._thread.start()
            logger.info("Continuous monitoring scheduler daemon started.")

    def stop(self) -> None:
        """Signals background scheduler to gracefully terminate."""
        with self._lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=3.0)
            logger.info("Continuous monitoring scheduler stopped.")

    def is_running(self) -> bool:
        """Returns True if background daemon thread is active."""
        return self._thread is not None and self._thread.is_alive()

    def _run_loop(self) -> None:
        """Periodic background evaluation loop."""
        while not self._stop_event.is_set():
            try:
                targets = get_monitoring_targets(enabled_only=True, db_path=self.db_path)
                now = datetime.datetime.now(datetime.timezone.utc)

                for target in targets:
                    if self._stop_event.is_set():
                        break

                    # Check if target is due for probe
                    is_due = True
                    if target.last_run:
                        try:
                            last_dt = datetime.datetime.fromisoformat(target.last_run)
                            elapsed = (now - last_dt).total_seconds()
                            if elapsed < target.interval_seconds:
                                is_due = False
                        except Exception:
                            pass

                    if is_due:
                        self.execute_check(target)

            except Exception as e:
                logger.error(f"Error in monitoring loop cycle: {e}")

            # Sleep in small slices to remain responsive to stop signal
            for _ in range(5):
                if self._stop_event.is_set():
                    break
                time.sleep(1.0)

    def execute_check(self, target: MonitoringTarget) -> MonitoringCheckRecord:
        """Runs a bounded probe for an individual target, assesses health, and alerts."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        orchestrator = DiagnosticOrchestrator(db_path=self.db_path)

        try:
            session = orchestrator.run_investigation(
                user_symptom=f"Automated probe for {target.name}",
                target_host=target.host,
                target_port=target.port,
                service_type=target.service_type,
                run_traceroute=False
            )

            # Evaluate diagnostic metrics
            has_failed_test = any(t.status in (TestStatus.FAIL, TestStatus.ERROR) for t in session.test_results)
            avg_lat: Optional[float] = None
            loss_pct: float = 0.0

            for t in session.test_results:
                if t.stage == DiagnosticStage.LATENCY:
                    avg_lat = t.measured_values.get("avg_rtt_ms")
                    loss_pct = float(t.measured_values.get("packet_loss_pct", 0.0))

            # Determine new status
            if has_failed_test:
                new_status = "DOWN"
                reason = "Diagnostic tests reported failure or connection refusal."
            elif (avg_lat and avg_lat > target.latency_threshold_ms) or (loss_pct > target.packet_loss_threshold_pct):
                new_status = "DEGRADED"
                reason = (
                    f"Performance threshold exceeded: latency={avg_lat}ms "
                    f"(limit: {target.latency_threshold_ms}ms), packet loss={loss_pct}% "
                    f"(limit: {target.packet_loss_threshold_pct}%)."
                )
            else:
                new_status = "HEALTHY"
                reason = f"Target operational: latency={avg_lat or 'N/A'}ms, loss={loss_pct}%."

            # Alert if status degraded or flipped
            old_status = target.current_status
            if new_status in ("DOWN", "DEGRADED") or (old_status in ("DOWN", "DEGRADED") and new_status == "HEALTHY"):
                if not alerter.should_suppress_alert(target.target_id, new_status):
                    alert_reason = reason if new_status != "HEALTHY" else "Target recovered and is now HEALTHY."
                    notifications = alerter.dispatch_incident_alert(
                        target=target,
                        status=new_status,
                        reason=alert_reason,
                        session_id=session.session_id
                    )
                    for notif in notifications:
                        save_monitoring_alert(notif, db_path=self.db_path)

            # Record telemetry in database
            record = MonitoringCheckRecord(
                target_id=target.target_id,
                timestamp=now_iso,
                status=new_status,
                latency_ms=avg_lat,
                packet_loss_pct=loss_pct,
                session_id=session.session_id,
                summary=reason
            )
            save_monitoring_check(record, db_path=self.db_path)
            update_target_status(target.target_id, new_status, now_iso, db_path=self.db_path)
            target.current_status = new_status
            target.last_run = now_iso
            return record

        except Exception as e:
            logger.error(f"Error checking target {target.name}: {e}")
            record = MonitoringCheckRecord(
                target_id=target.target_id,
                timestamp=now_iso,
                status="DOWN",
                summary=f"Diagnostic probe error: {str(e)}"
            )
            save_monitoring_check(record, db_path=self.db_path)
            update_target_status(target.target_id, "DOWN", now_iso, db_path=self.db_path)
            return record


# Global monitoring scheduler instance
monitoring_scheduler = MonitoringScheduler()
