import ollama

def chat(prompt: str):
    response = ollama.chat(
        model='tinyllama',             # Modelo ligero que ya descargaste
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']
