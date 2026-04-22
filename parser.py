import json
from ollama import Client

def parsear_boleto(texto):
    #####url = "https://api.ollama.com/api/chat"
    OLLAMA_API_KEY = "SECRET_KEY"

    prompt = f"""
        Você é um parser de boletos.

        RETORNE APENAS JSON VÁLIDO.
        NÃO escreva explicações.
        NÃO use markdown.
        NÃO use texto antes ou depois.

        Schema:
    {{
      "linha_digitavel":string  
      "valor":string
      "data_do_documento":string
      "data_de_vencimento":string
      "beneficiario":string     
    }}
    Se não souber algum campo, use "N/A".
    
    Texto:
    {texto}
    """
    client = Client(
        host='https://ollama.com',
        headers={'Authorization': 'Bearer ' + OLLAMA_API_KEY}
        )


    messages = [
    {
        'role': 'user',
        'content': prompt,
    },
    ]     
    response = client.chat(
        model = 'gpt-oss:120b',
        messages=messages,
        format='json')

    content = response["message"]["content"]
    return json.loads(content)