from flask import Flask, request, render_template, send_from_directory, render_template_string, jsonify
import os, json

app = Flask(__name__)

# Diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho real dos arquivos
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PERFIS_JSON_PATH = os.path.join(BASE_DIR, 'db', 'perfis.json')
ALLOWED_EXTENSIONS = {'mp4', 'png', 'jpg', 'jpeg'}

# Garantir pastas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'db'), exist_ok=True)
if not os.path.exists(PERFIS_JSON_PATH):
    with open(PERFIS_JSON_PATH, 'w') as f:
        json.dump([], f)

# Função de validação
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware CORS
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('media')
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            return f'<h3>✅ Arquivo salvo: uploads/{file.filename}</h3><a href="/">← Voltar</a>'
        else:
            return '<h3>❌ Arquivo inválido</h3><a href="/">← Voltar</a>'

    return render_template_string("""
        <h2>Upload de vídeo ou imagem</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="media" accept="video/mp4,image/png,image/jpeg"><br><br>
            <input type="submit" value="Enviar">
        </form>
    """)

@app.route('/salvar_perfil', methods=['POST'])
def salvar_perfil():
    data = request.json
    nome = data.get('nome')
    id_ = data.get('id')
    foto = data.get('foto')

    if not nome or not id_ or not foto:
        return jsonify({"status": "erro", "message": "Dados incompletos"}), 400

    try:
        with open(PERFIS_JSON_PATH, 'r') as f:
            perfis = json.load(f)
    except:
        perfis = []

    for perfil in perfis:
        if perfil['id'] == id_:
            return jsonify({"status": "duplicado", "message": "ID já existe"})

    perfis.append({"nome": nome, "id": id_, "foto": foto})

    try:
        with open(PERFIS_JSON_PATH, 'w') as f:
            json.dump(perfis, f)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500

@app.route('/login_perfil', methods=['GET', 'POST'])
def login_perfil():
    if request.method == 'POST':
        data = request.json
        nome = data.get('nome')
        id_ = data.get('id')
    else:
        nome = request.args.get('nome')
        id_ = request.args.get('id')
    
    if not nome or not id_:
        return jsonify({"status": "erro", "message": "Dados incompletos"}), 400

    try:
        with open(PERFIS_JSON_PATH, 'r') as f:
            perfis = json.load(f)
    except:
        perfis = []

    for perfil in perfis:
        if perfil['nome'] == nome and perfil['id'] == id_:
            return jsonify({
                "status": "ok",
                "nome": perfil['nome'],
                "id": perfil['id'],
                "foto": perfil['foto']
            })

    return jsonify({"status": "erro", "message": "Perfil não encontrado"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload.html')
def upload_html():
    return render_template('upload.html')

@app.route('/perfil.html')
def perfil_html():
    return render_template('perfil.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')


@app.route('/publicar.html')
def publicar():
    return render_template('publicar.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
