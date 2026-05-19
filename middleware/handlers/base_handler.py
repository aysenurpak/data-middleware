from abc import ABC, abstractmethod
from typing import Optional

class BaseHandler(ABC):
    """
    Chain of Responsibility - Soyut Temel Handler
    Her handler bir sonrakini çağırabilir.
    """

    def __init__(self):
        self._next_handler: Optional["BaseHandler"] = None

    def set_next(self, handler: "BaseHandler") -> "BaseHandler":
        """Zincirdeki bir sonraki halkayı bağlar."""
        self._next_handler = handler
        return handler  # Zincirleme yazım için handler döndür

    def handle(self, log: dict) -> dict:
        """
        Kendi işini yap, sonra zinciri devam ettir.
        Alt sınıflar process() metodunu override eder.
        """
        log = self.process(log)

        if self._next_handler:
            return self._next_handler.handle(log)

        return log

    @abstractmethod
    def process(self, log: dict) -> dict:
        """Her handler kendi işini burada tanımlar."""
        pass