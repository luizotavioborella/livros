from flask import Flask, render_template, request, redirect, url_for, flash
import fdb

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave_secreta_da_turma_b'

host = "localhost"
database = r"C:\Users\Aluno\Downloads\BANCO_BORELLA\BANCO.FDB"
user = "sysdba"
password = "sysdba"

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route("/")
def index():
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


if __name__ == "__main__":
    app.run(debug=True)