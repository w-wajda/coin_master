from abc import (
    ABC,
    abstractmethod,
)


class IEventBus(ABC):
    @abstractmethod
    def send_event(self, event) -> None:
        raise NotImplementedError
