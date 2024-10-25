from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import pandas as pd
from io import StringIO
from fuzzywuzzy import process
from sentence_transformers import SentenceTransformer, util

# Load sentence transformer model
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

app = FastAPI()

# Predefined dictionary for mappings with strong differences
mapping_dict = {
    "GER": "Deutschland",
    "DEU": "Deutschland",
    "ESP": "España",
    "USA": "United States",
}


def merge_with_advanced_fuzzy_match(
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    key1: str,
    key2: str,
    threshold: int = 80,
    use_embeddings: bool = True,
):
    mapping = []

    for val1 in table1[key1].unique():
        # Check dictionary first
        if val1 in mapping_dict:
            match = mapping_dict[val1]
            score = 100  # Assume perfect match from dictionary
        else:
            # Fallback to fuzzy matching or embedding-based similarity
            if use_embeddings:
                # Generate embeddings
                embedding1 = model.encode(val1, convert_to_tensor=True)
                candidates = [
                    (val2, model.encode(val2, convert_to_tensor=True))
                    for val2 in table2[key2].unique()
                ]

                # Find best match by cosine similarity
                match, score = max(
                    (
                        (val2, util.cos_sim(embedding1, emb2).item() * 100)
                        for val2, emb2 in candidates
                    ),
                    key=lambda x: x[1],
                )
            else:
                # Use fuzzy matching as fallback
                match, score = process.extractOne(val1, table2[key2].unique())

            if score < threshold:
                continue  # Skip matches below threshold

        mapping.append((val1, match, score))

    # Create DataFrame for mapping
    mapping_df = pd.DataFrame(mapping, columns=[key1, key2, "similarity"])
    merged_df = table1.merge(mapping_df[[key1, key2]], on=key1, how="left").merge(
        table2, on=key2, how="left"
    )
    return merged_df


@app.post("/merge-tables/")
async def merge_tables(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    key1: str = Form(...),
    key2: str = Form(...),
    threshold: Optional[int] = Form(80),
    use_embeddings: Optional[bool] = Form(True),
):
    # Read CSV files
    table1 = pd.read_csv(StringIO((await file1.read()).decode("utf-8")))
    table2 = pd.read_csv(StringIO((await file2.read()).decode("utf-8")))

    # Perform advanced fuzzy matching merge
    result = merge_with_advanced_fuzzy_match(
        table1, table2, key1, key2, threshold, use_embeddings
    )

    return result.to_csv(index=False)
