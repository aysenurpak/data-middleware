from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time

from handlers.anonymizer import AnonymizerHandler
from handlers.enricher import EnricherHandler
from handlers.formatter import FormatterHandler

app = FastAPI(title="Stock Exchange Middleware", version="1.0.0")

# ------- Veri Modeli -------
class LogEntry(BaseModel):
    level: str                  # ERROR, CRITICAL, WARNING, INFO
    role: str                   # system_admin, cybersec, web_dev
    message: str
    sender_id: Optional[str] = None
    transaction_no: Optional[str] = None
    credit_card: Optional[str] = None
    email: Optional[str] = None
    tc_kimlik: Optional[str] = None

# ------- Chain of Responsibility Kurulumu -------
def build_chain():
    anonymizer = AnonymizerHandler()
    enricher = EnricherHandler()
    formatter = FormatterHandler()

    #  anonymizer → enricher → formatter
    anonymizer.set_next(enricher).set_next(formatter)

    return anonymizer

# ------- Endpointler -------
@app.get("/")
def root():
    return {"status": "Middleware is running and ready to receive logs."}

@app.post("/log")
def receive_log(entry: LogEntry):
    start = time.time()

    chain = build_chain()
    result = chain.handle(entry.model_dump())

    elapsed = round((time.time() - start) * 1000, 3)
    result["processing_time_ms"] = elapsed

    return result

@app.post("/logs/batch")
def receive_batch(entries: list[LogEntry]):
    start = time.time()
    results = []

    chain = build_chain()
    for entry in entries:
        result = chain.handle(entry.model_dump())
        results.append(result)

    elapsed = round((time.time() - start) * 1000, 3)

    return {
        "total": len(results),
        "processing_time_ms": elapsed,
        "results": results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)