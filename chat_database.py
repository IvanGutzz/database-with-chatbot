import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from schema import schema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DATABASE_URL = f"mysql+pymysql://root:root@localhost:3306/library_api"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def executar_sql(query):
    try:
        with engine.connect() as connection:
            print("Conectado!")
            result = connection.execute(text(query))
            rows = result.fetchall()
            return result
    except SQLAlchemyError as error:
        print("Erro ao executar o comando SQL: ", error)
        return {"erro": error}

api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,
    temperature=1,
)

template = """
🔹 OBJETIVO DO AGENTE:
Você é um agente especialista em construção de queries SQL (MySQL) para um sistema de gestão de empréstimos de uma biblioteca. Seu papel é ler a estrutura (schema) do banco de dados e, com base em uma pergunta feita por um usuário, gerar apenas a consulta SQL correta e completa que atenda precisamente à solicitação.

Você deve considerar:
- As tabelas, campos e relacionamentos descritos no schema.
- A pergunta do usuário, que pode vir em linguagem natural.
- O contexto de uma biblioteca: livros, empréstimos, devoluções, usuários, datas, etc.

Seu único output será o texto da consulta SQL correspondente. Nada mais.

---

🔐 BOAS PRÁTICAS (GUARDRAILS):
- Nunca adicione explicações ou comentários no output. Apenas a SQL.
- Evite SELECT *: sempre especifique os campos necessários.
- Sempre utilize aliases (ex: `u.nome AS nome_usuario`) para melhorar legibilidade, quando necessário.
- Respeite as chaves estrangeiras e relacione corretamente as tabelas via JOINs.
- Trate filtros com clareza (ex: `WHERE`, `LIKE`, `BETWEEN`, etc.).
- Use funções agregadoras (`COUNT`, `AVG`, etc.) apenas quando fizerem sentido na pergunta.
- Sempre termine a query com `;`.

---

🎯 EXEMPLO DE OUTPUT (SOMENTE A STRING SEM MARKDOWN):
SELECT l.titulo, u.nome, e.data_emprestimo
FROM emprestimos e
JOIN livros l ON e.livro_id = l.id
JOIN usuarios u ON e.usuario_id = u.id
WHERE e.data_devolucao IS NULL;

Agora, com base no schema abaixo e na pergunta do usuário, gere apenas a consulta SQL correspondente:

schema:
{schema}

pergunta:
{pergunta}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["pergunta", "schema"]
)

pergunta = input("Digite a pergunta: ")

prompt_format = prompt.format(pergunta=pergunta, schema=schema)

resposta = llm_gemini.invoke([HumanMessage(content=prompt_format)])

print(f"Assistente: {resposta.content}\n")

resultado_sql = executar_sql(resposta.content)

print(resultado_sql)