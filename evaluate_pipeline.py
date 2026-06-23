import pandas as pd

def run_precision_recall_analysis():
    print("📊 Loading Ground-Truth Comparison Engine...")
    
    # 1. Define Ground Truth: The absolute reality of who is actually a match
    # (e.g., We know manually that REC_001/REC_002 and REC_003/REC_004 are the same people)
    ground_truth = {
        ("REC_001", "REC_002"): True,
        ("REC_003", "REC_004"): True,
        ("REC_001", "REC_003"): False, # Completely different people
        ("REC_002", "REC_004"): False  # Completely different people
    }
    
    # 2. Simulate Pipeline Predictions at different Threshold Levels
    # This proves to an interviewer how threshold tuning directly affects data integrity
    scenarios = {
        "Low Threshold (>0.50)": {
            ("REC_001", "REC_002"): True,   # Correct match (True Positive)
            ("REC_003", "REC_004"): True,   # Correct match (True Positive)
            ("REC_001", "REC_003"): True,   # FALSE POSITIVE (Mixed up strangers)
            ("REC_002", "REC_004"): False
        },
        "Optimized Threshold (>0.85)": {
            ("REC_001", "REC_002"): True,   # Correct match (True Positive)
            ("REC_003", "REC_004"): True,   # Correct match (True Positive)
            ("REC_001", "REC_003"): False,  # Correctly blocked!
            ("REC_002", "REC_004"): False
        }
    }
    
    print("\n⚖️ Computing Match Quality Matrices:")
    print("-" * 60)
    
    for configuration, predictions in scenarios.items():
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        
        for pair, predicted_match in predictions.items():
            actual_match = ground_truth[pair]
            
            if predicted_match and actual_match:
                true_positives += 1
            elif predicted_match and not actual_match:
                false_positives += 1
            elif not predicted_match and actual_match:
                false_negatives += 1
            elif not predicted_match and not actual_match:
                true_negatives += 1
                
        # Calculate Precision and Recall metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n⚙️ Configuration: {configuration}")
        print(f"   ▫️ Precision (Data Accuracy):  {precision * 100:.1f}%")
        print(f"   ▫️ Recall (Duplication Catch): {recall * 100:.1f}%")
        print(f"   ▫️ F1-Score (Balanced Quality): {f1_score * 100:.1f}%")
        print(f"   ▫️ Intercepted False Positives: {false_positives} catastrophic link errors.")

if __name__ == "__main__":
    run_precision_recall_analysis()
