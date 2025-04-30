# app/llm_response.py
import ollama

def answer_best_candidate(question: str, resume_texts: list) -> str:
    try:
        resumes_combined = "\n\n".join(resume_texts)
        input_prompt = (
            "qual currículo é o mais adequado? Justifique sua escolha com base nos conteúdos dos currículos e na descrição da vaga.\n\n"
            "Não cite os currículos que não foram escolhidos na construção da resposta"
            "Sempre cite o nome do melhor candidato para a vaga"
            f"Currículos:\n{resumes_combined}\n\n"
            f"Descrição da vaga: {question}"
        )

        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "Você é um recrutador experiente. Analise os currículos e selecione o mais adequado para a vaga."},
            {"role": "user", "content": input_prompt}
        ])

        return response["message"]["content"]

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
