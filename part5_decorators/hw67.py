import datetime
import json
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func: CallableWithMeta[P, R_co], block_time: datetime.datetime):
        super().__init__(TOO_MUCH)
        self.func_name = f"{func.__module__}.{func.__name__}"
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 3,
        triggers_on: type[Exception] = Exception,
    ):
        errors = []

        if critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        if time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.count_of_exceptions = 0
        self.block_time: datetime.datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) ->  R_co:
            self._check_state(func)
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as exception:
                self._handle_failure(func, exception)
            else:
                self._reset_state()
            return result

        return wrapper

    def _check_state(self, func: CallableWithMeta[P, R_co]) -> None:
        if self.block_time is None:
            return
        current_time = datetime.datetime.now(datetime.UTC)
        if (current_time - self.block_time).total_seconds() < self.time_to_recover:
            raise BreakerError(func, self.block_time)
        self._reset_state()

    def _handle_failure(self, func: CallableWithMeta[P, R_co], exception: Exception) -> None:
        self.count_of_exceptions += 1
        if self.count_of_exceptions >= self.critical_count:
            self.block_time = datetime.datetime.now(datetime.UTC)
            raise BreakerError(func, self.block_time) from exception
        raise exception

    def _reset_state(self) -> None:
        self.block_time = None
        self.count_of_exceptions = 0


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
