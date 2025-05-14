"""
gpt_result_analysis.py

Utility helpers that send a result JSON from your local ML workflow
to OpenAI GPT-4.1-mini for human-readable feedback.

Three entry-points (all return a string):
    • linear_regression_assistant(result_json)
    • svm_classifier_assistant(result_json)
    • kmeans_assistant(result_json)

Set OPENAI_API_KEY here only for demo purposes; replace with your own
secure loading strategy in production.
"""
import os
from dotenv import load_dotenv
import json
import openai
load_dotenv()  # load from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_keychain():
    import os
    import openai

    # 1 – Make sure the variable is populated
    key = os.getenv("OPENAI_API_KEY")      # or whatever var name you used
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set in your environment")

    openai.api_key = key                  # or openai.api_key = "sk-..."

    # 2 – Ping a lightweight endpoint to confirm the key works
    try:
        # list available models is the cheapest “health check”
        _ = openai.models.list()
        print("✅  OpenAI API key is set correctly and accepted by the server.")
    except openai.AuthenticationError as e:
        raise RuntimeError(
            "❌  The key is set but was rejected (wrong key or expired token)."
        ) from e

# ---------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------
def _ask_gpt(prompt: str, data: dict) -> str:
    """
    Low-level caller that feeds <prompt> and <data> to GPT-4.1-mini
    and returns the model’s reply (stripped).
    """
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user",   "content": prompt},
        {"role": "user",   "content": json.dumps(data, ensure_ascii=False)}
    ]

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------
_LINEAR_PROMPT = """
You will see a JSON block that summarizes the evaluation of a LinearRegression model.

JSON schema
-----------
model_name        : do NOT analyse this key
MSE_value         : float ≥ 0 (lower is better)
speed_mode        : One of {"Fast","Balance","High Precision"}
label_index       : index of target column in the original dataset
has_header        : do NOT analyse this key
precision_value   : do NOT analyse this key
plot_path         : do NOT analyse this key

Task
----
1. Decide whether the result is **good**:
     • Treat it as GOOD if MSE_value ≤ 0.10
       (feel free to adjust threshold slightly if clearly appropriate).
2. If GOOD:
     • Begin by congratulating the user (one sentence).
     • Briefly explain what MSE_value means and why the obtained value is good.
     • Mention speed_mode and label_index.
3. If NOT GOOD:
     • Explain possible reasons for high error (data quality, feature scale,
       wrong label, insufficient data, inappropriate speed_mode etc.).
     • Suggest concrete actions (feature engineering, more data, normalization,
       model variants, trying High Precision speed_mode, etc.).
4. Keep the response friendly, actionable, and under ~150 words.
5. Do **NOT** discuss or interpret the keys flagged “do NOT analyse”.

Output format
-------------
Plain prose (no JSON, no code fences).
"""

_SVM_PROMPT = """
You will see a JSON block that summarizes the evaluation of an SVM classifier.

JSON schema
-----------
model_name        : do NOT analyse this key
Precision_value   : float in [0,1]
Accuracy_value    : float in [0,1]
Recall_value      : float in [0,1]
F1_score_value    : float in [0,1]
plot_path         : do NOT analyse this key

Task
----
1. Consider the model GOOD if **all** of Accuracy_value, Recall_value,
   and F1_score_value are ≥ 0.80.
2. If GOOD:
     • Congratulate the user.
     • Summarise what each metric represents and spotlight the strong ones.
3. If NOT GOOD:
     • Identify which metric(s) are weak.
     • Explain what can hurt these metrics (class imbalance, over-/under-fitting,
       feature selection, kernel choice, hyper-parameters).
     • Provide 2-3 actionable improvement tips (e.g., grid search on C & gamma,
       resampling, feature scaling).
4. No commentary on model_name or plot_path.
5. Limit to ~160 words; write as helpful prose.

Output format
-------------
Plain prose, no code or JSON.
"""

_KMEANS_PROMPT = """
You will see a JSON block that summarizes the evaluation of a KMeans clustering run.

JSON schema
-----------
model_name : do NOT analyse this key
MSE        : float ≥ 0 (inertia; lower is better)  • may be None
precision  : float in [0,1]                        • may be None

Task
----
1. Treat the run as GOOD if BOTH metrics are present **and**:
       MSE ≤ 0.10  AND  precision ≥ 0.80
   If either metric is missing, or thresholds not met, treat as NOT GOOD.
2. If GOOD:
     • Congratulate briefly.
     • Explain why low inertia (MSE) and high precision indicate tight,
       well-separated clusters.
3. If NOT GOOD:
     • State which metric is missing or sub-par.
     • Offer practical tuning ideas:
         – choose better number of clusters (k),
         – scale features,
         – use k-means++ init,
         – more iterations, etc.
4. Do not analyse model_name.
5. Keep answer ≤ 150 words, clear and friendly.

Output format
-------------
Plain prose.
"""


# ---------------------------------------------------------------------
# Public helper functions
# ---------------------------------------------------------------------
def linear_regression_assistant(result_json: dict) -> str:
    """
    Analyse LinearRegression results via GPT-4.1-mini and return advice.
    """
    return _ask_gpt(_LINEAR_PROMPT, result_json)


def svm_classifier_assistant(result_json: dict) -> str:
    """
    Analyse SVM classifier results via GPT-4.1-mini and return advice.
    """
    return _ask_gpt(_SVM_PROMPT, result_json)


def kmeans_assistant(result_json: dict) -> str:
    """
    Analyse KMeans clustering results via GPT-4.1-mini and return advice.
    """
    return _ask_gpt(_KMEANS_PROMPT, result_json)
def json_loading(file_path:str):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data
if __name__ == "__main__":
    validate_keychain()
    path_linear1_json = "../../test_json/Linear1.json"
    path_linear2_json = "../../test_json/Linear2.json"
    path_svm1_json = "../../test_json/SVM1.json"
    path_Kmeans1_json = "../../test_json/Kmeans1.json"
    # print(json_loading(linear1_json))
    linear1_json = json_loading(path_linear1_json)
    linear2_json = json_loading(path_linear2_json)
    svm1_json = json_loading(path_svm1_json)
    kmeans1_json = json_loading(path_Kmeans1_json)
    print(linear_regression_assistant(linear1_json), end="\n")
    print()
    print(linear_regression_assistant(linear2_json), end="\n")
    print()
    print(svm_classifier_assistant(svm1_json), end="\n")
    print()
    print(kmeans_assistant(kmeans1_json), end="\n GPT testing is done")
