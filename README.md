Healthcare Cost Navigator
A full-stack application designed to help users explore healthcare pricing and quality data. It features data ingestion via CSV uploads, structured querying for healthcare providers, and a real-time AI-powered natural language interface to query the data.

Features
CSV Data Upload: Upload hospital data and upload hospital star ratings CSV files.

Structured Provider Search: Find healthcare providers based on ZIP code, radius, and MS-DRG (Medical Severity Diagnosis Related Group) keywords.

AI-Powered Natural Language Query (NL2SQL): Ask questions about hospital data in plain English and receive concise, AI-generated summaries.

Real-time Chat Interface: Interact with the AI using a WebSocket connection for a fluid conversational experience.

Responsive UI: A clean and modern user interface built with React and custom CSS.

System Design
graph TD
    subgraph Frontend (React Application)
        A[User Interface]
    end

    subgraph Backend (FastAPI Application)
        B[API Endpoints]
        C[ETL Module]
        D[AI Service]
    end

    subgraph Data Layer
        E[PostgreSQL Database]
    end

    subgraph External Services
        F[OpenAI API]
    end

    A -- HTTP Requests --> B
    A -- WebSocket Connection --> B

    B -- Calls ETL Functions --> C
    B -- Queries Database --> E
    B -- Calls AI Service --> D

    C -- Reads/Writes Data --> E

    D -- API Calls --> F
    F -- AI Responses --> D

    E -- Data Results --> B

    B -- HTTP/WebSocket Responses --> A

    style Frontend fill:#e0f2f7,stroke:#3498db,stroke-width:2px
    style Backend fill:#e8f5e9,stroke:#27ae60,stroke-width:2px
    style Data Layer fill:#f3e5f5,stroke:#9b59b6,stroke-width:2px
    style External Services fill:#fff3e0,stroke:#f39c12,stroke-width:2px

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
├── .env                  # Environment variables (API keys, DB URL)
├── main.py               # Entry point for the FastAPI backend
├── api.py                # FastAPI application, API endpoints (REST & WebSocket)
├── ai_service.py         # AI logic for NL2SQL and summarization
├── websocket_client.html # Simple HTML/JS client for WebSocket testing
├── etl/
│   ├── __init__.py       # Makes 'etl' a Python package
│   └── etl.py            # ETL logic for processing CSV data
├── models/
│   ├── __init__.py       # Makes 'models' a Python package
│   └── models.py         # SQLAlchemy ORM models for database tables
└── outfox-frontend/             # Your React application directory (assuming this structure)
    ├── public/
    ├── src/
    │   ├── App.js
    │   ├── App.css
    │   └── components/
    │       ├── ChatPage.js
    │       ├── FileUpload.js
    │       ├── GetProvidersPage.js
    │       └── NavigationBar.js
    └── package.json
    └── ...

Setup Instructions
Prerequisites
Python 3.8+

Node.js & npm/yarn (for the React frontend)

PostgreSQL Database: Ensure you have a PostgreSQL server running and access to a database.

1. Clone the Repository
git clone <your-repository-url>
cd healthcare-cost-navigator

2. Backend Setup (FastAPI)
Navigate to the backend root directory (where main.py is located).

cd healthcare-cost-navigator # If you're not already there

a. Create a Python Virtual Environment (Recommended)

python3 -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate

b. Install Python Dependencies

pip install -r requirements.txt
# If you don't have a requirements.txt, you can create one or install manually:
# pip install fastapi uvicorn[standard] sqlalchemy pandas python-dotenv openai psycopg2-binary geopy

c. Create a .env file

In the root directory of your backend (healthcare-cost-navigator/), create a file named .env and add the following variables:

DATABASE_URL="postgresql://user:password@host:port/database_name"
OPEN_AI_API="your_openai_api_key_here"

Replace user, password, host, port, and database_name with your PostgreSQL credentials.

Replace your_openai_api_key_here with your actual OpenAI API key.

d. Run the FastAPI Backend

uvicorn main:app --reload

The backend server will start, typically on http://127.0.0.1:8000. Keep this terminal window open.

3. Frontend Setup (React)
Navigate to your frontend application directory (e.g., healthcare-cost-navigator/frontend/).

cd frontend

a. Install Node.js Dependencies

npm install
# or
yarn install

b. Run the React Development Server

npm start
# or
yarn start

The React app will open in your browser, typically on http://localhost:3000.

Usage Instructions
Once both the backend and frontend servers are running:

1. Database Initialization & Data Upload
Open your browser and go to the FastAPI interactive API documentation: http://127.0.0.1:8000/docs.

Database Table Creation: When you start the FastAPI backend (uvicorn main:app --reload), it automatically attempts to create the hospital_data and star_rating tables in your PostgreSQL database based on your models/models.py. You should see INFO: Database tables created successfully in your backend terminal.

Important: If you make changes to your models.py (e.g., add/remove columns, change column names), you MUST stop the backend, drop the hospital_data and star_rating tables from your PostgreSQL database (using PgAdmin or psql), and then restart the backend to recreate them with the new schema.

Upload Hospital Data:

Find the /upload-hospital-data endpoint in the Swagger UI (http://127.0.0.1:8000/docs).

Click "Try it out".

Click "Choose File" and select your MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv file.

Click "Execute".

Upload Hospital Rating (Generates Mock Ratings):

Find the /upload-hospital-rating endpoint in the Swagger UI.

Click "Try it out".

Click "Choose File" and select the same MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv file. This endpoint uses the provider IDs from this CSV to generate and store mock star ratings.

Click "Execute".

2. Using the Frontend Application (http://localhost:3000)
Home Page (/): After uploading, you'll see the file upload components.

Get Providers Page (/get-providers):

Click the "Get Providers" button in the navigation bar.

Enter a ZIP Code (e.g., 36301, 10001).

Enter a Radius (km) (e.g., 25, 50).

Enter an MS DRG Keyword (e.g., HEART SURGERY, KNEE REPLACEMENT, CHEST PAIN).

Click "Search Providers" to see structured results.

AI Chat Page (/chat):

Click the "AI Chat" button in the navigation bar.

The chat window will attempt to connect to the backend WebSocket. You should see "Connected to AI Chat."

Type your natural language questions in the input field (e.g., "Who has the best ratings for heart surgery near 36301?", "What is the cheapest hospital for pneumonia in 10001?").

Press Enter or click "Send" to get an AI-generated summary.

Try asking an irrelevant question like "What's the weather today?" to see the custom error message.

Troubleshooting Common Issues
psycopg2.errors.UndefinedTable: relation "star_rating" does not exist or UndefinedColumn:

Cause: Your database schema doesn't match your models.py definition, or the table was not created/recreated correctly. This is often due to mismatched column names (e.g., ms_drg_defination vs. ms_drg_definition, provider_zip vs. provider_zip_code, rating vs. overall_rating) or table names (star_ratings vs. star_rating).

Solution:

Stop your FastAPI backend.

In PgAdmin, drop both hospital_data and star_rating tables.

Ensure all your Python files (models/models.py, ai_service.py, etl/etl.py, api.py) have the correct and consistent table and column names as defined in the latest models/models.py.

Restart your FastAPI backend. This will recreate the tables with the correct schema.

Re-upload your CSV data using the /upload-hospital-data and /upload-hospital-rating endpoints in Swagger UI.

openai.OpenAIError: The api_key client option must be set...:

Cause: The OpenAI client is not receiving your API key. This usually means the OPEN_AI_API environment variable is not loaded or not passed correctly to the AIService constructor.

Solution:

Ensure your .env file exists in the backend root and contains OPEN_AI_API="your_key_here".

Verify that api.py correctly reads this variable and passes it to AIService(api_key=OPENAI_API_KEY).

Restart your FastAPI backend.

WebSocket connection to 'ws://localhost:8000/ws/ask/' failed: ... (Frontend Console Error):

Cause: The React frontend cannot establish a connection to the WebSocket endpoint.

Solution:

Is your FastAPI backend running? (Check the terminal).

Is the WebSocket URL correct in ChatPage.js? It should be ws://localhost:8000/ws/ask.

Clear your browser cache and hard refresh the React application page (Ctrl+Shift+R or Cmd+Shift+R). Old cached JavaScript might be trying to connect to a wrong URL.

Check your FastAPI terminal for 403 Forbidden errors on the WebSocket path, which could indicate a URL mismatch or CORS issue.
