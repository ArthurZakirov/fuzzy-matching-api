from fastapi import APIRouter, File, UploadFile, Form, Response
from app.services.merge_service import merge_with_advanced_fuzzy_match
import pandas as pd
from io import StringIO

router = APIRouter()


@router.post("/merge-tables/")
async def merge_tables(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    key1: str = Form(...),
    key2: str = Form(...),
    threshold: int = Form(80),
    use_embeddings: bool = Form(True),
):
    # Read CSV files
    table1 = pd.read_csv(StringIO((await file1.read()).decode("utf-8")))
    table2 = pd.read_csv(StringIO((await file2.read()).decode("utf-8")))

    # Perform the merge using the advanced fuzzy matching
    result = merge_with_advanced_fuzzy_match(
        table1, table2, key1, key2, threshold, use_embeddings
    )

    # Return merged DataFrame as CSV
    result_csv = result.to_csv(index=False)
    return Response(content=result_csv, media_type="text/csv")
