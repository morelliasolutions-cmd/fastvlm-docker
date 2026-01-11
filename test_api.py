"""
Script de test pour l'API FastVLM
Usage: python test_api.py
"""
import requests
import base64
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"  # Chemin vers une image de test (optionnel)

def test_health():
    """Test du endpoint /health"""
    print("Test du endpoint /health...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_generate_with_base64():
    """Test avec une petite image base64 encodée (exemple)"""
    print("\nTest du endpoint /generate...")
    
    # Image 1x1 pixel rouge en PNG (base64 encodée)
    # C'est juste un exemple minimal pour tester l'API
    minimal_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "image": f"data:image/png;base64,{minimal_image_base64}",
        "prompt": "What is in this image? Describe it in detail.",
        "max_length": 100
    }
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_generate_with_file(image_path: str):
    """Test avec un fichier image réel"""
    print(f"\nTest avec fichier image: {image_path}...")
    
    if not Path(image_path).exists():
        print(f"Fichier {image_path} non trouvé. Passe ce test.")
        return True
    
    try:
        # Lire et encoder l'image
        with open(image_path, "rb") as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "image": f"data:image/jpeg;base64,{image_base64}",
            "prompt": "What is in this image? Describe it in detail.",
            "max_length": 256
        }
        
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 50)
    print("Test de l'API FastVLM 1.5B")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Le serveur n'est pas accessible. Assurez-vous qu'il est démarré.")
        return
    
    print("\n✅ Health check réussi!")
    
    # Test 2: Génération avec image base64 minimale
    if test_generate_with_base64():
        print("\n✅ Test avec image base64 réussi!")
    else:
        print("\n❌ Test avec image base64 échoué")
    
    # Test 3: Génération avec fichier image (si disponible)
    if Path(TEST_IMAGE_PATH).exists():
        if test_generate_with_file(TEST_IMAGE_PATH):
            print("\n✅ Test avec fichier image réussi!")
        else:
            print("\n❌ Test avec fichier image échoué")
    
    print("\n" + "=" * 50)
    print("Tests terminés")
    print("=" * 50)

if __name__ == "__main__":
    main()
