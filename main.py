from flask import Flask, render_template, request, redirect, url_for, flash, session
import fdb
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave_secreta_da_turma_b'

host = "localhost"
# database = r"C:\Users\Aluno\Downloads\BANCO_BORELLA\BANCO.FDB"
database = r"C:\Users\Aluno\Downloads\livros-main (1)\livros-main\livros-sql\BANCO_BORELLA\BANCO.FDB"
user = "sysdba"
password = "sysdba"

con = fdb.connect(host=host, database=database, user=user, password=password)

def validar_senha(senha):
    min_caractere = False
    min_upper = False
    min_lower = False
    min_num = False
    min_caractere_esp = False

    if len(senha) >= 8:
        min_caractere = True

    for caractere in senha:
        if caractere.isalpha() and caractere == caractere.upper():
            min_upper = True
        if caractere.isalpha() and caractere == caractere.lower():
            min_lower = True
        if caractere.isdigit():
            min_num = True
        if not caractere.isalpha() and not caractere.isdigit():
            min_caractere_esp = True

    if min_caractere == True and min_upper == True and min_lower == True and min_num == True and min_caractere_esp == True:
        validacao = True
        return(validacao)
    else:
        validacao = False
        return(validacao)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute(""" SELECT l.id_livro
                            ,l.nome
                            ,l.autor
                            ,l.ano_publicado
                            FROM livro l""")
    livros = cursor.fetchall()
    cursor.close()
    return render_template("livros.html", livros=livros)

@app.route('/home')
def home():
    return redirect(url_for('index'))

@app.route('/novo')
def novo():
    if 'id_usuario' not in session:
        flash('precisa estar logado aqui nao ebagunça')
        return redirect(url_for('login'))
    else:
        return render_template('novo.html')

@app.route('/criar', methods=['POST'])
def criar():
    nome = request.form['nome']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']
    cursor = con.cursor()
    try:
        cursor.execute("""SELECT 1 FROM livro WHERE nome = ?""", (nome,))
        if cursor.fetchone():
            flash("Erro: Livro já existe!", "error")
            return redirect(url_for('novo'))
        cursor.execute(""" INSERT INTO livro (nome, autor, ano_publicado)
                       values (?,?,?) RETURNING ID_LIVRO""", (nome, autor, ano_publicado))
        id_livro = cursor.fetchone()[0]
        con.commit()
        arquivo = request.files['imagem']
        arquivo.save(f'uploads/capa{id_livro}.jpg')

        flash("Livro criado com sucesso!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocorreu um erro: {e}", "error")
        con.rollback()
        return redirect(url_for('novo'))
    finally:
        cursor.close()

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""SELECT id_livro, nome, autor, ano_publicado FROM livro WHERE id_livro = ?""", (id,))
        livro = cursor.fetchone()
        if not livro:
            flash("Livro não encontrado!")
            return redirect(url_for('index'))

        if request.method == 'POST':
            nome = request.form['nome']
            autor = request.form['autor']
            ano_publicado = request.form['ano_publicado']
            cursor.execute("""update livro set nome = ?, autor = ?, ano_publicado = ? where id_livro = ?""", (nome, autor, ano_publicado, id))
            con.commit()
            flash("Livro editado com sucesso!", "success")
            return redirect(url_for('index'))
        else:
            return render_template("editar.html", livro=livro)
    except Exception as e:
        flash(f"Ocorreu um erro: {e}", "error")
        con.rollback()
    finally:
        cursor.close()

@app.route('/confirmar_delete/<int:id>')
def confirmar_delete(id):
    cursor = con.cursor()
    cursor.execute("""SELECT id_livro, nome, autor, ano_publicado
                      FROM livro
                      WHERE id_livro = ?""", (id,))
    livro = cursor.fetchone()
    cursor.close()
    return render_template('confirmar_delete.html', livro=livro)

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""DELETE FROM livro WHERE id_livro = ?""", (id,))
        con.commit()
        flash("Livro deletado com sucesso!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocorreu um erro: {e}", "error")
        con.rollback()
        return redirect(url_for('index'))
    finally:
        cursor.close()

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if validar_senha(senha) == False:
            flash("A senha não atende aos requisitos!", "error")
            return render_template('cadastrar_usuario.html')

        senha = generate_password_hash(senha)
        cursor = con.cursor()

        try:
            cursor.execute("""INSERT INTO usuario (nome, email, senha)
                              VALUES (?,?,?)""", (nome, email, senha))
            con.commit()
            flash("Usuário cadastrado com sucesso!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Ocorreu um erro: {e}", "error")
        finally:
            cursor.close()

    return render_template('cadastrar_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if session.get('bloqueado') == True:
        flash("Login bloqueado após 3 tentativas incorretas!", "error")
        return redirect(url_for('login'))

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    cursor.execute("""SELECT id_usuario, senha FROM usuario
                      WHERE nome = ? AND email = ?""", (nome, email))
    usuario = cursor.fetchone()
    cursor.close()

    if usuario and check_password_hash(usuario[1], senha):
        session['id_usuario'] = usuario[0]
        session['tentativas_login'] = 0
        return redirect(url_for('index'))
    else:
        tentativas = session.get('tentativas_login', 0) + 1
        session['tentativas_login'] = tentativas

        if tentativas >= 3:
            session['bloqueado'] = True
            flash("Você errou a senha 3 vezes. Login bloqueado!", "error")
        else:
            flash(f"Nome, e-mail ou senha incorretos! Tentativa {tentativas} de 3.", "error")

        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
