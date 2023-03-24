from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text
import databases
import os
from typing import Dict, List

# SQLAlchemy Database URL
# example: "postgresql://postgres@localhost:5433/postgres"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///chinook.db")
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

app = FastAPI(
    title="SQL Playground Plugin",
    version="1.0.0",
    # Specify the API servers here
    # servers=[
    #    {"url": "https://api.example.com/v1", "description": "Production server"},
    #    {"url": "https://api.staging.example.com/v1", "description": "Staging server"},
    # ],
)

# Connection middleware
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class SQLQuery(BaseModel):
    query: str


class TableColumn(BaseModel):
    name: str
    type: str


class TableColumnsResponse(BaseModel):
    columns: List[TableColumn]


class TablesResponse(BaseModel):
    tables: List[str]


class SQLQueryResult(BaseModel):
    result: List[Dict[str, str]]


get_tables_description = """
Returns a list of tables in the database.
"""


@app.get("/tables", response_model=TablesResponse, description=get_tables_description)
async def get_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}


get_columns_description = """
Returns a list of columns in a table.
"""


@app.get(
    "/tables/{table_name}/columns",
    response_model=TableColumnsResponse,
    description=get_columns_description,
)
async def get_columns(table_name: str):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail="Table not found")
    columns = [
        {"name": column["name"], "type": str(column["type"])}
        for column in inspector.get_columns(table_name)
    ]
    return {"columns": columns}


execute_sql_description = """
Executes a SQL query and returns the result.
"""


@app.post(
    "/execute_sql", response_model=SQLQueryResult, description=execute_sql_description
)
async def execute_sql(query: SQLQuery):
    async with database.transaction():
        result = await database.fetch_all(query=query.query)
        return {"result": result}


def main():
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
