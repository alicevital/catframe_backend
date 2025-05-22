from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# Nome do banco de dados
DB_NAME = 'filmes.db'

# Função para criar o banco de dados
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            diretor TEXT NOT NULL,
            ano INTEGER NOT NULL,
            sinopse TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Página inicial (front-end)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Rota para listar todos os filmes
@app.route('/api/filmes/get_filmes', methods=['GET'])
def get_filmes():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM filmes")
    filmes = c.fetchall()
    conn.close()
    return jsonify(filmes)

# Rota para adicionar um novo filme
@app.route('/api/filmes/set_filmes', methods=['POST'])
def add_filme():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO filmes (titulo, genero, diretor, ano, sinopse) VALUES (?, ?, ?, ?, ?)",
        (data['titulo'], data['genero'], data['diretor'], data['ano'], data['sinopse'])
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "sucesso"}), 201

# Rota para obter um filme por ID (opcional)
@app.route('/api/filmes/get_filme/<int:id>', methods=['GET'])
def get_filme(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    filme = c.fetchone()
    conn.close()
    return jsonify(filme)

# Inicialização
if __name__ == '_main_':
    init_db()
    app.run(debug=True)