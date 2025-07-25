import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,
    temperature=1,
)

template = """
Você é um agente de inteligência artificial especializado em análise de sentimentos de clientes. Sua tarefa é analisar a avaliação abaixo e gerar três elementos:

1. Sentimento: positivo, neutro ou negativo.
2. Satisfação: percentual entre 0% e 100%, baseado no tom e nas palavras utilizadas pelo cliente.
3. Comentário da IA: uma breve análise em linguagem natural (de 2 a 3 frases), explicando a razão do sentimento identificado.

Regras:
- Sentimentos positivos: satisfação entre 70% e 100%.
- Sentimentos neutros: satisfação entre 40% e 69%.
- Sentimentos negativos: satisfação entre 0% e 39%.
- Seja direto, sem copiar o texto do cliente literalmente.
- Não invente informações.
- Sempre responda no formato:

Sentimento: <classificação>  
Satisfação: <percentual>%  
Comentário da IA: <texto da análise>

🧪 Exemplo:

Avaliação: "Achei o produto bom, chegou antes do prazo e o atendimento foi ótimo. Só achei o preço um pouco salgado."

Saída esperada:
Sentimento: Positivo  
Satisfação: 85%  
Comentário da IA: O cliente demonstrou satisfação com a entrega e o atendimento, o que são pontos fortes da experiência. Apesar de mencionar o preço elevado, o tom geral da avaliação é positivo e indica uma boa aceitação do produto.

🔍 Agora, avalie a seguinte avaliação:

Avaliação: {user_input}"
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["user_input"]
)

while True:
    pergunta = input("Usuário: ")

    if pergunta.lower() == "sair":
        print("Encerrando o chat!")
        break

    prompt_format = prompt.format(user_input=pergunta)

    resposta = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    print(f"Assistente: {resposta.content}\n")

