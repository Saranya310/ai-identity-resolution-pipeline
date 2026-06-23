import os
import pandas as pd

def run_identity_pipeline():
    print("🚀 Initializing Identity Resolution Pipeline...")
    
    # Securely retrieve the API key from the system environment instead of hardcoding it
    api_key = os.getenv("OPENAI_API_KEY", "mock_fallback_key")
    
    if api_key == "mock_fallback_key":
        print("⚠️ No live API key detected. Running in safe local simulation mode.")
    else:
        print("🔐 Live API credentials loaded successfully.")

    # 1. Ingest Data Simulation
    data = [
        {"id": "REC_001", "name": "Saranya Achanti", "phone": "123-456-7890", "zip": "500081"},
        {"id": "REC_002", "name": "S. Achanti", "phone": "123.456.7890", "zip": "500081"},
        {"id": "REC_003", "name": "John Doe", "phone": "987-654-3210", "zip": "90210"},
        {"id": "REC_004", "name": "Jon Doe", "phone": "", "zip": "90210"}
    ]
    df = pd.DataFrame(data)
    print(f"📥 Loaded {len(df)} ingestion records.")

    # 2. Standardization Layer
    print("🧼 Executing PII Standardization Rulebook...")
    df['clean_phone'] = df['phone'].str.replace(r'\D', '', regex=True)
    df['clean_name'] = df['name'].str.lower().str.strip()

    # 3. Hybrid Resolution Evaluation
    print("🧠 Evaluating Record Links via Hybrid Resolution...")
    matches = []
    
    # Step A: Deterministic Track (Phone Match)
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            rec1, rec2 = df.iloc[i], df.iloc[j]
            
            # Blocking Guardrail: Only evaluate if they share a Zip Code map
            if rec1['zip'] != rec2['zip']:
                continue
                
            if rec1['clean_phone'] and rec1['clean_phone'] == rec2['clean_phone']:
                matches.append((rec1['id'], rec2['id'], 1.0, "Deterministic (Exact Phone)"))
            else:
                # Step B: Probabilistic Simulation Fallback (Name Ambiguity)
                if "achanti" in rec1['clean_name'] and "achanti" in rec2['clean_name']:
                    matches.append((rec1['id'], rec2['id'], 0.92, "Probabilistic (Semantic Name Match)"))
                elif "doe" in rec1['clean_name'] and "doe" in rec2['clean_name']:
                    matches.append((rec1['id'], rec2['id'], 0.78, "Probabilistic (Low Confidence - Dropped)"))

    # 4. Enforce Safety Threshold Guardrail (Target: 0.85)
    print("🛡️ Applying Threshold Confidence Guardrails (>0.85)...")
    final_links = [m for m in matches if m[2] >= 0.85]

    print("\n🎯 FINAL RESOLVED IDENTITY LINKS:")
    print("=" * 65)
    for link in final_links:
        print(f"🔗 Match Confirmed: {link[0]} ⇄ {link[1]} | Confidence: {link[2]} | Strategy: {link[3]}")
    print("=" * 65)

if __name__ == "__main__":
    run_identity_pipeline()
