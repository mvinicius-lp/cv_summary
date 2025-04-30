from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from datetime import datetime
import uuid
from bson import ObjectId

from app.models.schemas import ExtractAndSummarizeResponse 
from app.sumarizer import summarize_text
from app.extract_text import extract_text_from_pdf, extract_text_from_image
from app.llm_response import answer_best_candidate
from app.db.mongo import save_summary_record

router = APIRouter()

@router.post("/extract_and_summarize", response_model=ExtractAndSummarizeResponse)
async def extract_and_summarize(
    files: List[UploadFile] = File(...),
    job_requirements: str = Form(...),
    user_id: str = Form(...),
):
    summaries = []
    resume_texts = []

    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()

    try:
        for file in files:
            file_info = {"filename": file.filename}
            
            try:
                if file.content_type == "application/pdf":
                    extracted_text = extract_text_from_pdf(file)
                elif file.content_type.startswith("image/"):
                    contents = await file.read()
                    extracted_text = extract_text_from_image(contents)
                else:
                    file_info["error"] = "Unsupported file type"
                    summaries.append(file_info)
                    continue

                if isinstance(extracted_text, dict) and "error" in extracted_text:
                    file_info["error"] = extracted_text["error"]
                    summaries.append(file_info)
                    continue

                summary_text = summarize_text(extracted_text)
                file_info["summary"] = summary_text
                summaries.append(file_info)
                resume_texts.append(extracted_text)

            except Exception as e:
                file_info["error"] = str(e)
                summaries.append(file_info)

        if not resume_texts:
            raise HTTPException(status_code=400, detail="Nenhum currículo processado com sucesso.")

        question = f"Qual desses currículos se enquadra melhor para a vaga com os seguintes requisitos: {job_requirements}?"
        best_candidate_response = answer_best_candidate(question, resume_texts)

        result_payload = {
            "request_id": request_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "summaries": summaries,
            "best_candidate_answer": best_candidate_response
        }
        record_id = save_summary_record(result_payload)

        response_data = {
            **result_payload,
            "record_id": record_id
        }

        return ExtractAndSummarizeResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))