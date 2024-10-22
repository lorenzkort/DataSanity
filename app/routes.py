import os
from flask import render_template, request, jsonify
from app import app
from .visualise import visualize_data_lineage
import anthropic
import json

client = anthropic.Anthropic()


def claud_request(prompt):
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def parse_json(response):
    # Parse the JSON string
    json_data = json.loads(response)
    # Pretty print the JSON
    pretty_json = json.dumps(json_data, indent=2)
    return pretty_json


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        sql_code = request.form["sql_code"]
        lineage_data = get_lineage(sql_code)
        return render_template(
            "result.html",
            lineage_json=lineage_data["json"],
            lineage_viz=lineage_data["visualization"],
        )
    return render_template("index.html")


def get_lineage(sql_code):
    api_key = app.config.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

    prompt = f"""
    Analyze the following SQL code and generate a JSON file that represents the data lineage in a format compatible with Purview. The JSON should include source and target tables, columns, and their relationships.

    DON'T RESPOND WITH ANYTHING ELSE THAN VALID JSON!!

    SQL Code:
    {sql_code}

    Please provide the lineage information in the following JSON format:
    {{
        "entities": [
            {{
                "type": "azure_sql_table",
                "name": "<table_name>",
                "qualifiedName": "<database>.<schema>.<table_name>",
                "columns": [
                    {{
                        "name": "<column_name>",
                        "type": "<data_type>"
                    }}
                ]
            }}
        ],
        "processes": [
            {{
                "name": "SQL Query",
                "inputs": [
                    {{
                        "uniqueAttributes": {{
                            "qualifiedName": "<input_table_qualified_name>"
                        }}
                    }}
                ],
                "outputs": [
                    {{
                        "uniqueAttributes": {{
                            "qualifiedName": "<output_table_qualified_name>"
                        }}
                    }}
                ]
            }}
        ]
    }}

    Ensure that the JSON is valid and includes all relevant tables, columns, and relationships found in the SQL code.
    """

    response = claud_request(prompt)
    retries = 3

    for attempt in range(retries):
        try:
            parsed_json = parse_json(response)
            fig = visualize_data_lineage(parsed_json)
            return {"json": parsed_json, "visualization": fig.to_json()}
        except json.JSONDecodeError as e:
            if attempt < retries - 1:  # If not the last attempt
                error_message = (
                    f"Error parsing JSON (Attempt {attempt + 1}/{retries}): {str(e)}"
                )
                print(error_message)
                parsed_json = parse_json(
                    response + "\n\nFix the following error: " + error_message
                )
                fig = visualize_data_lineage(parsed_json)
                print(parsed_json)
                return {"json": parsed_json, "visualization": fig.to_json()}
            else:
                return f"Error parsing JSON after {retries} attempts: {str(e)}"
