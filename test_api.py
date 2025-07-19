#!/usr/bin/env python3
"""
Script de teste para a API de YouTube Download
"""

import requests
import json
import time

# URL base da API (mude para sua URL do Render quando estiver deployada)
BASE_URL = "http://localhost:5000"

def test_health():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_info():
    """Testa o endpoint de informações do vídeo"""
    print("\n🔍 Testando endpoint de informações...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        response = requests.get(f"{BASE_URL}/info?url={url}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações obtidas: {data.get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Falha ao obter informações: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
        return False

def test_test_endpoint():
    """Testa o endpoint de teste"""
    print("\n🔍 Testando endpoint de teste...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        response = requests.get(f"{BASE_URL}/test?url={url}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Teste OK - Formatos disponíveis: {data.get('formats_count', 0)}")
            return True
        else:
            print(f"❌ Falha no teste: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_download_mp3():
    """Testa download MP3"""
    print("\n🔍 Testando download MP3...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        response = requests.get(f"{BASE_URL}/download?url={url}&format=mp3", stream=True)
        if response.status_code == 200:
            # Salvar arquivo de teste
            with open("test_download.mp3", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Download MP3 OK")
            return True
        else:
            print(f"❌ Falha no download MP3: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                print(f"Erro: {error_data}")
            return False
    except Exception as e:
        print(f"❌ Erro no download MP3: {e}")
        return False

def test_download_mp4():
    """Testa download MP4"""
    print("\n🔍 Testando download MP4...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        response = requests.get(f"{BASE_URL}/download?url={url}&format=mp4", stream=True)
        if response.status_code == 200:
            # Salvar arquivo de teste
            with open("test_download.mp4", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Download MP4 OK")
            return True
        else:
            print(f"❌ Falha no download MP4: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                print(f"Erro: {error_data}")
            return False
    except Exception as e:
        print(f"❌ Erro no download MP4: {e}")
        return False

def test_status():
    """Testa o endpoint de status"""
    print("\n🔍 Testando endpoint de status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status OK - Arquivos: {data.get('files_count', 0)}")
            return True
        else:
            print(f"❌ Falha no status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no status: {e}")
        return False

def test_cleanup():
    """Testa o endpoint de limpeza"""
    print("\n🔍 Testando endpoint de limpeza...")
    try:
        response = requests.post(f"{BASE_URL}/cleanup")
        if response.status_code == 200:
            print("✅ Limpeza OK")
            return True
        else:
            print(f"❌ Falha na limpeza: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API de YouTube Download")
    print("=" * 50)
    
    tests = [
        test_health,
        test_info,
        test_test_endpoint,
        test_download_mp3,
        test_download_mp4,
        test_status,
        test_cleanup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Pausa entre testes
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A API está funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    print("\n💡 Para usar no Render, mude BASE_URL para sua URL do Render:")
    print("   BASE_URL = 'https://sua-api.onrender.com'")

if __name__ == "__main__":
    main() 