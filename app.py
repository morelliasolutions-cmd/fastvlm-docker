"""
FastVLM 1.5B API Server
Serveur API pour FastVLM qui accepte des images en base64 via HTTP
"""
import os
import base64
import io
from typing import Optional
from PIL import Image
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="FastVLM 1.5B API", version="1.0.0")

# Configuration CORS pour permettre les requêtes depuis n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales pour le modèle
model = None
processor = None
device = None


class ImageRequest(BaseModel):
    """Requête contenant une image en base64 et une question optionnelle"""
    image: str  # Image encodée en base64 (avec ou sans data:image prefix)
    prompt: Optional[str] = "What is in this image? Describe it in detail."  # Question/prompt pour le VLM
    max_length: Optional[int] = 512  # Longueur maximale de la réponse


class VLMResponse(BaseModel):
    """Réponse du modèle VLM"""
    response: str
    model: str = "FastVLM-1.5B"


def load_model():
    """Charge le modèle FastVLM 1.5B"""
    global model, processor, device
    
    try:
        from transformers import AutoModelForCausalLM, AutoProcessor
        
        model_name = os.getenv("MODEL_NAME", "apple/FastVLM-1.5B")
        
        print(f"Chargement du modèle {model_name}...")
        
        # Forcer l'utilisation de CPU (configuration pour VPS sans GPU)
        device = os.getenv("TORCH_DEVICE", "cpu")
        if device == "cpu" or not torch.cuda.is_available():
            device = "cpu"
            print(f"Mode CPU uniquement activé")
        else:
            device = "cuda"
        print(f"Utilisation du device: {device}")
        
        # Charger le processeur
        processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        
        # Charger le modèle (CPU uniquement - float32 pour compatibilité)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float32,  # CPU nécessite float32
            device_map=None,  # Pas de device_map pour CPU
            low_cpu_mem_usage=True,  # Optimisation mémoire pour CPU
        )
        
        # Déplacer explicitement vers CPU
        model = model.to("cpu")
        model.eval()
        print(f"Modèle {model_name} chargé avec succès sur CPU!")
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Assurez-vous que transformers est installé avec: pip install transformers")
        raise
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        raise


def decode_base64_image(image_base64: str) -> Image.Image:
    """Décode une image depuis base64"""
    try:
        # Nettoyer le prefix data:image si présent
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # Décoder base64
        image_data = base64.b64decode(image_base64)
        
        # Ouvrir avec PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir en RGB si nécessaire
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        return image
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du décodage de l'image: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Charge le modèle au démarrage"""
    print("Démarrage du serveur FastVLM API...")
    load_model()


@app.get("/")
async def root():
    """Endpoint de santé"""
    return {
        "status": "online",
        "model": "FastVLM-1.5B",
        "device": device if device else "loading...",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Vérification de santé du serveur"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": device if device else "unknown"
    }


@app.post("/generate", response_model=VLMResponse)
async def generate(request: ImageRequest):
    """
    Génère une réponse à partir d'une image et d'un prompt
    
    Args:
        request: Requête contenant l'image (base64) et le prompt
        
    Returns:
        Réponse du modèle VLM
    """
    if model is None or processor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé. Veuillez réessayer dans quelques instants.")
    
    try:
        # Décoder l'image
        image = decode_base64_image(request.image)
        
        # Préparer les inputs
        inputs = processor(
            images=image,
            text=request.prompt,
            return_tensors="pt"
        ).to(device)
        
        # Générer la réponse (optimisé pour CPU)
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_length=request.max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                num_beams=1,  # Beam search désactivé pour CPU (plus rapide)
                pad_token_id=processor.tokenizer.pad_token_id if processor.tokenizer.pad_token_id else processor.tokenizer.eos_token_id,
            )
        
        # Décoder la réponse
        generated_text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        # Extraire seulement la partie générée (après le prompt)
        if request.prompt in generated_text:
            response_text = generated_text.split(request.prompt)[-1].strip()
        else:
            response_text = generated_text.strip()
        
        return VLMResponse(response=response_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@app.post("/chat", response_model=VLMResponse)
async def chat(request: ImageRequest):
    """
    Alias pour /generate avec format de conversation
    """
    return await generate(request)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
