import openai
from dotenv import load_dotenv
import os
import faiss
import numpy as np
import array

load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

# Handle message upload.

print(f"Please enter the file name with extension from the data folder you are using:")
fileName = input();
print(f"{fileName}");
fileName = "data/"+fileName;
messages = []

HARD_CAP = 2000
curr_amt = 0

with open(fileName, "r", encoding="utf-8") as f:
    for line in f:
        if curr_amt == HARD_CAP:
            break
        curr_amt+=1

        split_ = line.split("-/-/- ")
        split_.pop(0);
        sanitized = '-'.join(split_)
        sanitized = sanitized.replace('\n','')
        if (type(sanitized) == str and len(sanitized) != 0) :
            messages.append(sanitized)
print(messages)


def embed_messages(messages):
    response = openai.embeddings.create(
        input=messages,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

embeddings = embed_messages(messages)
embedding_matrix = np.array(embeddings).astype("float32")
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(embedding_matrix)


def retrieve_similar(query, messages, index):
    query_embedding = embed_messages([query])[0]
    query_vector = np.array([query_embedding]).astype("float32")
    _, indices = index.search(query_vector, k=3)
    return [messages[i] for i in indices[0]]


def generate_response(query, retrieved_messages):
    context = "\n".join(retrieved_messages)
    prompt = f"Based on the following messages from Kayne Whitney:\n{context}\nRespond to: {query}"

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Kayne Whitney, a cybersecurity expert and student at UW-Stout. You will be given relevant messages you have sent in the past. You will generate a reply to mimic the speaking pattern (length, concepts used, language) of yourself. Make it as close as possible to what you would say based on your past messages. Try your best to reference at least one of the past messages you've sent."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Example usage
query = "What should we do about the new malware alert?"
retrieved = retrieve_similar(query, messages, index)
response = generate_response(query, retrieved)

print("Retrieved Messages:")
for msg in retrieved:
    print("-", msg)

print("\nAI Response:")
print(response)
