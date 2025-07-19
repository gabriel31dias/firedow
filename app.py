from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid
import time
import threading
from werkzeug.utils import secure_filename
import logging
import re
import urllib.parse

app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração para armazenamento temporário
TEMP_DIR = tempfile.gettempdir()
DOWNLOAD_DIR = os.path.join(TEMP_DIR, 'youtube_downloads')

# Criar diretório de downloads se não existir
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def cleanup_old_files():
    """Remove arquivos mais antigos que 1 hora"""
    try:
        current_time = time.time()
        max_age = 3600  # 1 hora em segundos
        
        for filename in os.listdir(DOWNLOAD_DIR):
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age:
                    try:
                        os.remove(filepath)
                        logger.info(f"Arquivo removido: {filename}")
                    except Exception as e:
                        logger.error(f"Erro ao remover arquivo {filename}: {str(e)}")
    except Exception as e:
        logger.error(f"Erro na limpeza de arquivos: {str(e)}")

def delete_file_after_delay(filepath, delay=30):
    """Deleta um arquivo após um delay específico"""
    def delete_file():
        time.sleep(delay)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Arquivo removido após delay: {os.path.basename(filepath)}")
        except Exception as e:
            logger.error(f"Erro ao remover arquivo {filepath}: {str(e)}")
    
    thread = threading.Thread(target=delete_file)
    thread.daemon = True
    thread.start()

def clean_youtube_url(url):
    """Limpa a URL do YouTube e extrai apenas o ID do vídeo"""
    try:
        logger.info(f"Limpando URL: {url}")
        
        # Padrões para extrair o ID do vídeo
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{10,11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{10,11})',
            r'v=([a-zA-Z0-9_-]{10,11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"Encontrou ID: {video_id}")
                # Verificar se o ID tem 10-11 caracteres (padrão do YouTube)
                if 10 <= len(video_id) <= 11:
                    cleaned_url = f"https://www.youtube.com/watch?v={video_id}"
                    logger.info(f"URL limpa: {cleaned_url}")
                    return cleaned_url
        
        # Se não encontrou padrão, tentar parsear a URL
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        logger.info(f"Query params: {query_params}")
        
        if 'v' in query_params:
            video_id = query_params['v'][0]
            logger.info(f"ID encontrado via parse: {video_id}")
            if 10 <= len(video_id) <= 11:
                cleaned_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.info(f"URL limpa via parse: {cleaned_url}")
                return cleaned_url
        
        # Se não encontrou padrão, retorna a URL original
        logger.info(f"Retornando URL original: {url}")
        return url
    except Exception as e:
        logger.error(f"Erro ao limpar URL: {str(e)}")
        return url

def get_video_info(url):
    """Obtém informações do vídeo sem fazer download"""
    try:
        # Limpar a URL primeiro
        clean_url = clean_youtube_url(url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # Verificar se info é None
            if info is None:
                logger.error("Não foi possível extrair informações do vídeo")
                return None
                
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'formats': []
            }
    except Exception as e:
        logger.error(f"Erro ao obter informações do vídeo: {str(e)}")
        return None

def download_video(url, format_type='mp4'):
    """Faz o download do vídeo no formato especificado"""
    try:
        # Limpar a URL primeiro
        clean_url = clean_youtube_url(url)
        
        # Configurações baseadas no formato
        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'prefer_ffmpeg': True,
                'nooverwrites': False,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
            }
        elif format_type == 'mp4':
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'prefer_ffmpeg': True,
                'nooverwrites': False,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
            }
        else:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'prefer_ffmpeg': True,
                'nooverwrites': False,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Fazer o download diretamente sem verificar formatos primeiro
            info = ydl.extract_info(clean_url, download=True)
            
            # Verificar se info é None após o download
            if info is None:
                raise Exception("Erro durante o download do vídeo")
            
            filename = ydl.prepare_filename(info)
            
            # Para MP3, o arquivo final terá extensão .mp3
            if format_type == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            # Verificar se o arquivo foi realmente criado
            if not os.path.exists(filename):
                raise Exception("Arquivo não foi criado após o download")
            
            # Verificar se o arquivo tem tamanho > 0
            if os.path.getsize(filename) == 0:
                raise Exception("Arquivo baixado está vazio")
            
            return filename
            
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        raise e

@app.route('/')
def home():
    """Endpoint de teste"""
    return jsonify({
        'message': 'YouTube Download API',
        'status': 'running',
        'endpoints': {
            'GET /info': 'Obter informações do vídeo',
            'POST /download': 'Fazer download do vídeo'
        }
    })

@app.route('/info', methods=['GET'])
def get_info():
    """Obtém informações do vídeo sem fazer download"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    try:
        info = get_video_info(url)
        if info:
            return jsonify(info)
        else:
            return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 400
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/download', methods=['POST'])
def download():
    """Faz o download do vídeo"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
    
    url = data.get('url')
    format_type = data.get('format', 'mp4')  # Padrão é MP4
    
    if not url:
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    if format_type not in ['mp3', 'mp4']:
        return jsonify({'error': 'Formato deve ser mp3 ou mp4'}), 400
    
    try:
        # Limpar arquivos antigos antes do download
        cleanup_old_files()
        
        # Fazer download
        filename = download_video(url, format_type)
        
        # Verificar se o arquivo existe
        if not os.path.exists(filename):
            return jsonify({'error': 'Erro no download do arquivo'}), 500
        
        # Agendar remoção do arquivo após 30 segundos
        delete_file_after_delay(filename, 30)
        
        # Enviar arquivo
        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

@app.route('/download', methods=['GET'])
def download_get():
    """Faz o download do vídeo via GET (mais simples para usar no navegador)"""
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')  # Padrão é MP4
    
    if not url:
        return jsonify({'error': 'URL é obrigatória. Use: /download?url=YOUTUBE_URL&format=mp3'}), 400
    
    if format_type not in ['mp3', 'mp4']:
        return jsonify({'error': 'Formato deve ser mp3 ou mp4'}), 400
    
    try:
        # Limpar arquivos antigos antes do download
        cleanup_old_files()
        
        # Fazer download
        filename = download_video(url, format_type)
        
        # Verificar se o arquivo existe
        if not os.path.exists(filename):
            return jsonify({'error': 'Erro no download do arquivo'}), 500
        
        # Agendar remoção do arquivo após 30 segundos
        delete_file_after_delay(filename, 30)
        
        # Enviar arquivo
        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({'status': 'healthy'})

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Endpoint para limpeza manual dos arquivos temporários"""
    try:
        cleanup_old_files()
        return jsonify({
            'message': 'Limpeza realizada com sucesso',
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Erro na limpeza manual: {str(e)}")
        return jsonify({'error': 'Erro na limpeza'}), 500

@app.route('/status')
def status():
    """Endpoint para verificar status dos arquivos temporários"""
    try:
        files = []
        total_size = 0
        
        for filename in os.listdir(DOWNLOAD_DIR):
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                file_age = time.time() - os.path.getmtime(filepath)
                files.append({
                    'name': filename,
                    'size': file_size,
                    'age_seconds': int(file_age)
                })
                total_size += file_size
        
        return jsonify({
            'files_count': len(files),
            'total_size_bytes': total_size,
            'files': files
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        return jsonify({'error': 'Erro ao obter status'}), 500

@app.route('/test', methods=['GET'])
def test_download():
    """Endpoint de teste para verificar formatos disponíveis"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    try:
        # Limpar a URL primeiro
        clean_url = clean_youtube_url(url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # Verificar se info é None
            if info is None:
                return jsonify({
                    'error': 'Não foi possível extrair informações do vídeo',
                    'original_url': url,
                    'cleaned_url': clean_url
                }), 400
            
            formats = []
            for f in info.get('formats', []):
                formats.append({
                    'format_id': f.get('format_id', 'N/A'),
                    'ext': f.get('ext', 'N/A'),
                    'resolution': f.get('resolution', 'N/A'),
                    'filesize': f.get('filesize', 'N/A'),
                    'acodec': f.get('acodec', 'N/A'),
                    'vcodec': f.get('vcodec', 'N/A'),
                })
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(formats),
                'formats': formats[:10],  # Mostrar apenas os primeiros 10 formatos
                'original_url': url,
                'cleaned_url': clean_url
            })
            
    except Exception as e:
        logger.error(f"Erro no teste: {str(e)}")
        return jsonify({'error': f'Erro no teste: {str(e)}'}), 500

@app.route('/debug', methods=['GET'])
def debug_download():
    """Endpoint de debug para mostrar qual formato está sendo selecionado"""
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')
    
    if not url:
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    try:
        # Limpar a URL primeiro
        clean_url = clean_youtube_url(url)
        
        # Configurações baseadas no formato
        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
        elif format_type == 'mp4':
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
        else:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Simular seleção de formato
            info = ydl.extract_info(clean_url, download=False)
            selected_format = ydl.list_formats(info)
            
            return jsonify({
                'url': clean_url,
                'format_type': format_type,
                'ydl_opts': ydl_opts,
                'selected_format': selected_format,
                'info_keys': list(info.keys()) if info else []
            })
            
    except Exception as e:
        logger.error(f"Erro no debug: {str(e)}")
        return jsonify({'error': f'Erro no debug: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 