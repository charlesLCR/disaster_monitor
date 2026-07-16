"""
Web 与主循环共享的运行时状态（电机实例、最新传感器快照）。
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, Optional

motor_lock = threading.Lock()
_motor = None
_sensor_snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None
_latest_sensors: Dict[str, Any] = {}
_sensors_lock = threading.Lock()


def attach_hardware(motor, sensor_snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None) -> None:
    global _motor, _sensor_snapshot_fn
    _motor = motor
    _sensor_snapshot_fn = sensor_snapshot_fn


def get_motor():
    return _motor


def update_sensor_snapshot(data: Dict[str, Any]) -> None:
    with _sensors_lock:
        _latest_sensors.clear()
        _latest_sensors.update(data or {})


def get_sensor_snapshot() -> Dict[str, Any]:
    if _sensor_snapshot_fn is not None:
        try:
            return _sensor_snapshot_fn() or {}
        except Exception as exc:
            return {"error": str(exc)}
    with _sensors_lock:
        return dict(_latest_sensors)
