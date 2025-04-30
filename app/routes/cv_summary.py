from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from datetime import datetime
import uuid

from app.sumarizer import summarize_text
from app.extract_text import extract_text_from_pdf, extract_text_from_image
from app.llm_response import answer_best_candidate
from app.db.mongo import save_summary, collection
from app.models.schemas import FullAnalysisResponse, SummariesOnlyResponse

router = APIRouter()

@router.post("/extract_and_summarize")
async def extract_and_summarize(
    files: List[UploadFile] = File(...),
    job_requirements: Optional[str] = Form(None),
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

        base_payload = {
            "request_id": request_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "summaries": summaries
        }

        if job_requirements:
            best_candidate_response = answer_best_candidate(
                f"Qual currículo melhor atende: {job_requirements}?", 
                resume_texts
            )
            result_payload = {**base_payload, "best_candidate_answer": best_candidate_response}
            record_id = save_summary(result_payload)
            return FullAnalysisResponse(**result_payload, record_id=record_id)
        else:
            record_id = save_summary(base_payload)
            return SummariesOnlyResponse(**base_payload, record_id=record_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs():
    try:
        logs = list(collection.find({}, {"_id": 0}))
        if not logs:
            return {"message": "Nenhum registro encontrado"}
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
