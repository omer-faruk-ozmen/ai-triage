from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T):
        pass

    @abstractmethod
    def get(self, entity_id: int) -> T:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def update(self, entity: T):
        pass

    @abstractmethod
    def delete(self, entity_id: int):
        pass
