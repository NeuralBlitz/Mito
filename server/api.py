"""
Mito API Server
FastAPI server for Mito AI toolkit
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from config.observability import RateLimiter, APIKeyManager
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import tempfile
import os
import base64

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

API_KEY_ENV = os.getenv("MITO_API_KEY")
API_KEY_HEADER = "X-API-Key"
api_keys = APIKeyManager()
limiter = RateLimiter(rate=int(os.getenv("MITO_RATE_LIMIT", "120")), period=60)
if API_KEY_ENV:
    api_keys.create_key("env-key", rate_limit=limiter.rate)
    # replace placeholder key with actual env value
    api_keys.keys[API_KEY_ENV] = api_keys.keys.pop(list(api_keys.keys.keys())[0])

def require_api_key(request: Request):
    if API_KEY_ENV:
        key = request.headers.get(API_KEY_HEADER)
        if not key or not api_keys.validate_key(key):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        return key
    return None

def enforce_rate_limit(request: Request):
    key = request.headers.get(API_KEY_HEADER) or "anonymous"
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return None



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



class TTSRequest(BaseModel):
    text: str
    model: Optional[str] = "tts_models/en/ljspeech/glow-tts"

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
def generate(req: GenerateRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai import TextGenerator
        
        gen = TextGenerator(model_name=req.model)
        result = gen.generate_single(req.prompt, max_length=req.max_tokens)
        
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
def summarize(req: SummarizeRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai.summarize import Summarizer
        
        summ = Summarizer()
        result = summ.summarize(req.text, max_length=req.max_length)
        
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
def translate(req: TranslateRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai.translate import Translator
        
        trans = Translator(model_name=req.model)
        result = trans.translate(req.text)
        
        return {"translation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qa")
def question_answer(req: QARequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai.qa import QAModel
        
        qa = QAModel()
        result = qa.answer(req.question, req.context)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment")
def sentiment(req: SentimentRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
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
def embed(req: EmbedRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai.embeddings import Embedder
        
        embedder = Embedder(model_name=req.model)
        result = embedder.embed(req.text)
        
        return {"embedding": result.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/ocr")
async def ocr(file: UploadFile = File(...), api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    tmp_path = None
    try:
        from python.ai.ocr import OCREngine
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        engine = OCREngine()
        results = engine.read_text(tmp_path)
        return {"text": [r["text"] for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/classify")
async def classify(file: UploadFile = File(...), api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    tmp_path = None
    try:
        from python.ai.image_classify import ImageClassifier
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        classifier = ImageClassifier()
        results = classifier.classify(tmp_path)
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/speech")
async def speech(file: UploadFile = File(...), api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    tmp_path = None
    try:
        from python.ai.speech import SpeechRecognizer
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        recognizer = SpeechRecognizer()
        result = recognizer.get_text(tmp_path)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/tts")
def tts(req: TTSRequest, api_key: str = Depends(require_api_key), _rl: None = Depends(enforce_rate_limit)):
    try:
        from python.ai.tts import TTSEngine
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name
        try:
            engine = TTSEngine(model_name=req.model)
            output_path = engine.speak(req.text, output_path=tmp_path)
            with open(output_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            return {"audio_base64": audio_b64, "format": "wav"}
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    run_server()
