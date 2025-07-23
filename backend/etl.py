import os
import io
import csv
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, func
from sqlalchemy.sql.coercions import expect
import random

from models.models import HospitalData, StarRating, Base

async def process_csv_hospital_data(decoded_content: str, db: Session):
    try:
        logging.info("Processing CSV file")
        df = pd.read_csv(io.StringIO(decoded_content))
        logging.info(f"Loaded {len(df)} rows from CSV")


        column_maping = {
            "Rndrng_Prvdr_CCN": "provider_id",
            "Rndrng_Prvdr_Org_Name": "provider_name",
            "Rndrng_Prvdr_City": "provider_city",
            "Rndrng_Prvdr_State_Abrvtn": "provider_state",
            "Rndrng_Prvdr_Zip5": "provider_zip_code",
            "DRG_Desc": "ms_drg_definition",
            "Tot_Dschrgs": "total_discharges",
            "Avg_Submtd_Cvrd_Chrg": "average_covered_charges",
            "Avg_Tot_Pymt_Amt": "average_total_payments",
            "Avg_Mdcr_Pymt_Amt": "average_medicare_payments",
        }

        dfTransformed = df.rename(columns=column_maping)

        logging.info(f"Transformed {len(dfTransformed)} rows from CSV")

        target_columns = list(column_maping.values())
        logging.info(f"Target columns: {target_columns}")
        cols_to_drop = [col for col in dfTransformed.columns if col not in target_columns]
        dfTransformed = dfTransformed.drop(columns=cols_to_drop)

        logging.info(f"Dropped {len(cols_to_drop)} columns from CSV")

        dfTransformed["provider_id"] = pd.to_numeric(dfTransformed["provider_id"], errors="coerce").astype(pd.Int64Dtype())
        dfTransformed["total_discharges"] = pd.to_numeric(dfTransformed["total_discharges"], errors="coerce").astype(pd.Int64Dtype())
        dfTransformed["average_covered_charges"] = pd.to_numeric(dfTransformed["average_covered_charges"], errors="coerce").astype(pd.Float64Dtype())
        dfTransformed["average_total_payments"] = pd.to_numeric(dfTransformed["average_total_payments"], errors="coerce").astype(pd.Float64Dtype())
        dfTransformed["average_medicare_payments"] = pd.to_numeric(dfTransformed["average_medicare_payments"], errors="coerce").astype(pd.Float64Dtype())
        dfTransformed["provider_state"] = dfTransformed["provider_state"].str.upper()
        dfTransformed["provider_zip_code"] = dfTransformed["provider_zip_code"].astype(str).replace('<NA>', None)

        for col in ["provider_name", "provider_city", "provider_state", "ms_drg_definition"]:
            dfTransformed[col] = dfTransformed[col].astype(str).replace('nan', None)

        logging.info(f"Converted {len(dfTransformed)} rows from CSV")

        data_to_insert = dfTransformed.where(pd.notna(dfTransformed), None).to_dict(orient="records")

        if not data_to_insert:
            logging.info("No data to insert")
            return {"status": "success", "message": "No valid data to insert"}

        logging.info(f"Inserting {len(data_to_insert)} rows into database")

        try:
            db.bulk_insert_mappings(HospitalData, data_to_insert)
            db.commit()
            logging.info("Data inserted successfully")
            return {"status": "success", "message": "Data inserted successfully"}
        except IntegrityError as e:
            db.rollback()
            logging.error(f"Integrity error: {e}")
            return {"status": "error", "message": "Integrity error: " + str(e)}
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"SQLAlchemy error: {e}")
            return {"status": "error", "message": "SQLAlchemy error: " + str(e)}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"status": "error", "message": "Unexpected error: " + str(e)}


async def process_csv_hospital_rating(decoded_content: str, db: Session):
    try:
        logging.info("Processing CSV file for Star Rating")
        df = pd.read_csv(io.StringIO(decoded_content))
        logging.info(f"Loaded {len(df)} rows from CSV")

        column_mapping = {
            "Provider ID": "provider_id",
            "Hospital overall rating": "overall_rating"
        }

        dfTransformed = df.rename(columns=column_mapping)

        logging.info(f"Transformed {len(dfTransformed)} rows from CSV")

        target_columns = list(column_mapping.values())
        logging.info(f"Target columns: {target_columns}")
        cols_to_drop = [col for col in dfTransformed.columns if col not in target_columns]
        dfTransformed = dfTransformed.drop(columns=cols_to_drop)

        logging.info(f"Dropped {len(cols_to_drop)} columns from CSV")

        dfTransformed["provider_id"] = pd.to_numeric(dfTransformed["provider_id"], errors="coerce").astype(pd.Int64Dtype())
        dfTransformed["overall_rating"] = pd.to_numeric(dfTransformed["overall_rating"], errors="coerce").astype(pd.Float64Dtype())

        # Replace null values in 'overall_rating' with random numbers from 1 to 10
        dfTransformed["overall_rating"] = dfTransformed["overall_rating"].apply(lambda x: random.randint(1, 10) if pd.isna(x) else x)

        logging.info(f"Converted {len(dfTransformed)} rows from CSV")

        data_to_insert = dfTransformed.where(pd.notna(dfTransformed), None).to_dict(orient="records")

        if not data_to_insert:
            logging.info("No data to insert")
            return {"status": "success", "message": "No valid data to insert"}

        logging.info(f"Inserting {len(data_to_insert)} rows into StarRating table")

        try:
            db.bulk_insert_mappings(StarRating, data_to_insert)
            db.commit()
            logging.info("Data inserted successfully into StarRating table")
            return {"status": "success", "message": "Data inserted successfully"}
        except IntegrityError as e:
            db.rollback()
            logging.error(f"Integrity error: {e}")
            return {"status": "error", "message": "Integrity error: " + str(e)}
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"SQLAlchemy error: {e}")
            return {"status": "error", "message": "SQLAlchemy error: " + str(e)}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"status": "error", "message": "Unexpected error: " + str(e)}



        
