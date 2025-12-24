from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.controllers.query_controller import QueryController

router = APIRouter()

# Initialize the controller
query_controller = QueryController()

class QueryRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask(request: QueryRequest):
    try:
        result = await query_controller.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))