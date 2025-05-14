import os
import openai
import json
import pandas as pd
# The following three lines are used for loading api key from local file system
from dotenv import load_dotenv, find_dotenv
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

def say_hello_gpt4_1():
    """
    Sends a 'Hello' message to the GPT-4.1 model using openai-python ≥1.0.0
    and prints the assistant's reply to the terminal.
    """
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")  # correct instantiation  [oai_citation:14‡Stack Overflow](https://stackoverflow.com/questions/77505030/openai-api-error-you-tried-to-access-openai-chatcompletion-but-this-is-no-lon?utm_source=chatgpt.com)
    )
    response = client.chat.completions.create( # invoke the chat endpoint correctly  [oai_citation:15‡Stack Overflow](https://stackoverflow.com/questions/77505030/openai-api-error-you-tried-to-access-openai-chatcompletion-but-this-is-no-lon?utm_source=chatgpt.com) [oai_citation:16‡OpenAI Community](https://community.openai.com/t/how-to-pass-prompt-to-the-chat-completions-create/592629?utm_source=chatgpt.com)
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.0,
        max_tokens=50
    )
    reply = response.choices[0].message.content.strip()  # extract the reply  [oai_citation:17‡Stack Overflow](https://stackoverflow.com/questions/77505030/openai-api-error-you-tried-to-access-openai-chatcompletion-but-this-is-no-lon?utm_source=chatgpt.com)
    print("GPT-4.1 says:", reply) 
    return None
def select_label_columns(df: pd.DataFrame) -> tuple[int, int]:
    """
    Calls GPT-4.1 to choose the best label column for regression and classification.

    :param df: A pandas DataFrame with at least 3 columns (column 0 is ID).
    :return: A tuple (regression_label_index, classification_label_index).
    """
    # Load .env from the Flask app root
    load_dotenv(find_dotenv())
    PROMPT = """
You are given an input JSON object representing a slice of a larger tabular dataset:

{
  "data": [...]
}

Task:
1. Treat each element in the inner lists as a feature column (0-based indexing).
2. Column 0 is an ID column and must be ignored when selecting label columns.
3. Analyze the remaining columns and determine:
   - The best feature column index to use as the label for a regression task.
   - The best feature column index to use as the label for a classification task.
4. Report only two integers separated by a single space: first the regression label column index, then the classification label column index.

Output rules:
- Your entire response must be exactly two integers separated by a single space (e.g., `2 5`) with no additional text, punctuation, or whitespace.
- Do not include explanations, quotes, or code fences.

Dataset assumptions:
- The table has at least 3 and at most 100 columns.
- The input `data` is a JSON array of rows converted from a pandas DataFrame.
"""
    # Instantiate the OpenAI client
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Prepare the payload
    payload = {"data": df.values.tolist()}
    user_message = json.dumps(payload)

    # Query GPT-4.1
    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.0,
        max_tokens=8
    )

    # Parse the two integers from the response
    content = resp.choices[0].message.content.strip()
    parts = content.split()
    if len(parts) != 2:
        raise ValueError(f"Unexpected response format: '{content}'")
    return int(parts[0]), int(parts[1])

if __name__ == "__main__":
    validate_keychain()
    say_hello_gpt4_1()
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "age": [23, 45, 31],
        "income": [40000, 80000, 60000],
        "purchased": [0, 1, 0]
    })
    print("====================Test 1 begin====================")
    reg_idx, cls_idx = select_label_columns(df)
    print(f"Regression label column: {reg_idx}")
    print(f"Classification label column: {cls_idx}")
    print("====================Test 2 begin====================")
    df = pd.read_csv("/Users/yanchenyu/Documents/MachineLearning_Datafolder/HousePriceDataset/data.csv")
    reg_idx, cls_idx = select_label_columns(df.head(20))
    print(f"Regression label column: {reg_idx}")
    print(f"Classification label column: {cls_idx}")