import json
import os
from typing import List

import pandas as pd
from dotenv import load_dotenv
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.output_parsers.boolean import BooleanOutputParser
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import (
    BaseSQLDatabaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import MetaData, Table

from app.prompts import (
    few_shot_column_mapping_prompt,
    few_shot_sql_column_addition_prompt,
    few_shot_tech_company_classifier_prompt,
)

load_dotenv(".env")


def get_formatted_data(df: pd.DataFrame) -> List[dict]:
    data = []
    for i in range(len(df)):
        metadata_fields = ""
        for col in df.columns:
            if col != "Description":
                metadata_fields += f"- {col}: {df[col][i]}\n"
        data.append(
            {
                "metadata_fields": metadata_fields.strip(),
                "description": df["Description"][i],
            }
        )
    return data


db = SQLDatabase.from_uri(os.environ.get("DATABASE_URL"))
llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
)
boolean_output_parser = BooleanOutputParser()
json_output_parser = JsonOutputParser()

execute_query = QuerySQLDataBaseTool(db=db)
# write_query = create_sql_query_chain(llm, db, prompt=few_shot_sql_column_addition_prompt)

classification_chain = (
    few_shot_tech_company_classifier_prompt | llm | boolean_output_parser
)
columns_mapping_chain = few_shot_column_mapping_prompt | llm | json_output_parser
# incremental_column_addition_chain = write_query | execute_query
# incremental_column_addition_chain = few_shot_sql_column_addition_prompt | llm | execute_query
incremental_column_addition_chain = few_shot_sql_column_addition_prompt | llm


async def call_llm(df: pd.DataFrame) -> pd.DataFrame:
    df["Technology Company"] = await classification_chain.abatch(get_formatted_data(df))
    if "companies" not in db.get_usable_table_names():
        df.to_sql(
            "companies",
            con=os.environ.get("DATABASE_URL"),
            if_exists="replace",
            index=False,
        )
    else:
        metadata = MetaData()
        table = Table("companies", metadata, autoload_with=db._engine)
        column_names = [column.name for column in table.columns]
        if set(column_names) == set(df.columns):
            df.to_sql(
                "companies",
                con=os.environ.get("DATABASE_URL"),
                if_exists="append",
                index=False,
            )
        else:
            original_df_dict = (
                pd.read_sql_table("companies", con=os.environ.get("DATABASE_URL"))
                .head(5)
                .to_dict(orient="list")
            )
            new_df_dict = df.head(5).to_dict(orient="list")
            column_mappings = await columns_mapping_chain.ainvoke(
                {"df1": original_df_dict, "df2": new_df_dict}
            )
            print(column_mappings)
            non_mapped_columns = []

            for col in column_mappings:
                if not column_mappings[col]:
                    non_mapped_columns.append(col)
                else:
                    df.rename(columns={col: column_mappings[col]}, inplace=True)
            print(non_mapped_columns)
            if non_mapped_columns:
                non_mapped_df_dict = (
                    df[non_mapped_columns].head(5).to_dict(orient="list")
                )
                print(non_mapped_df_dict)
                str_non_mapped_dict = json.dumps(non_mapped_df_dict)
                print(str_non_mapped_dict)
                print("BEFORE INVOKE")
                out = incremental_column_addition_chain.invoke(
                    {"columns": str_non_mapped_dict, "schema": "companies"}
                )
                print(out, "OUT +++++++++++++++++")
            df.to_sql(
                "companies",
                con=os.environ.get("DATABASE_URL"),
                if_exists="append",
                index=False,
            )
    return df
