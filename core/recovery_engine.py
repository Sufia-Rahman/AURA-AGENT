import time

from .fallback_engine import FallbackEngine


class RecoveryEngine:

    def __init__(
        self,
        max_retries=2,
        retry_delay=1.0,
        fallback_engine=None
    ):

        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.fallback_engine = (
            fallback_engine
            or FallbackEngine()
        )

        self.total_operations = 0
        self.total_retries = 0
        self.total_recoveries = 0
        self.total_failures = 0

    def classify_error(self, error):

        error_text = str(
            error
        ).lower()

        non_retryable_patterns = [
            "credit_balance_exhausted",
            "insufficient_quota",
            "billing",
            "invalid api key",
            "authentication",
            "permission denied",
            "invalid request",
            "bad request",
            "not found"
        ]

        if any(
            pattern in error_text
            for pattern in non_retryable_patterns
        ):
            return "non_retryable"

        retryable_patterns = [
            "timeout",
            "timed out",
            "connection",
            "connection reset",
            "temporarily unavailable",
            "rate limit",
            "429",
            "500",
            "502",
            "503",
            "504",
            "server error"
        ]

        if any(
            pattern in error_text
            for pattern in retryable_patterns
        ):
            return "retryable"

        return "unknown"

    def is_retryable(self, error):

        return (
            self.classify_error(error)
            == "retryable"
        )

    def _wait_before_retry(self, attempt):

        delay = (
            self.retry_delay
            * (2 ** (attempt - 1))
        )

        time.sleep(delay)

    def execute(
        self,
        operation,
        operation_name="unknown",
        fallback=None
    ):

        self.total_operations += 1

        attempts = 0
        last_error = None

        while attempts <= self.max_retries:

            try:

                result = operation()

                return {
                    "status": "success",
                    "result": result,
                    "attempts": attempts + 1,
                    "recovered": attempts > 0,
                    "recovery_strategy": (
                        "retry"
                        if attempts > 0
                        else "none"
                    ),
                    "operation": operation_name
                }

            except Exception as error:

                last_error = error

                error_type = (
                    self.classify_error(
                        error
                    )
                )

                attempts += 1

                if error_type != "retryable":
                    break

                if attempts > self.max_retries:
                    break

                self.total_retries += 1

                self._wait_before_retry(
                    attempts
                )

        fallback_info = (
            self.fallback_engine.select(
                operation=operation_name,
                failed_attempts=attempts
            )
        )

        if fallback:

            try:

                result = fallback()

                self.total_recoveries += 1

                return {
                    "status": "fallback_success",
                    "result": result,
                    "attempts": attempts,
                    "recovered": True,
                    "recovery_strategy": "fallback",
                    "fallback": fallback_info,
                    "operation": operation_name
                }

            except Exception as fallback_error:

                self.total_failures += 1

                return {
                    "status": "failed",
                    "result": None,
                    "attempts": attempts,
                    "recovered": False,
                    "recovery_strategy":
                        "fallback_failed",
                    "fallback": fallback_info,
                    "operation": operation_name,
                    "error": str(
                        fallback_error
                    ),
                    "original_error": str(
                        last_error
                    )
                }

        self.total_failures += 1

        return {
            "status": "failed",
            "result": None,
            "attempts": attempts,
            "recovered": False,
            "recovery_strategy": "exhausted",
            "fallback": fallback_info,
            "operation": operation_name,
            "error": str(last_error)
        }

    def statistics(self):

        return {
            "max_retries":
                self.max_retries,

            "retry_delay":
                self.retry_delay,

            "total_operations":
                self.total_operations,

            "total_retries":
                self.total_retries,

            "total_recoveries":
                self.total_recoveries,

            "total_failures":
                self.total_failures,

            "fallback":
                self.fallback_engine.statistics()
        }