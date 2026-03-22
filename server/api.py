"""
Mito API Server
FastAPI server for Mito AI toolkit
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import tempfile
import os

VERSION = "1.0.0"

app = FastAPI(
    title="Mito API",
    description="The Powerhouse AI Toolkit API",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt2"
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7


class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = 130


class TranslateRequest(BaseModel):
    text: str
    model: Optional[str] = "Helsinki-NLP/opus-mt-en-es"


class QARequest(BaseModel):
    question: str
    context: str


class SentimentRequest(BaseModel):
    text: str


class EmbedRequest(BaseModel):
    text: str
    model: Optional[str] = "sentence-transformers/all-MiniLM-L6-v2"


@app.get("/")
def root():
    return {
        "name": "Mito API",
        "version": VERSION,
        "status": "running"
    }


@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {"name": "llama", "description": "Llama LLM inference"},
            {"name": "textgen", "description": "Text generation"},
            {"name": "summarize", "description": "Text summarization"},
            {"name": "translate", "description": "Translation"},
            {"name": "qa", "description": "Question answering"},
            {"name": "sentiment", "description": "Sentiment analysis"},
            {"name": "embed", "description": "Text embeddings"},
            {"name": "ocr", "description": "OCR text recognition"},
            {"name": "classify", "description": "Image classification"},
            {"name": "speech", "description": "Speech recognition"},
            {"name": "tts", "description": "Text-to-speech"},
        ]
    }


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        from python.ai import TextGenerator
        
        gen = TextGenerator(model_name=req.model)
        result = gen.generate_single(req.prompt, max_length=req.max_tokens)
        
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
def summarize(req: SummarizeRequest):
    try:
        from python.ai.summarize import Summarizer
        
        summ = Summarizer()
        result = summ.summarize(req.text, max_length=req.max_length)
        
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
def translate(req: TranslateRequest):
    try:
        from python.ai.translate import Translator
        
        trans = Translator(model_name=req.model)
        result = trans.translate(req.text)
        
        return {"translation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qa")
def question_answer(req: QARequest):
    try:
        from python.ai.qa import QAModel
        
        qa = QAModel()
        result = qa.answer(req.question, req.context)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment")
def sentiment(req: SentimentRequest):
    try:
        from python.ai.sentiment import quick_sentiment, quick_emotion
        
        sent = quick_sentiment(req.text)
        emotion = quick_emotion(req.text)
        
        return {
            "sentiment": sent["label"],
            "score": sent["score"],
            "emotion": emotion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed")
def embed(req: EmbedRequest):
    try:
        from python.ai.embeddings import Embedder
        
        embedder = Embedder(model_name=req.model)
        result = embedder.embed(req.text)
        
        return {"embedding": result.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    try:
        from python.ai.ocr import OCREngine
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        engine = OCREngine()
        results = engine.read_text(tmp_path)
        
        os.unlink(tmp_path)
        
        return {"text": [r["text"] for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    try:
        from python.ai.image_classify import ImageClassifier
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        classifier = ImageClassifier()
        results = classifier.classify(tmp_path)
        
        os.unlink(tmp_path)
        
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speech")
async def speech(file: UploadFile = File(...)):
    try:
        from python.ai.speech import SpeechRecognizer
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        recognizer = SpeechRecognizer()
        result = recognizer.get_text(tmp_path)
        
        os.unlink(tmp_path)
        
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
