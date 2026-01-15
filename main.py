"""FastAPI backend for EcoTrack - Agentic AI Architecture"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware

from schemas import AnalyzeRequest, AnalyzeResponse,HistoryItem
from agents.supervisor import SupervisorAgent
from supabase_client import get_supabase_client
import jwt


# -------------------------
# App Initialization
# -------------------------

app = FastAPI(
    title="EcoTrack Backend",
    description="Agentic AI backend for carbon footprint analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://eco-track-ai-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor = SupervisorAgent()


# -------------------------
# Auth Helper
# -------------------------

def get_access_token(authorization: str = Header(...)) -> str:
    """
    Extracts Bearer token from Authorization header.
    Raises HTTPException if invalid.
    """
    if not authorization or " " not in authorization:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    token_type, token = authorization.split(" ", 1)
    if token_type.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth token type")
    return token


def get_user_id_from_token(token: str) -> str:
    """
    Decodes JWT and returns the user ID (sub).
    Raises HTTPException if invalid.
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# -------------------------
# Routes
# -------------------------

@app.get("/")
async def root():
    return {
        "message": "EcoTrack Backend API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze carbon footprint",
            "/calculate": "POST - Analyze + persist history"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Pure analysis endpoint (no persistence)
    """
    try:
        return supervisor.analyze(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate", response_model=AnalyzeResponse)
async def calculate(
    request: AnalyzeRequest,
    access_token: str = Depends(get_access_token)
) -> AnalyzeResponse:
    """
    Analyze and persist analysis to Supabase with user ID
    """
    try:
        # Extract user ID from JWT
        user_id = get_user_id_from_token(access_token)

        # Run agentic analysis (already returns AnalyzeResponse)
        response = supervisor.analyze(request)

        # Inject user_id into response (no dict unpacking)
        response.user_id = user_id

        # Persist to Supabase
        supabase = get_supabase_client(access_token)
        supabase.table("eco_analysis").insert({
            "user_id": user_id,
            "input_data": request.model_dump(),
            "ai_output": response.model_dump()
        }).execute()

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", response_model=list[HistoryItem])
async def get_history(
    access_token: str = Depends(get_access_token)
):
    """
    Fetch logged-in user's carbon footprint history.
    RLS ensures only user's own data is returned.
    """
    try:
        # Create user-scoped Supabase client
        supabase = get_supabase_client(access_token)

        # Query user's history (RLS enforced)
        response = (
            supabase
            .table("eco_analysis")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# -------------------------
# Run Local Server
# -------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
