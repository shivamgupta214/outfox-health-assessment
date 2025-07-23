import os 
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query, status, WebSocket, WebSocketDisconnect

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from dotenv import load_dotenv
from models.models import HospitalData, StarRating, Base
from etl import process_csv_hospital_data, process_csv_hospital_rating
import logging
import fastapi.middleware.cors
from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim
from sqlalchemy import func
from ai_service.ai_service import AIService
from typing import List, Dict, Any, Union

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPEN_AI_API")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Healthcare Cost Navigator backend", description="API for Healthcare Cost Navigator", version="0.1.0")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise




@app.post("/upload-hospital-data")
async def upload_hospital_data(file: UploadFile = File(...), db: Session = Depends(get_db)):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        content = await file.read()
        try:
            decoded_content = content.decode("utf-8")
        except UnicodeDecodeError:
            decoded_content = content.decode("latin1")  # Try a different encoding
        logging.info("Decoded content: %s", decoded_content)
        result = await process_csv_hospital_data(decoded_content, db)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-hospital-rating")
async def upload_hospital_rating(file: UploadFile = File(...), db: Session = Depends(get_db)):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        content = await file.read()
        try:
            decoded_content = content.decode("utf-8")
        except UnicodeDecodeError:
            decoded_content = content.decode("latin1")
        logging.info("Decoded content for hospital rating: %s", decoded_content)
        result = await process_csv_hospital_rating(decoded_content, db)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize geolocator
geolocator = Nominatim(user_agent="healthcare_cost_navigator")

# Function to get coordinates from ZIP code using geopy
# def get_coordinates_from_zip(zip_code: str):
#     location = geolocator.geocode(zip_code)
#     if location:
#         return location.latitude, location.longitude
#     else:
#         raise ValueError(f"Could not find coordinates for ZIP code: {zip_code}")

# Function to calculate the distance between two points using the Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in miles is 3956
    miles = 3956 * c
    return miles


ZIP_CODE_LAT_LON_MAP = {
    "36301": (31.3072, -85.3956),
    "35801": (34.6993, -86.6902),
    "76065": (32.5156, -97.8361),
    "90210": (34.0195, -118.4105),
    "90001": (33.7701, -118.1956),
    "90002": (33.7701, -118.1956),
    "90003": (33.7701, -118.1956),
    "90004": (33.7701, -118.1956),
    "90005": (33.7701, -118.1956),
    "90006": (33.7701, -118.1956),
    "10001": (40.7128, -74.0060),
    "10002": (40.7128, -74.0060),
    "10003": (40.7128, -74.0060),
    "10004": (40.7128, -74.0060),
    "10005": (40.7128, -74.0060),
    "10006": (40.7128, -74.0060),
    "10007": (40.7128, -74.0060),
}

def get_nearby_zip_codes(zip_code: str, radius_km: float) -> list[str]:
    if zip_code in ZIP_CODE_LAT_LON_MAP:
        C_lat, C_lon = ZIP_CODE_LAT_LON_MAP[zip_code]
        nearby_zip_codes = []
        for zip_code, (lat, lon) in ZIP_CODE_LAT_LON_MAP.items():
            dist = haversine(C_lat, C_lon, lat, lon)
            if dist <= radius_km:
                nearby_zip_codes.append(zip_code)
        return nearby_zip_codes
    else:
        return []

@app.get("/providers")
async def search_hospitals(
    zip_code: str = Query(..., description="ZIP code to search around"),
    radius_km: float = Query(..., description="Radius in kilometers"),
    ms_drg: str = Query(..., description="MS-DRG procedure to search for"),
    db: Session = Depends(get_db)
):
    try:
        logging.info(f"Received search request with zip_code: {zip_code}, radius_km: {radius_km}, ms_drg: {ms_drg}")

        # Convert radius from kilometers to miles
        radius_miles = radius_km * 0.621371

        # Get coordinates from the input ZIP code using geopy
        # zipcode= get_coordinates_from_zip(zip_code)
        # logging.info(f"Coordinates for zip_code {zipcode}")
        nearby_zip_codes = get_nearby_zip_codes(zip_code, radius_km)
        # Query hospitals offering the specified MS-DRG procedure using ILIKE for case-insensitive search

        logging.info(f"Nearby ZIP codes: {nearby_zip_codes}")

        query = db.query(
            HospitalData.provider_id,
            HospitalData.provider_name,
            HospitalData.provider_city,
            HospitalData.provider_state,
            HospitalData.provider_zip_code,
            HospitalData.ms_drg_definition,
            HospitalData.total_discharges,
            HospitalData.average_covered_charges,
            HospitalData.average_total_payments,
            StarRating.overall_rating
        ).outerjoin(StarRating, HospitalData.provider_id == StarRating.provider_id).filter(func.lower(HospitalData.ms_drg_definition).ilike(f"%{ms_drg.lower()}%"))

        if nearby_zip_codes:
            query = query.filter(HospitalData.provider_zip_code.in_(nearby_zip_codes))
        
        query = query.order_by(HospitalData.average_covered_charges.asc())
        results = query.all()

        provider_list = []
        unique_provider_ids = {}
        for row in results:
            if row.provider_id not in unique_provider_ids:
                unique_provider_ids[row.provider_id] = {
                    "provider_id": row.provider_id,
                    "provider_name": row.provider_name,
                    "provider_city": row.provider_city,
                    "provider_state": row.provider_state,
                    "provider_zip_code": row.provider_zip_code,
                    "ms_drg_definition": row.ms_drg_definition,
                    "total_discharges": row.total_discharges,
                    "average_covered_charges": row.average_covered_charges,
                    "average_total_payments": row.average_total_payments,
                    "overall_rating": row.overall_rating
                }
                provider_list = list(unique_provider_ids.values())

        return {"status": "success", "data": provider_list}
    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logging.error(f"Error searching hospitals: {e}")
        raise HTTPException(status_code=500, detail="Error searching hospitals")

        # Filter hospitals within the specified radius
        # results = []
        # for hospital in hospitals:
        #     # Assume provider_zip_code is accurate and use it directly
        #     provider_lat, provider_lon = get_coordinates_from_zip(hospital.provider_zip_code)
        #     logging.info(f"Coordinates for provider {hospital.provider_id}: latitude {provider_lat}, longitude {provider_lon}")
        #     # distance = haversine(lon, lat, provider_lon, provider_lat)
        #     if distance <= radius_miles:
        #         results.append({
        #             "provider_id": hospital.provider_id,
        #             "provider_name": hospital.provider_name,
        #             "provider_city": hospital.provider_city,
        #             "provider_state": hospital.provider_state,
        #             "estimated_price": hospital.average_total_payments,
        #             "average_covered_charges": hospital.average_covered_charges,
        #             "quality_signals": {
        #                 "overall_rating": db.query(StarRating.overall_rating).filter(StarRating.provider_id == hospital.provider_id).scalar()
        #             }
        #         })

        # # Sort results by average_covered_charges
        # results.sort(key=lambda x: x["average_covered_charges"])
global_ai_service_instance = AIService(api_key=OPENAI_API_KEY)

@app.post("/ask", response_model=Union[List[Dict[str, Any]], str]) # Updated response_model
async def query_data_nl(
    natural_language_query: str,
    db: Session = Depends(get_db)
):
    try:

        sql_query = await global_ai_service_instance.generate_sql_query(natural_language_query)
        if sql_query == "IRRELEVANT_QUERY_SIGNAL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings."
            )

        result = db.execute(text(sql_query))
        column_names = result.keys()
        rows = result.fetchall()
        results_as_dicts = [dict(zip(column_names, row)) for row in rows]

        # --- Summarize the results using AI service ---
        summary_response = await global_ai_service_instance.summarize_results(natural_language_query, results_as_dicts)
        return summary_response # Return the natural language summary

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error executing generated SQL: {e}. Please check the generated SQL query or your database connection.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing natural language query: {e}")


        

@app.websocket("/ws/ask")
async def websocket_query_data_nl(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for natural language queries, providing real-time responses.
    """
    await websocket.accept()
    print("WebSocket: Client connected.")
    try:
        while True:
            natural_language_query = await websocket.receive_text()
            print(f"WebSocket: Received query: '{natural_language_query}'")

            try:
                # 1. Generate SQL query using AI service
                sql_query = await global_ai_service_instance.generate_sql_query(natural_language_query)
                print(f"WebSocket: Generated SQL: {sql_query}")

                # 2. Check for irrelevant query signal
                if sql_query == "IRRELEVANT_QUERY_SIGNAL":
                    response_message = "I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings."
                    await websocket.send_text(response_message)
                    print(f"WebSocket: Sent irrelevant query response.")
                    continue # Continue to next message

                # 3. Execute the generated SQL query
                print(f"WebSocket: Executing SQL: {sql_query}")
                result = db.execute(text(sql_query))
                column_names = result.keys()
                rows = result.fetchall()
                results_as_dicts = [dict(zip(column_names, row)) for row in rows]
                print(f"WebSocket: Database query returned {len(results_as_dicts)} rows.")

                # 4. Summarize the results using AI service
                summary_response = await global_ai_service_instance.summarize_results(natural_language_query, results_as_dicts)
                await websocket.send_text(summary_response)
                print(f"WebSocket: Sent summary response.")

            except HTTPException as e:
                # Catch HTTPExceptions (like the irrelevant query one) and send their detail
                await websocket.send_text(f"Error: {e.detail}")
                print(f"WebSocket: Sent HTTPException detail: {e.detail}")
            except SQLAlchemyError as e:
                error_msg = f"Database error: {e}. Please check the generated SQL query or your database connection."
                await websocket.send_text(f"Error: {error_msg}")
                print(f"WebSocket: Sent SQLAlchemyError: {error_msg}")
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                await websocket.send_text(f"Error: {error_msg}")
                print(f"WebSocket: Sent unexpected error: {error_msg}")

    except WebSocketDisconnect:
        print("WebSocket: Client disconnected.")
    except Exception as e:
        print(f"WebSocket: An unhandled error occurred in the main loop: {e}")



