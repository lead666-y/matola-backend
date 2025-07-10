from flask import Flask, request, render_template, render_template_string, send_from_directory
import os
import json

app = Flask(__name__)

# Pastas
UPLOAD_FOLDER = 'uploads'
PERFIS_DB = 'db/perfis.json'
ALLOWED_EXTENSIONS = {'mp4', 'png', 'jpg', 'jpeg'}

# Cria pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('db', exist_ok=True)

# Cria JSON se não existir
if not os.path.exists(PERFIS_DB):
    with open(PERFIS_DB, 'w') as f:
        json.dump([], f)

# Verifica extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota principal (teste simples)
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('media')
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            return f'<h3>✅ Arquivo salvo com sucesso: uploads/{file.filename}</h3><a href="/">← Voltar</a>'
        else:
            return '<h3>❌ Arquivo inválido</h3><a href="/">← Voltar</a>'

    return render_template_string("""
        <h2>Upload de vídeo ou imagem</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="media" accept="video/mp4,image/png,image/jpeg"><br><br>
            <input type="submit" value="Enviar">
        </form>
    """)

# ========== API PERFIL ==========

@app.route('/salvar_perfil', methods=['POST'])
def salvar_perfil():
    data = request.json
    nome = data.get('nome')
    id_ = data.get('id')
    foto = data.get('foto')

    try:
        with open(PERFIS_DB, 'r') as f:
            perfis = json.load(f)
    except:
        perfis = []

    # Verifica duplicado
    for perfil in perfis:
        if perfil['id'] == id_:
            return {"status": "duplicado"}

    perfis.append({"nome": nome, "id": id_, "foto": foto})

    with open(PERFIS_DB, 'w') as f:
        json.dump(perfis, f)

    return {"status": "ok"}

@app.route('/login_perfil')
def login_perfil():
    nome = request.args.get('nome')
    id_ = request.args.get('id')

    try:
        with open(PERFIS_DB, 'r') as f:
            perfis = json.load(f)
    except:
        return {"status": "erro"}

    for perfil in perfis:
        if perfil['nome'] == nome and perfil['id'] == id_:
            return {
                "status": "ok",
                "nome": perfil['nome'],
                "id": perfil['id'],
                "foto": perfil['foto']
            }

    return {"status": "erro"}

# Arquivos de upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# HTMLs
@app.route('/upload.html')
def upload_html():
    return render_template('upload.html')

@app.route('/perfil.html')
def perfil_html():
    return render_template('perfil.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')

# ==========
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
