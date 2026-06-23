# AI-Augmented Identity Resolution Pipeline (Snowflake Scale-Out Blueprint)

## 📌 Project Overview
An end-to-end data engineering blueprint designed to resolve and deduplicate messy customer identity data (PII) at scale. This project implements a high-performance **Hybrid Matching Engine** that combines rapid, cost-effective rule-based deterministic matching with advanced probabilistic semantic matching powered by Large Language Models (LLMs)[cite: 192, 204].

Additionally, this architecture outlines how this localized Python workload seamlessly scales out into the **Snowflake Data Cloud** utilizing native Snowpark DataFrames, Change Data Capture (CDC) Streams, and automated execution Tasks[cite: 67, 77, 80, 276].

---

## 🏗️ Core Architecture & Data Flow

1. **Standardization & PII Sanitization:** Ingests dirty data streams and strips formatting noise (lowercasing strings, trimming whitespace padding, and extracting numeric digits from phone formatting)[cite: 279].
2. **Computational Blocking Keys:** Groups records by localized geographical tags (e.g., 3-digit Zip Code blocks) to completely avoid an $O(N^2)$ cross-comparison calculation explosion[cite: 281].
3. **Deterministic Fast-Track:** Immediately links records sharing exact unique identifiers (phone numbers or emails) in a fraction of a millisecond, completely bypassing the AI layer to conserve operational costs[cite: 284].
4. **Probabilistic AI Layer:** Cascades ambiguous records (e.g., matching surnames/addresses but misspelled or initialed first names) to a structured LLM payload to evaluate semantic context[cite: 286, 287].
5. **Threshold Safety Guardrails:** Evaluates model confidence scores against a tuned execution threshold of `0.85` to aggressively safeguard the destination database against false-positive household clusters[cite: 291].

---

## ❄️ Production Enterprise Scale-Out (Snowflake Theory)
While this repository contains a fully executable Python prototype simulating the architecture locally, the system is designed to deploy natively within Snowflake:
* **Snowpark DataFrames:** Replaces local memory-bound processes with distributed, lazy-evaluation processing across virtual warehouses[cite: 67].
* **Snowflake Streams & Tasks:** Automates continuous Change Data Capture (CDC) and cron-cadence scheduling for continuous data asset refreshes[cite: 77, 80].
* **Dynamic Data Masking:** Enforces strict data governance policies, protecting sensitive PII fields from unauthorized visualization while background engines run linking graphs[cite: 81, 82].

---

## 🏃‍♂️ Local Quickstart (Simulation Prototype)

### 1. Clone the repository and install dependencies
\`\`\`bash
git clone https://github.com/Saranya310/ai-identity-resolution-pipeline.git
cd ai-identity-resolution-pipeline
conda activate identity_env
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment & Run
To test live API integrations, export your token:
\`\`\`bash
export OPENAI_API_KEY="your-api-key-here"
python pipeline.py
\`\`\`
*Note: If no API key is detected, the framework automatically activates a safe, local fallback simulation mode to evaluate the data pipelines end-to-end for free[cite: 496].*
