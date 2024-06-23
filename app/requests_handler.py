import os
from openai import OpenAI
import requests

client=OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_algorithms_with_ai(prompt):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role":"user","content":prompt}
        ]) 
    return  completion.choices[0].message.content