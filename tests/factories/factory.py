from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TypeVar, cast, overload

from pydantic import BaseModel

FieldsT = TypeVar("FieldsT")
SchemaT = TypeVar("SchemaT", bound=BaseModel)
OrmT = TypeVar("OrmT")


class AbstractFactory[FieldsT, SchemaT, OrmT](ABC):
    model_for_validation: type[BaseModel] | None = None

    def __init__(
        self, insert_async_func: Callable[[OrmT], Awaitable[OrmT]] | None = None
    ) -> None:
        self.insert_async_func = insert_async_func

    @abstractmethod
    def make_schema(self, fields: FieldsT | None = None) -> SchemaT:
        pass

    @abstractmethod
    def schema_to_orm(self, schema: SchemaT) -> OrmT:
        pass

    def make_orm(self, fields: FieldsT) -> OrmT:
        schema = self.make_schema(fields)
        return self.schema_to_orm(schema)

    @overload
    async def insert_to_database(
        self,
        fields: FieldsT,
        validate: bool = False,
        insert_async_func: Callable[[OrmT], Awaitable[OrmT]] | None = None,
    ) -> OrmT: ...

    @overload
    async def insert_to_database(
        self,
        fields: FieldsT,
        validate: bool = True,
        insert_async_func: Callable[[OrmT], Awaitable[OrmT]] | None = None,
    ) -> SchemaT: ...

    async def insert_to_database(
        self,
        fields: FieldsT,
        validate: bool = True,
        insert_async_func: Callable[[OrmT], Awaitable[OrmT]] | None = None,
    ) -> OrmT | SchemaT:
        orm = self.make_orm(fields)
        if insert_async_func:
            insert = insert_async_func
        elif self.insert_async_func:
            insert = self.insert_async_func
        else:
            raise ValueError("No insert async function passed")
        if validate:
            if not self.model_for_validation:
                raise ValueError("No model to validate")
            return cast(
                SchemaT, self.model_for_validation.model_validate(await insert(orm))
            )
        return await insert(orm)
