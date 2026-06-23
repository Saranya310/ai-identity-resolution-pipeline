import os
import json
import pandas as pd
from typing import Dict, List, Tuple
from openai import OpenAI

class ProductionIdentityPipeline:
    def __init__(self, confidence_threshold: float = 0.85):
        """
        Initializes the pipeline with a fallback mock client if no API key exists.
        """
        self.threshold = confidence_threshold
        
        # Checking if an API key actually exists in the terminal env
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            self.client = OpenAI(api_key=env_key)
            self.mock_mode = False
        else:
            print("⚠️ No OPENAI_API_KEY found. Activating simulated pipeline engine mode...")
            self.client = None
            self.mock_mode = True

    def normalize_pii(self, text: str) -> str:
        """
        Standardizes text variations to eliminate baseline formatting noise.
        """
        if pd.isna(text) or not str(text).strip():
            return ""
        return str(text).strip().lower()

    def clean_phone(self, phone: str) -> str:
        """
        Extracts raw numeric characters to standardize varied phone formats.
        """
        if pd.isna(phone):
            return ""
        return "".join(filter(str.isdigit, str(phone)))

    def generate_blocking_key(self, row: pd.Series) -> str:
        """
        Step 1: Creates an optimized blocking key using Postal Code metadata 
        to avoid an N^2 comparison explosion across datasets.
        """
        zip_str = str(row.get("zip", "")).strip()
        return zip_str[:3] if len(zip_str) >= 3 else "UNKNOWN"

    def is_deterministic_match(self, rec1: Dict, rec2: Dict) -> bool:
        """
        Step 2: Rule-based evaluation engine checking unique identifiers.
        """
        if rec1["email"] and rec1["email"] == rec2["email"]:
            return True
        if rec1["phone"] and rec1["phone"] == rec2["phone"]:
            return True
        return False

    def evaluate_probabilistic_llm(self, rec1: Dict, rec2: Dict) -> Tuple[float, str]:
        """
        Dispatches ambiguous records to the LLM semantic layer, with a built-in local simulation.
        """
        # If no API key is available, simulate a perfect match response locally for testing
        if self.mock_mode:
            if "achanti" in rec1["name"] and "achanti" in rec2["name"]:
                return 0.92, "Simulated Match: Address variations recognized; initials resolve cleanly to surname."
            return 0.35, "Simulated Non-Match: Distinct demographic details."

        prompt = f"""
        You are an elite Identity Resolution systems engineer auditing data deduplication.
        Analyze these two consumer records and calculate the mathematical likelihood that they represent the SAME individual.

        Record A:
        - Name: {rec1['name']}
        - Address: {rec1['address']}
        - Email: {rec1['email']}
        - Phone: {rec1['phone']}

        Record B:
        - Name: {rec2['name']}
        - Address: {rec2['address']}
        - Email: {rec2['email']}
        - Phone: {rec2['phone']}

        Respond ONLY with a valid JSON object matching this schema. Do not include markdown code block formatting or backticks:
        {{
            "confidence_score": <float between 0.0 and 1.0>,
            "reasoning": "<clear sentence explaining your entity resolution matching deduction>"
        }}
        """

        try:
            # Invoking the model with JSON output enforcement
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            payload = json.loads(response.choices[0].message.content)
            return float(payload.get("confidence_score", 0.0)), payload.get("reasoning", "No reason provided.")
        except Exception as e:
            return 0.0, f"API Exception encountered during pipeline execution: {str(e)}"

    def process_linkage(self, df: pd.DataFrame) -> List[Dict]:
        """
        Step 4: Drives the full hybrid identity engine over the incoming records dataframe.
        """
        # Data standardization step
        standardized_records = []
        for _, row in df.iterrows():
            standardized_records.append({
                "id": row["id"],
                "name": self.normalize_pii(row["name"]),
                "address": self.normalize_pii(row["address"]),
                "email": self.normalize_pii(row["email"]),
                "phone": self.clean_phone(row["phone"]),
                "block_key": self.generate_blocking_key(row)
            })

        results = []
        num_records = len(standardized_records)

        # Cross-compare records clustered within identical blocks
        for i in range(num_records):
            for j in range(i + 1, num_records):
                r1 = standardized_records[i]
                r2 = standardized_records[j]

                # Skip comparison if they do not belong to the same blocking domain
                if r1["block_key"] != r2["block_key"]:
                    continue

                # Test Step 2: Deterministic Short-Circuit
                if self.is_deterministic_match(r1, r2):
                    results.append({
                        "record_id_a": r1["id"], "record_id_b": r2["id"],
                        "is_linked": True, "score": 1.0,
                        "method": "deterministic", "reasoning": "Exact matching identifier match."
                    })
                    continue

                # Test Step 3: Probabilistic LLM Layer Evaluation
                score, reasoning = self.evaluate_probabilistic_llm(r1, r2)
                is_linked = score >= self.threshold

                results.append({
                    "record_id_a": r1["id"], "record_id_b": r2["id"],
                    "is_linked": is_linked, "score": score,
                    "method": "probabilistic_llm", "reasoning": reasoning
                })

        return results

# --- Test Data Instantiation & Execution Loop ---
if __name__ == "__main__":
    # Formulating messy real-world datasets with nicknames, typos, and omitted attributes
    raw_consumer_data = [
        {"id": "REC_001", "name": "Saranya Achanti", "address": "123 Main St", "email": "saranya@test.com", "phone": "469-468-4849", "zip": "30040"},
        {"id": "REC_002", "name": "S. Achanti", "address": "123 Main Street", "email": "", "phone": "", "zip": "30040-112"},
        {"id": "REC_003", "name": "John Doe", "address": "555 Pine Rd", "email": "john.doe@email.com", "phone": "5551234567", "zip": "90210"},
        {"id": "REC_004", "name": "Jonathan Doe", "address": "555 Pine Road", "email": "john.doe@email.com", "phone": "", "zip": "90210"}
    ]

    input_df = pd.DataFrame(raw_consumer_data)
    print("🚀 Initializing Production Identity Resolution Framework Data Stream...")
    
    # Initialize the engine with our targeted confidence evaluation boundary
    pipeline = ProductionIdentityPipeline(confidence_threshold=0.85)
    linkage_report = pipeline.process_linkage(input_df)

    print("\n📊 Identity Resolution Evaluation Report:")
    print(json.dumps(linkage_report, indent=4))