from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import QueryRequest, QueryResponse
from app.services import process_query, get_stats

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    try:
        sql, result, execution_time = process_query(request.question)
        return QueryResponse(
            question=request.question,
            generated_sql=sql,
            result=result,
            execution_time_ms=execution_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
def stats_endpoint():
    try:
        stats = get_stats()
        return JSONResponse(content={
            "total_queries": stats["total_queries"],
            "common_keywords": stats["common_keywords"],
            "slowest_query": stats["slowest_query"],
            "queries": stats["queries"]
        })
    except Exception:
        return JSONResponse(content={
            "total_queries": 0,
            "common_keywords": [],
            "slowest_query": None,
            "queries": []
        })