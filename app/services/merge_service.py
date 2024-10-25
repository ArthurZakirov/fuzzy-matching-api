from sentence_transformers import SentenceTransformer, util
import pandas as pd
from fuzzywuzzy import process
from tqdm import tqdm

# Load the sentence transformer model once for reuse
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Predefined mappings for complex cases
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
    threshold: int = 0,
    use_embeddings: bool = True,
):
    mapping = []

    for val1 in tqdm(table1[key1].unique()):
        if val1 in mapping_dict:
            match = mapping_dict[val1]
            score = 100  # Predefined mappings have full match
        else:
            if use_embeddings:
                embedding1 = model.encode(val1, convert_to_tensor=True)
                candidates = [
                    (val2, model.encode(val2, convert_to_tensor=True))
                    for val2 in table2[key2].unique()
                ]
                match, score = max(
                    (
                        (val2, util.cos_sim(embedding1, emb2).item() * 100)
                        for val2, emb2 in candidates
                    ),
                    key=lambda x: x[1],
                )
            else:
                match, score = process.extractOne(val1, table2[key2].unique())

            if score < threshold:
                continue

        mapping.append((val1, match, score))

    mapping_df = pd.DataFrame(mapping, columns=[key1, key2, "similarity"])
    merged_df = table1.merge(mapping_df[[key1, key2]], on=key1, how="left").merge(
        table2, on=key2, how="left"
    )
    return merged_df
