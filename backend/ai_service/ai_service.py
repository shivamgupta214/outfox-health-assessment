# ai_service.py

import os
from openai import AsyncOpenAI
from typing import Dict, Any, List

class AIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def _get_provider_data_schema(self) -> str:
        """
        Generates a string representation of the HospitalData and StarRating table schemas for the AI model.
        Corrected column names to match models.py:
        - ms_drg_definition (from ms_drg_defination)
        - provider_zip_code (from provider_zip)
        - overall_rating (from rating)
        """
        schema = """
        Table Name: hospital_data
        Columns:
        - id: INTEGER (Primary Key, auto-increment)
        - provider_id: INTEGER (Unique Identifier for Provider, maps to Rndrng_Prvdr_CCN in original CSV. NOT unique in this table as a provider can have multiple DRG entries.)
        - provider_name: TEXT
        - provider_city: TEXT
        - provider_state: TEXT
        - provider_zip_code: TEXT
        - ms_drg_definition: TEXT (Medical Service DRG definition)
        - total_discharges: INTEGER
        - average_covered_charges: REAL (Float)
        - average_total_payments: REAL (Float)
        - average_medicare_payments: REAL (Float)
        Description: This table contains all information about healthcare providers and their specific DRG procedures.

        Table Name: star_rating
        Columns:
        - id: INTEGER (Primary Key, auto-increment)
        - provider_id: INTEGER (Refers to hospital_data.provider_id. Unique in this table to give one rating per provider.)
        - overall_rating: INTEGER (Rating from 1 to 10)
        Description: This table stores mock quality ratings for providers, linked by provider_id.

        Relationship: hospital_data.provider_id = star_rating.provider_id (Conceptual join, not a database-enforced foreign key due to hospital_data.provider_id not being unique)

        """
        return schema

    async def generate_sql_query(self, natural_language_query: str) -> str:
        """
        Uses an OpenAI model to convert a natural language query into a SQL query
        for the 'hospital_data' and 'star_rating' tables.
        If the query is irrelevant, it returns a specific signal string.
        Corrected column names in prompt and examples to match models.py.
        """
        schema_info = self._get_provider_data_schema()

        prompt = f"""
        You are a SQL query generator. Your task is to convert natural language questions into valid PostgreSQL SQL queries.
        The database contains two tables: 'hospital_data' and 'star_rating', with the following schemas and relationship:

        {schema_info}

        Important Rules:
        1.  Generate only the SQL query, without any additional text, explanations, or backticks.
        2.  Do NOT use any SQL functions or syntax that are not standard PostgreSQL.
        3.  Do NOT include comments in the SQL query.
        4.  Always select all relevant columns unless specific columns are requested. Use aliases for clarity (e.g., `hd.provider_name`, `sr.overall_rating`).
        5.  Use `ILIKE` for case-insensitive partial string matches (e.g., `WHERE hd.provider_name ILIKE '%hospital%'`).
        6.  For "cheapest", "most expensive", "highest", "lowest", use `ORDER BY` and `LIMIT`.
        7.  For "best ratings" or "highest rated", join with `star_rating` and use `ORDER BY sr.overall_rating DESC`.
        8.  If the query asks for "near me", you can assume a city or state and filter by `hd.provider_city` or `hd.provider_state` or `hd.provider_zip_code`. If no specific location is mentioned, do not add location filters.
        9.  Ensure column names in the query exactly match the schema.
        10. If the query is ambiguous or cannot be translated to a meaningful SQL query given the schema, return a simple SELECT statement like `SELECT * FROM hospital_data LIMIT 10;` or indicate that it's not possible.
        11. When joining tables, use `LEFT JOIN` to ensure all relevant records from the primary table (e.g., `hospital_data`) are included even if there's no matching data in the joined table.
        12. If a query implies unique providers (e.g., "cheapest hospital"), you might need to use `DISTINCT` on `provider_id` or `GROUP BY provider_id` and aggregate other fields, but generally, selecting from `hospital_data` and joining `star_rating` is sufficient.
        13. **VERY IMPORTANT:** If the natural language query is completely irrelevant to hospital pricing, quality, medical procedures, or hospital data (e.g., "What's the weather today?", "Tell me a joke"), return the exact string "IRRELEVANT_QUERY_SIGNAL" and nothing else.

        Examples:
        - "What's the cheapest hospital for knee replacement?"
          SELECT hd.provider_id, hd.provider_name, hd.provider_city, hd.average_covered_charges FROM hospital_data AS hd WHERE hd.ms_drg_definition ILIKE '%KNEE REPLACEMENT%' ORDER BY hd.average_covered_charges ASC LIMIT 1;

        - "Which hospitals have the highest total discharges for heart surgery?"
          SELECT hd.provider_id, hd.provider_name, hd.provider_city, hd.total_discharges FROM hospital_data AS hd WHERE hd.ms_drg_definition ILIKE '%HEART SURGERY%' ORDER BY hd.total_discharges DESC LIMIT 5;

        - "Show me all providers in New York with their ratings."
          SELECT hd.provider_id, hd.provider_name, hd.provider_city, hd.provider_state, sr.overall_rating FROM hospital_data AS hd LEFT JOIN star_rating AS sr ON hd.provider_id = sr.provider_id WHERE hd.provider_state = 'NY' LIMIT 10;

        - "List the highest rated hospitals for cancer treatment."
          SELECT hd.provider_id, hd.provider_name, hd.provider_city, hd.ms_drg_definition, sr.overall_rating FROM hospital_data AS hd LEFT JOIN star_rating AS sr ON hd.provider_id = sr.provider_id WHERE hd.ms_drg_definition ILIKE '%CANCER TREATMENT%' ORDER BY sr.overall_rating DESC LIMIT 5;

        Natural Language Query: {natural_language_query}

        SQL Query:
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": natural_language_query}
                ],
                max_tokens=150,
                temperature=0.0
            )
            sql_query = response.choices[0].message.content.strip()
            return sql_query
        except Exception as e:
            print(f"Error generating SQL query with OpenAI: {e}")
            raise

    async def summarize_results(self, original_query: str, query_results: List[Dict[str, Any]]) -> str:
        """
        Uses an OpenAI model to summarize structured query results into a natural language response.
        """
        if not query_results:
            return f"I couldn't find any information for '{original_query}'. Please try a different query."

        results_for_summary = query_results[:5]
        results_str = "\n".join([str(row) for row in results_for_summary])

        summary_prompt = f"""
        You are a helpful assistant that summarizes hospital data.
        A user asked the following question: "{original_query}"
        You found the following data:
        {results_str}

        Please summarize this information in a concise, conversational, and user-friendly sentence or two.
        Focus on the key findings relevant to the user's original question.
        If there are multiple results, mention the top few most relevant ones.
        Include specific details like hospital names, ratings, and relevant procedure names if available.
        For ratings, if they are floats, round them to one decimal place.
        If there are many results, summarize the most important ones without listing all.

        Examples:
        - Original Query: "Who has the best ratings for heart surgery near 10032?"
          Results: [{{'provider_name': 'Mount Sinai Hospital', 'overall_rating': 9}}, {{'provider_name': 'NYU Langone', 'overall_rating': 8.5}}]
          Summary: Based on data, Mount Sinai Hospital (rating: 9/10) and NYU Langone (rating: 8.5/10) have the highest ratings for cardiac procedures near 10032.

        - Original Query: "What's the cheapest hospital for knee replacement?"
          Results: [{{'provider_name': 'Community Hospital', 'average_covered_charges': 25000}}]
          Summary: The cheapest hospital for knee replacement found is Community Hospital with average covered charges of $25,000.

        Summary:
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": f"Summarize the data for the query: '{original_query}' and results: {query_results}"}
                ],
                max_tokens=150,
                temperature=0.2
            )
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            print(f"Error summarizing results with OpenAI: {e}")
            return "I encountered an error while trying to summarize the results. Please try again."