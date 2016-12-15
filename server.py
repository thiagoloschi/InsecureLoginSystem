# coding: utf-8

import os
import sqlite3
from flask import Flask
from flask import redirect
from flask import request
from flask import send_from_directory
from flask import session
from jinja2 import Environment
from jinja2 import PackageLoader

_ARQUIVO_BANCO_ = './banco.sqlite'

app = Flask(__name__, static_url_path='/static')
env = Environment(loader=PackageLoader(__name__, 'templates'))

# Checa se o banco de dados já foi criado
if not os.path.isfile(_ARQUIVO_BANCO_):
    con = sqlite3.connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('''
        CREATE TABLE usuario (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            senha TEXT NOT NULL
        );
    ''')
    con.close()

def sqlite_cadastra_usuario(email, senha):
    con = sqlite3.connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('INSERT INTO usuario (email, senha) VALUES ("%s", "%s")' % (email, senha))
    con.commit()
    con.close()


def sqlite_consulta_usuario(email, senha):
    usuario = ''
    con = sqlite3.connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('SELECT * from usuario WHERE usuario.email = "%s" AND usuario.senha = "%s"' % (email, senha))
    for linha in cursor.fetchall():
        usuario = linha
    con.close()
    return usuario


# Arquivos estáticos (CSS, JS, etc.)
@app.route('/static/<path:path>', methods=['GET'])
def static_file(path):
    return app.send_static_file(path)


@app.route('/', methods=['GET'])
def home():
    # Verifica se o usuário está autenticado
    if 'email' in session:
        return env.get_template('index.html').render()

    else:
        return env.get_template('login.html').render()


@app.route('/cadastro', methods=['GET'])
def cadastro():
    if 'email' in session:
        return env.get_template('index.html').render()

    return env.get_template('cadastro.html').render()


@app.route('/login', methods=['GET'])
def login():
    if 'email' in session:
        return env.get_template('index.html').render()

    return env.get_template('login.html').render(e=request.args.get('e'))


@app.route('/sair', methods=['GET'])
def sair():
    if 'email' in session:
        del session['email']

    return env.get_template('login.html').render()


@app.route('/autenticar', methods=['GET'])
def autenticar():
    email = request.args.get('email')
    senha = request.args.get('senha')

    if email and senha:
        usuario = sqlite_consulta_usuario(email, senha)

        if usuario:
            session['email'] = email

        else:
            return redirect('/login?e=' + email)

    return redirect('/')


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    email = request.form['email']
    senha = request.form['senha']
    senha2 = request.form['senha2']

    if senha == senha2:
        # Verifica se o usuário não existe
        if not sqlite_consulta_usuario(email, senha):
            sqlite_cadastra_usuario(email, senha)
            session['email'] = email

            return redirect('/')

    return redirect('/cadastro')


if __name__ == "__main__":
    # Chave para o flask gerenciar a sessão HTTP
    app.secret_key = 'm;4slF=Y6]Afb/.p9Xd7iO8(V0yU~R"'
    app.run(debug=True)