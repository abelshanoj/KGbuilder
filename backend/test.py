from langchain_text_splitters import RecursiveCharacterTextSplitter


try:
    with open('/home/abel/Documents/documents/black holes/basics.txt', 'r', encoding='utf-8') as f:
        text = f.read()
except Exception as e:
    print(f"Error reading TXT file: {e}")
    raise e

splitter = RecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=5)
chunks = splitter.split_text(text)

print(chunks)
# for chunk in chunks:
#     print(f"Chunk: '{chunk}'")   



# from google import genai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# result = client.models.embed_content(
#         model="gemini-embedding-001",
#         contents= [
#             "What is the meaning of life?",
#             "What is the purpose of existence?",
#             "How do I bake a cake?"
#         ]
# )

# for embedding in result.embeddings:
#     print(f"Len: {len(embedding)}")



# import requests
# import os   
# from dotenv import load_dotenv

# load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")
# url = "https://api.groq.com/openai/v1/models"

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# response = requests.get(url, headers=headers)

# print(response.json())