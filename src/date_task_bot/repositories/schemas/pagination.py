import math
from typing import Generic, TypeVar

from pydantic import BaseModel


class PaginationRequest(BaseModel):
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    page: int
    page_size: int
    total_items: int
    items: list[T]

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total_items / self.page_size)
