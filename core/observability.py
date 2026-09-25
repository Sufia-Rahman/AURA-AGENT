import json
import os
import time
import uuid
from datetime import datetime


class Observability:

    def __init__(
        self,
        file_path="aura_traces.json"
    ):

        self.file_path = file_path
        self.traces = self._load()

    def _load(self):

        if not os.path.exists(
            self.file_path
        ):

            return []

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            return (
                data
                if isinstance(data, list)
                else []
            )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []

    def _save(self):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.traces,
                file,
                indent=2,
                ensure_ascii=False
            )

    def start_trace(
        self,
        task
    ):

        trace = {
            "trace_id": str(
                uuid.uuid4()
            ),
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "status": "running",
            "steps": [],
            "total_duration_ms": 0
        }

        self.traces.append(
            trace
        )

        return trace["trace_id"]

    def start_step(
        self,
        trace_id,
        name
    ):

        step = {
            "step_id": str(
                uuid.uuid4()
            ),
            "name": name,
            "status": "running",
            "started_at": time.time()
        }

        trace = self._find_trace(
            trace_id
        )

        if trace:

            trace["steps"].append(
                step
            )

        return step["step_id"]

    def finish_step(
        self,
        trace_id,
        step_id,
        status="success",
        metadata=None
    ):

        trace = self._find_trace(
            trace_id
        )

        if not trace:

            return

        for step in trace["steps"]:

            if step["step_id"] != step_id:

                continue

            duration = (
                time.time()
                - step["started_at"]
            )

            step["duration_ms"] = round(
                duration * 1000,
                2
            )

            step["status"] = status

            step.pop(
                "started_at",
                None
            )

            if metadata:

                step["metadata"] = metadata

            break

    def finish_trace(
        self,
        trace_id,
        status="success"
    ):

        trace = self._find_trace(
            trace_id
        )

        if not trace:

            return

        started_at = datetime.fromisoformat(
            trace["timestamp"]
        )

        duration = (
            datetime.now()
            - started_at
        ).total_seconds()

        trace["total_duration_ms"] = round(
            duration * 1000,
            2
        )

        trace["status"] = status

        self._save()

    def _find_trace(
        self,
        trace_id
    ):

        for trace in self.traces:

            if trace["trace_id"] == trace_id:

                return trace

        return None

    def recent(
        self,
        limit=10
    ):

        return self.traces[-limit:]

    def statistics(self):

        if not self.traces:

            return {
                "traces": 0,
                "successful": 0,
                "failed": 0,
                "average_duration_ms": 0
            }

        successful = sum(
            1
            for trace in self.traces
            if trace["status"]
            == "success"
        )

        failed = sum(
            1
            for trace in self.traces
            if trace["status"]
            == "failed"
        )

        durations = [
            trace.get(
                "total_duration_ms",
                0
            )
            for trace in self.traces
        ]

        return {
            "traces": len(
                self.traces
            ),
            "successful": successful,
            "failed": failed,
            "average_duration_ms": round(
                sum(durations)
                / len(durations),
                2
            )
        }