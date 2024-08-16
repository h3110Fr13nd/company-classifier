import json

from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

classification_examples = [
    {
        "metadata_fields": "- Name: TechCorp Inc.\n- Industry: Software",
        "description": "A company that develops and sells cloud-based software solutions for enterprise resource planning and customer relationship management.",
        "response": "YES",
    },
    {
        "metadata_fields": "- CompanyName: AutoParts Co.\n- Industry: Manufacturing\n- Location: Detroit, MI",
        "description": "A traditional manufacturing company that produces and distributes high-quality mechanical parts for the automotive industry.",
        "response": "NO",
    },
    {
        "metadata_fields": "- Org: CyberSecure Ltd.\n- Industry: Cybersecurity\n- Location: New York, NY\n- Founded: 2010",
        "description": "A leading provider of cybersecurity solutions, specializing in threat detection and response for enterprise networks.",
        "response": "YES",
    },
    {
        "metadata_fields": "- Organisation: GreenEarth Org.",
        "description": "A non-profit organization that focuses on wildlife conservation and environmental education.",
        "response": "NO",
    },
    {
        "metadata_fields": "- Entity: AutoParts Co.\n- Region: Detroit, MI\n- Industry: Manufacturing\n- Founded: 1995\n- Employees: 500\n- Revenue: $100M",
        "description": "A traditional manufacturing company that produces and distributes high-quality mechanical parts for the automotive industry.",
        "response": "NO",
    },
    {
        "metadata_fields": "- Name: CyberSecure Ltd.\n- Industry: Cybersecurity",
        "description": "A leading provider of cybersecurity solutions, specializing in threat detection and response for enterprise networks.",
        "response": "YES",
    },
]


tech_company_classifier_prompt = PromptTemplate(
    input_variables=["metadata_fields", "description", "response"],
    template="""Example:

Metadata:
{metadata_fields}
Description: {description}
Response: {response}""",
)


few_shot_tech_company_classifier_prompt = FewShotPromptTemplate(
    examples=classification_examples,
    example_prompt=tech_company_classifier_prompt,
    prefix="""You are an expert in categorizing companies based on their descriptions. Given a company's description and additional contextual metadata, your task is to determine if it is a tech company or not.

Here are some examples:""",
    suffix="Now, categorize the following company:\n\nMetadata:\n{metadata_fields}\nDescription: {description}\nResponse: ",
    input_variables=["metadata_fields", "description"],
)


column_mapping_examples = [
    {
        "df1": f"""{"{" + json.dumps({
            "Customer_ID": [1, 2, 3],
            "First_Name": ["John", "Jane", "Doe"],
            "Last_Name": ["Smith", "Doe", "Johnson"],
            "Email": ["john.smith@example.com", "jane.doe@example.com", "doe.johnson@example.com"]
        }, indent=4) + "}"}""",
        "df2": f"""{"{" + json.dumps({
            "Client_ID": [1, 2, 3],
            "Given_Name": ["John", "Jane", "Doe"],
            "Surname": ["Smith", "Doe", "Johnson"],
            "Contact_Email": ["john.smith@example.com", "jane.doe@example.com", "doe.johnson@example.com"]
        }, indent=4) + "}"}""",
        "output": f"""{"{" + json.dumps({
            "Client_ID": "Customer_ID",
            "Given_Name": "First_Name",
            "Surname": "Last_Name",
            "Contact_Email": "Email"
        }, indent=4) + "}"}""",
    },
    {
        "df1": f"""{"{" + json.dumps({
            "Order_ID": [101, 102, 103],
            "Product": ["Laptop", "Phone", "Tablet"],
            "Price": [1000, 500, 300]
        }, indent=4) + "}"}""",
        "df2": f"""{"{" + json.dumps({
            "OrderNumber": [101, 104, 105],
            "Item_Name": ["Laptop", "Smartwatch", "Phone"],
            "Cost": [1000, 200, 500]
        }, indent=4) + "}"}""",
        "output": f"""{"{" + json.dumps({
            "OrderNumber": "Order_ID",
            "Item_Name": None,
            "Cost": "Price"
        }, indent=4) + "}"}""",
    },
]

column_mapping_prompt = PromptTemplate(
    input_variables=["df1", "df2", "output"],
    template="""Example:
df1:
{df1}

df2:
{df2}

Output:
{output}""",
)

few_shot_column_mapping_prompt = FewShotPromptTemplate(
    examples=column_mapping_examples,
    example_prompt=column_mapping_prompt,
    prefix="""You are provided with two DataFrames, df1 and df2. Both DataFrames contain fields that perform similar functions, but the column names may differ. Your task is to map the columns in df2 to the corresponding columns in df1 based on the similarity of the data they contain. The output should be a JSON object where each key is a column name from df2, and the corresponding value is the name of the matching column from df1. If no appropriate mapping is found, return None.

You are also provided with a few rows of data from each DataFrame to help you understand the nature of the data in the columns.""",
    suffix="""Task:

Given the following df1 and df2, generate the JSON mapping as described.
df1:
{df1}

df2:
{df2}

Output:
""",
    input_variables=["df1", "df2"],
)
example_1 = json.dumps(
    {
        "Phone_Number": ["123-456-7890", "234-567-8901", "345-678-9012"],
        "Shipping_Address": ["123 Elm St", "456 Oak St", "789 Pine St"],
    },
    indent=4,
)
example_2 = json.dumps(
    {
        "Order_Notes": ["Urgent delivery", "Gift wrap", "No special requests"],
        "Payment_Method": ["Credit Card", "PayPal", "Bank Transfer"],
    },
    indent=4,
)

few_shot_sql_column_addition_examples = [
    {
        "columns": f'{"{" + example_1 + "}"}',
        "schema": """CREATE TABLE customers (
    "Customer_ID" INTEGER,
    "First_Name" TEXT,
    "Last_Name" TEXT,
    "Email" TEXT
);

/*
3 rows from customers table:
Customer_ID     First_Name      Last_Name       Email
1               John            Smith           john.smith@example.com
2               Jane            Doe             jane.doe@example.com
3               Doe             Johnson         doe.johnson@example.com
*/""",
        "table_name": "customers",
        "output": 'ALTER TABLE customers ADD COLUMN "Phone_Number" TEXT, ADD COLUMN "Shipping_Address" TEXT;',
    },
    {
        "columns": f'{"{" + example_2 + "}"}',
        "schema": """CREATE TABLE orders (
    "Order_ID" INTEGER,
    "Product" TEXT,
    "Price" INTEGER
);

/*
3 rows from orders table:
Order_ID    Product     Price
101         Laptop      1000
102         Phone       500
103         Tablet      300
*/""",
        "table_name": "orders",
        "output": 'ALTER TABLE orders ADD COLUMN "Order_Notes" TEXT, ADD COLUMN "Payment_Method" TEXT;',
    },
]

sql_column_addition_prompt = PromptTemplate(
    input_variables=["columns", "schema", "output"],
    template="""Example:
## Add the following non-mapped columns to the {table_name} table.
Provided Columns in JSON Format:
{columns}

Existing Table Schema:
{schema}

SQL Query: {output}""",
)


few_shot_sql_column_addition_prompt = FewShotPromptTemplate(
    examples=few_shot_sql_column_addition_examples,
    example_prompt=sql_column_addition_prompt,
    prefix="""You are a Postgres expert. Your task is to create a SQL query that adds columns to an existing table. These columns correspond to fields that were not mapped to any existing columns in the table. Based on the provided columns in JSON format, sample data, and existing table schema, generate the appropriate SQL statements to add these columns with the correct data types.

Follow these best practices:

Only add columns that do not already exist in the table.
Choose the appropriate data type for each column based on the provided sample data.
Wrap each column name in double quotes (") to denote them as delimited identifiers.
If the new column name contains spaces or special characters, use underscores (_) instead.
ONLY generate the SQL query to add or alter the columns; No triple quotes or comments are required. No Prefix or Suffix is required.

Few-Shot Examples:""",
    suffix="""Task:
Given the following columns in JSON format, sample data, and existing table schema, generate the SQL query to add the non-mapped columns to the table table_name.

## Add the following non-mapped columns to the {table_name} table.
Provided Columns in JSON Format:
{columns}

Existing Table Schema:
{schema}

SQL Query: """,
    input_variables=["columns", "schema"],
)

few_shot_sql_column_addition_prompt = few_shot_sql_column_addition_prompt.partial(
    table_name="customers",
    format_str="""{
    "column_name_1": [sample_data_1],
    "column_name_2": [sample_data_2]
}""",
)
