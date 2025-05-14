import os

import openai


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

def say_hello2model(model_name="gpt-4.1-mini-2025-04-14"):
    api_key= os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API key not found. Please set OPENAI_API_KEY in .env.")
        return None

    client = openai.OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
    model=model_name,
    store=True,
    messages=[
        {"role": "user", "content": "Hi, who are you"}
    ]
    )

    print(completion.choices[0].message)
    return None
def GPT_column_suggestion(input:str):

    # Set your API key, remember to replace the SECRET-KEY into our own before demostration
    api_key =  os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API key not found. Please set OPENAI_API_KEY in .env.")
        return None
    
    openai.api_key = api_key


    # Example dataset slice (replace with your actual JSON)
    dataset_json = input

    # Prompt from previous step
    prompt_instructions = (
        "You are given an input JSON object that represents a slice of a larger tabular dataset.\n\n"
        "{\n"
        '  "data": [...],\n'
        '  "label_column": <int>\n'
        "}\n\n"
        "Task:\n"
        "1. Treat each position in the inner lists as a separate feature column (0‑based indexing).\n"
        "2. Using only the information provided, identify the single feature column that is most valuable "
        "to analyze with respect to the label column.\n"
        "3. Report only the zero‑based index of that column.\n\n"
        "Output rules:\n"
        "- Your entire response must be just one integer (e.g., 4) with no additional text, punctuation, or whitespace.\n"
        "- Do not include explanations, quotes, or code fences.\n\n"
        "Dataset assumptions: The table has at least 3 and at most 100 columns."
    )
    print("=======================GPT analysation process begin, please be patient===============================")
    # Build the messages payload
    messages = [
        {"role": "system", "content": "You are a helpful data analysation assistant."},
        {"role": "user", "content": prompt_instructions},
        {"role": "user", "content": dataset_json}
    ]

    # Call the model
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0
    )

    # Extract the predicted column index
    predicted_column_index = response.choices[0].message.content.strip()
    print("=======================GPT analysation process done, dumping response right now===============================")
    # print("Column index worth analyzing:", predicted_column_index)
    if isinstance(predicted_column_index, str):
        try:
            predicted_column_index = int(predicted_column_index)
        except ValueError:
            return None
    
    return predicted_column_index

if __name__ == "__main__":
    say_hello2model()