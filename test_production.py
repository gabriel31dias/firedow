#!/usr/bin/env python3
"""
Script de teste para produção - Testa a API no Render
"""

import requests
import json
import time
import sys

# URL da sua API no Render (substitua pela sua URL real)
PRODUCTION_URL = "https://youtube-download-api.onrender.com"

def test_production_health():
    """Testa o health check em produção"""
    print("🔍 Testando health check em produção...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_production_download():
    """Testa download em produção"""
    print("\n🔍 Testando download em produção...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Teste MP3
    print("  Testando MP3...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/download?url={url}&format=mp3", 
                              stream=True, timeout=60)
        if response.status_code == 200:
            print("  ✅ Download MP3 OK")
            return True
        else:
            print(f"  ❌ Falha no download MP3: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                print(f"  Erro: {error_data}")
            return False
    except Exception as e:
        print(f"  ❌ Erro no download MP3: {e}")
        return False

def test_production_info():
    """Testa informações do vídeo em produção"""
    print("\n🔍 Testando informações em produção...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        response = requests.get(f"{PRODUCTION_URL}/test?url={url}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações OK - Formatos: {data.get('formats_count', 0)}")
            return True
        else:
            print(f"❌ Falha nas informações: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro nas informações: {e}")
        return False

def main():
    """Executa testes de produção"""
    print("🚀 Testando API em Produção")
    print("=" * 50)
    print(f"URL: {PRODUCTION_URL}")
    print("=" * 50)
    
    # Aguardar um pouco para a aplicação "acordar"
    print("⏳ Aguardando aplicação inicializar...")
    time.sleep(10)
    
    tests = [
        test_production_health,
        test_production_info,
        test_production_download,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(2)  # Pausa entre testes
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A API está funcionando em produção.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 