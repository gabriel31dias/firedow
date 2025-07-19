# YouTube Download API

API Flask para download de vídeos do YouTube em formatos MP3 e MP4.

## Funcionalidades

- Download de vídeos do YouTube em MP3 e MP4
- Limpeza automática de arquivos temporários
- Suporte a CORS para uso em frontend
- Endpoints de health check e status
- Configurações otimizadas para produção

## Endpoints

### GET /health
Verifica se a API está funcionando.

### GET /info?url=YOUTUBE_URL
Obtém informações do vídeo sem fazer download.

### GET /download?url=YOUTUBE_URL&format=mp3|mp4
Faz download do vídeo no formato especificado.

### GET /test?url=YOUTUBE_URL
Lista formatos disponíveis para o vídeo.

### GET /status
Mostra status dos arquivos temporários.

### POST /cleanup
Limpa arquivos temporários antigos.

## Deploy no Render

### Opção 1: Deploy via GitHub (Recomendado)

1. Faça push do código para um repositório GitHub
2. Acesse [render.com](https://render.com)
3. Clique em "New +" e selecione "Web Service"
4. Conecte seu repositório GitHub
5. Configure:
   - **Name**: youtube-download-api
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Clique em "Create Web Service"

### Opção 2: Deploy via render.yaml

1. Faça push do código para um repositório GitHub
2. Acesse [render.com](https://render.com)
3. Clique em "New +" e selecione "Blueprint"
4. Conecte seu repositório GitHub
5. O Render detectará automaticamente o arquivo `render.yaml`
6. Clique em "Apply"

## Uso Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
python app.py
```

A API estará disponível em `http://localhost:5000`

## Exemplos de Uso

```bash
# Download MP3
curl "https://sua-api.onrender.com/download?url=https://www.youtube.com/watch?v=Dc4z7WvUPyE&format=mp3" -o video.mp3

# Download MP4
curl "https://sua-api.onrender.com/download?url=https://www.youtube.com/watch?v=Dc4z7WvUPyE&format=mp4" -o video.mp4

# Ver informações do vídeo
curl "https://sua-api.onrender.com/test?url=https://www.youtube.com/watch?v=Dc4z7WvUPyE"
```

## Limpeza Automática

A API automaticamente:
- Remove arquivos após 30 segundos do download
- Limpa arquivos antigos (mais de 1 hora) periodicamente
- Gerencia espaço em disco automaticamente

## Solução de Problemas

### Erro de SSL em Produção

Se você encontrar erros de SSL como:
```
certificate verify failed: unable to get local issuer certificate
```

A API já está configurada para resolver isso com:
- `nocheckcertificate: True`
- `ignoreerrors: True`
- Certificados SSL instalados no Dockerfile
- Configurações de retry e timeout

### Teste de Produção

Após o deploy, teste sua API:

```bash
# Edite o arquivo test_production.py com sua URL
python test_production.py
```

## Notas

- O plano gratuito do Render tem limitações de recursos
- Downloads podem ser mais lentos no ambiente de produção
- Recomenda-se usar para vídeos de tamanho moderado
- A primeira requisição pode demorar alguns segundos (cold start) 