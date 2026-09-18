from flask import Flask, render_template, request, redirect, url_for, flash
import fdb
from flask_bcrypt import generate_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave_secreta_da_turma_b'

host = "localhost"
database = r"C:\Users\Aluno\Downloads\BANCO_BORELLA\BANCO.FDB"
user = "sysdba"
password = "sysdba"

con = fdb.connect(host=host, database=database, user=user, password=password)

def validar_senha(senha):
    min_caracteres = False
    min_upper = False
    min_lower = False
    min_num = False
    min_caracteres_esp = False

    if len(senha) >= 8:
        min_caracteres = True
    for caracteres in senha:
        if caracteres.isalpha() and caracteres == caracteres.upper():
            min_upper = True
        if caracteres.isalpha() and caracteres == caracteres.lower():
            min_lower = True
        if caracteres.isdigit():
            min_num = True
        if not caracteres.isalpha() and not caracteres.isdigit():
            min_caracteres_esp = True
    if min_caracteres == True and min_upper == True and min_lower == True and min_num == True:
        validacao == True
        return(validacao)
    else:
        validacao = False
        return(validacao)

@app.route('/')
def index():
    return render_template("login.html")

@app.route("/home")
def home():
    cursor = con.cursor()
    cursor.execute(""" SELECT l.id_livro
                            ,l.nome
                            ,l.autor
                            ,l.ano_publicado
                            FROM livro l
""")
    livros = cursor.fetchall()
    cursor.close()

    return render_template("livros.html", livros=livros)

@app.route('/novo')
def novo():
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
            flash("Erro: Livro já existe!")
            return redirect(url_for('novo'))
        cursor.execute(""" INSERT INTO livro (nome, autor, ano_publicado)
                       values (?,?,?)""", (nome, autor, ano_publicado))
        con.commit()
        flash('Livro criado com sucesso!')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocorreu um erro: {e}" )
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
            flash("Livro editado com sucesso!")
            return redirect(url_for('index'))
        else:
            return render_template("editar.html", livro=livro)
    except Exception as e:
        flash(f"Ocorreu um erro: {e}" )
        con.rollback()
    finally:
        cursor.close()

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""DELETE FROM livro WHERE id_livro = ?""", (id,))
        con.commit()
        flash("Livro deletado com sucesso!")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocorreu um erro: {e}")
        con.rollback()
        return redirect(url_for('index'))
    finally:
        cursor.close()

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = generate_password_hash(request.form['senha'])
    cursor = con.cursor()
    try:
        if validar_senha(senha) == True:
            cursor.execute("""INSERT INTO usuario (nome, email, senha)
                           VALUES (?,?,?)""", (nome, email, senha))
            con.commit()
            flash("Usuário cadastrado com sucesso!", "sucess")
            return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocorreu um erro: {e}" )
    finally:
        cursor.close()

if __name__ == "__main__":
    app.run(debug=True)