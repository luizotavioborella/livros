from flask import Flask, render_template, request
import fdb

app = Flask(__name__)

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
if __name__ == "__main__":
    app.run(debug=True)