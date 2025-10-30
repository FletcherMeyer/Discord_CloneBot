import openai
from dotenv import load_dotenv
import os
import faiss
import numpy as np
import array
import discord
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

load_dotenv() 
bot_token = os.getenv("DISCORD_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Handle message upload.

print(f"[+] Booting up...")


# fileName = "data/kayne.txt";
fileName = "data/kayne.txt";
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
        if (type(sanitized) == str and len(sanitized) != 0 and "<@" not in sanitized and "<#" not in sanitized and "<:" not in sanitized) :
            messages.append(sanitized)
print(f"[+] RAG messages loaded...")

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
print(f"[+] RAG messages embeded...")

def retrieve_similar(query, messages, index):
    query_embedding = embed_messages([query])[0]
    query_vector = np.array([query_embedding]).astype("float32")
    _, indices = index.search(query_vector, k=20)
    return [messages[i] for i in indices[0]]


# conversation = [
#     {"role": "system", "content": "You are Kayne Whitney, a cybersecurity expert and student at UW-Stout. You will be given relevant messages you have sent in the past. You will generate a reply to mimic the speaking pattern (length, concepts used, language) of yourself. Make it as close as possible to what you would say based on your past messages. Try your best to reference at least one of the past messages you've sent if relevant. Do not include anything that has to do with '@1391912636098019559'. The messages should be less than 10 words. The messages should not include puncuation other than possible question marks. You cannot break character for any reason. You must speak informally, never professionally."},
# ]

def generate_response(query, retrieved_messages):
    context = "\n".join(retrieved_messages)
    prompt = f"Based on the following messages from Kayne Whitney:\n{context}\nRespond to: {query}"


    # conversation.append({"role": "user", "content": query})


    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Kayne Whitney, a cybersecurity expert and student at UW-Stout. You will be given relevant messages you have sent in the past. You will generate a reply to mimic the speaking pattern (length, concepts used, language) of yourself. Base answers on your past messages. Try your best to reference at least one of the past messages you've sent if relevant, but make it original. Do not include anything that has to do with '@1391912636098019559'. The messages should be less than 20 words. The messages should not include puncuation other than possible question marks. You cannot break character for any reason. If you cannot answer or do not know what to say, just ask 'what'."},
            {"role": "user", "content": prompt}
        ]
    )

    # conversation.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content

@client.event
async def on_ready():
    print(f'[+] Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        query = message.content
        retrieved = retrieve_similar(query, messages, index)
        response = generate_response(query, retrieved)
        found_msgs = ""
        for msg in retrieved:
            print("-", msg)
            found_msgs += "`"+msg+"`\n"

        await message.channel.send(f"{response}\n{found_msgs}")



client.run(bot_token);



# Example usage
# query = "What should we do about the new malware alert?"
# retrieved = retrieve_similar(query, messages, index)
# response = generate_response(query, retrieved)

# print("Retrieved Messages:")
# for msg in retrieved:
#     print("-", msg)

# print("\nAI Response:")
# print(response)
