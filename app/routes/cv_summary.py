# app/routes/cv_summary.py

from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from datetime import datetime
import uuid

from app.sumarizer import summarize_text
from app.extract_text import extract_text_from_pdf, extract_text_from_image
from app.llm_response import answer_best_candidate

router = APIRouter()

@router.post("/extract_and_summarize")
async def extract_and_summarize(
    files: List[UploadFile] = File(...),
    job_requirements: str = Form(...),
    user_id: str = Form(...),
):
    summaries = []
    resume_texts = []

    try:
        for file in files:
            if file.content_type == "application/pdf":
                extracted_text = extract_text_from_pdf(file)
            elif file.content_type.startswith("image/"):
                contents = await file.read()
                extracted_text = extract_text_from_image(contents)
            else:
                summaries.append({"filename": file.filename, "error": "Unsupported file type"})
                continue

            if isinstance(extracted_text, dict) and "error" in extracted_text:
                summaries.append({"filename": file.filename, "error": extracted_text["error"]})
                continue

            summary_text = summarize_text(extracted_text)
            summaries.append({"filename": file.filename, "summary": summary_text})
            resume_texts.append(extracted_text)

        if not resume_texts:
            raise HTTPException(status_code=400, detail="Nenhum currículo processado com sucesso.")

        question = f"Qual desses currículos se enquadra melhor para a vaga: {job_requirements}?"
        best_candidate_response = answer_best_candidate(question, resume_texts)

        return {
            "request_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "summaries": summaries,
            "best_candidate_answer": best_candidate_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
