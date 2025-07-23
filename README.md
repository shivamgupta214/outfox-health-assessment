
Healthcare Cost Navigator
A full-stack application designed to help users explore healthcare pricing and quality data. It features data ingestion via CSV uploads, structured querying for healthcare providers, and a real-time AI-powered natural language interface to query the data.

<img src="https://github.com/shivamgupta214/outfox-health-assessment/raw/main/project_screenshots/Screenshot%202025-07-22%20at%2011.57.15%E2%80%AFPM.png" alt="App Screenshot" width="600"/>

<img src="https://github.com/shivamgupta214/outfox-health-assessment/blob/main/project_screenshots/Screenshot%202025-07-22%20at%2011.57.31%E2%80%AFPM.png" alt="App Screenshot" width="600"/>

<img src="https://github.com/shivamgupta214/outfox-health-assessment/blob/main/project_screenshots/Screenshot%202025-07-22%20at%2011.57.46%E2%80%AFPM.png" alt="App Screenshot" width="600"/>

<img src="https://github.com/shivamgupta214/outfox-health-assessment/blob/main/project_screenshots/Screenshot%202025-07-22%20at%2011.57.57%E2%80%AFPM.png" alt="App Screenshot" width="600"/>

[![Watch the video](https://github.com/shivamgupta214/outfox-health-assessment/blob/main/ScreenRecoding.mp4)



Features
CSV Data Upload: Upload hospital data and generate mock star ratings from CSV files.

Structured Provider Search: Find healthcare providers based on ZIP code, radius, and MS-DRG (Medical Severity Diagnosis Related Group) keywords.

AI-Powered Natural Language Query (NL2SQL): Ask questions about hospital data in plain English and receive concise, AI-generated summaries.

Real-time Chat Interface: Interact with the AI using a WebSocket connection for a fluid conversational experience.

Responsive UI: A clean and modern user interface built with React and custom CSS.

![System Design](https://github.com/shivamgupta214/outfox-health-assessment/blob/main/project_screenshots/sys_design.png)




Technology Stack
Backend:

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+.

SQLAlchemy: Python SQL toolkit and Object Relational Mapper (ORM) for interacting with the PostgreSQL database.

PostgreSQL: A powerful, open-source relational database system.

Pandas: For efficient CSV data processing and transformation during ETL.

OpenAI API: Powers the Natural Language to SQL conversion and result summarization.

python-dotenv: For managing environment variables.

psycopg2-binary: PostgreSQL adapter for Python.

uvicorn: ASGI server to run the FastAPI application.

geopy: For basic geospatial calculations (though currently using a mock ZIP code map).

Frontend:

React.js: A JavaScript library for building user interfaces.

React Router DOM: For declarative routing in your React application.

Axios: A promise-based HTTP client for making API requests.

WebSockets: For real-time communication with the AI chat backend.

Custom CSS: For styling the user interface.

Project Structure
healthcare-cost-navigator/
├── backend/
│   ├── .env                  # Environment variables (API keys, DB URL)
│   ├── main.py               # Entry point for the FastAPI backend
│   ├── api/
│   │   └── apis.py           # FastAPI application, API endpoints (REST & WebSocket)
│   ├── models/
│   │   ├── __init__.py       # Makes 'models' a Python package
│   │   └── models.py         # SQLAlchemy ORM models for database tables
│   ├── ai_service/
│   │   ├── __init__.py       # Makes 'ai_service' a Python package
│   │   └── ai_service.py     # AI logic for NL2SQL and summarization
│   ├── etl/                  # ETL module (assuming this location)
│   │   ├── __init__.py       # Makes 'etl' a Python package
│   │   └── etl.py            # ETL logic for processing CSV data
│   └── requirements.txt      # Backend Python dependencies
├── outfox-frontend/          # Your React application directory
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── components/
│   │       ├── ChatPage.js
│   │       ├── FileUpload.js
│   │       ├── GetProvidersPage.js
│   │       └── NavigationBar.js
│   ├── package.json
│   └── ...
└── .gitignore                # Specifies files/directories to ignore in Git

Setup Instructions
Prerequisites
Docker and Docker Compose: For containerized deployment (recommended).

Python 3.8+ (if running directly without Docker)

Node.js & npm/yarn (for the React frontend)

PostgreSQL Database: If not using Docker Compose, ensure you have a PostgreSQL server running and access to a database.

1. Clone the Repository
git clone <your-repository-url>
cd healthcare-cost-navigator

2. Docker Compose Setup (Recommended)
This method simplifies setting up both the backend and database.

a. Create docker-compose.yml in the project root (healthcare-cost-navigator/)

version: '3.8'

services:
  db:
    image: postgres:14-alpine
    container_name: healthcare_db
    environment:
      POSTGRES_DB: healthcare_navigator_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d healthcare_navigator_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: healthcare_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/healthcare_navigator_db
      OPEN_AI_API: ${OPEN_AI_API} # Read from host's .env or environment
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app # Mount backend code for hot-reloading (development)

  frontend:
    build:
      context: ./outfox-frontend
      dockerfile: Dockerfile
    container_name: healthcare_frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./outfox-frontend:/app # Mount frontend code for hot-reloading (development)
      - /app/node_modules # Prevent host node_modules from overwriting container's
    environment:
      # React apps typically need REACT_APP_ prefix for env vars
      REACT_APP_BACKEND_URL: http://localhost:8000
      REACT_APP_WS_URL: ws://localhost:8000/ws/ask

volumes:
  db_data:

b. Create backend/Dockerfile


FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

c. Create outfox-frontend/Dockerfile

FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

EXPOSE 3000


CMD ["yarn", "start"]

CMD ["npm", "start"]

d. Create .env file in backend/ directory

# backend/.env
DATABASE_URL="postgresql://user:password@db:5432/healthcare_navigator_db"
OPEN_AI_API="your_openai_api_key_here" # Replace with your actual OpenAI API key

Note: When using Docker Compose, the DATABASE_URL for the backend container points to the db service name, not localhost.

e. Build and Run with Docker Compose

From the project root (healthcare-cost-navigator/):

docker-compose build
docker-compose up

This will build the images, start the PostgreSQL database, backend, and frontend containers.

3. Manual Setup (Without Docker Compose)
If you prefer to run directly on your host machine:

a. Backend Setup (FastAPI)

Navigate to the backend directory.

cd backend

i. Create a Python Virtual Environment (Recommended)

python3 -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate

ii. Install Python Dependencies

pip install -r requirements.txt
# If you don't have a requirements.txt, you can create one or install manually:
# pip install fastapi uvicorn[standard] sqlalchemy pandas python-dotenv openai psycopg2-binary geopy

iii. Create a .env file in backend/ directory

# backend/.env
DATABASE_URL="postgresql://user:password@localhost:5432/database_name" # Replace with your host DB details
OPEN_AI_API="your_openai_api_key_here"

iv. Run the FastAPI Backend

uvicorn main:app --reload

The backend server will start, typically on http://127.0.0.1:8000. Keep this terminal window open.

b. Frontend Setup (React)

Navigate to your frontend application directory.

cd ../outfox-frontend # Assuming you are in the 'backend' directory
# or if you are in the project root:
# cd outfox-frontend

i. Install Node.js Dependencies

npm install
# or
yarn install

ii. Run the React Development Server

npm start
# or
yarn start

The React app will open in your browser, typically on http://localhost:3000.

Database Seeding Instructions
After starting the backend (either via Docker Compose or manually), the database tables (hospital_data and star_rating) will be automatically created on startup.

To populate them with data:

Download Sample CSV: Obtain your MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv file. Place it in a convenient location (e.g., in your backend/ directory for easier access if using cURL, or just remember its path).

Upload via Frontend:

Open your browser and go to http://localhost:3000.

On the home page, use the "Upload Hospital Data" and "Upload Hospital Rating" sections. Select your CSV file for both and click "Upload".

Upload via Swagger UI (Backend API Docs):

Open your browser and go to http://127.0.0.1:8000/docs.

Find the /upload-hospital-data endpoint. Click "Try it out", select your CSV, and Execute.

Find the /upload-hospital-rating endpoint. Click "Try it out", select the same CSV, and Execute. (This generates mock ratings for unique providers found in the CSV).

Sample cURL Commands
Replace http://localhost:8000 with your backend URL if it's different (e.g., if you're deploying to a cloud service).

1. Upload Hospital Data (POST)

curl -X POST "http://localhost:8000/upload-hospital-data" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@/path/to/your/MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv;type=text/csv"

Replace /path/to/your/MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv with the actual path to your CSV file on your local machine.

2. Upload Hospital Rating (POST)

curl -X POST "http://localhost:8000/upload-hospital-rating" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@/path/to/your/MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv;type=text/csv"

Use the same CSV file as for hospital data.

3. Search Providers (GET)

curl -X GET "http://localhost:8000/providers?zip_code=36301&radius_km=50&ms_drg=HEART%20SURGERY" \
-H "accept: application/json"

4. Ask AI (Natural Language Query - POST)

curl -X POST "http://localhost:8000/ask?natural_language_query=What%27s%20the%20cheapest%20hospital%20for%20knee%20replacement%3F" \
-H "accept: application/json"

5. WebSocket Chat (/ws/ask)

cURL does not directly support interactive WebSocket communication. You can test this endpoint using:

Browser Developer Console: Open http://localhost:3000/chat, open the browser console (F12), and type messages.

wscat (Node.js CLI tool):

npm install -g wscat
wscat -c ws://localhost:8000/ws/ask

Then type your queries in the terminal.

Example AI Prompts
The AI assistant can answer questions related to hospital pricing, quality, and procedures. Here are some examples:

"Who has the best ratings for heart surgery near 36301?"

"What is the cheapest hospital for pneumonia in New York?"

"List hospitals in California with high total discharges for stroke treatment."

"Show me the average covered charges for appendectomy in zip code 90210."

"Which providers have a rating of 8 or higher for any procedure?"

"Tell me about hospitals in Texas that perform hip replacement surgery."

Architecture Decisions and Trade-offs
FastAPI for Backend: Chosen for its high performance, modern Python features (async/await), automatic API documentation (Swagger UI), and strong type hints, which accelerate development.

React for Frontend: Provides a component-based architecture for building dynamic and responsive user interfaces.

PostgreSQL for Database: A robust, open-source relational database suitable for structured healthcare data.

NL2SQL with OpenAI:

Decision: Leveraging large language models (LLMs) for natural language understanding allows for a highly intuitive user experience, removing the need for users to learn SQL or complex search filters.

Trade-offs:

Cost: API calls to OpenAI incur costs.

Latency: While generally fast, LLM calls add a small amount of latency compared to direct database queries.

Accuracy: LLM output can sometimes be non-deterministic or generate incorrect SQL, though prompt engineering aims to minimize this. Robust error handling and input validation are crucial.

Security: Directly executing AI-generated SQL is a significant security risk (SQL Injection). In a production environment, rigorous sanitization, whitelisting, or using parameterized queries with an ORM (like SQLAlchemy's query builder for GET /providers) is essential. For the /ask endpoint, the prompt is designed to produce safe SELECT statements, but this should be hardened for production.

WebSockets for Chat:

Decision: Provides a persistent, bi-directional communication channel, ideal for real-time chat experiences where multiple queries and responses flow continuously without the overhead of repeated HTTP handshakes.

Trade-offs: More complex to set up and manage compared to simple HTTP requests, requiring state management on both client and server.

Mock Geospatial Data & Ratings:

Decision: For simplicity and to focus on the core NL2SQL and ETL logic, a pre-defined dictionary (ZIP_CODE_LAT_LON_MAP) is used for ZIP code coordinates, and random ratings are generated.

Trade-offs: Not production-ready for real-world geospatial searches or actual hospital ratings. A production system would integrate with a dedicated geospatial database (e.g., PostGIS) and real hospital rating APIs.
