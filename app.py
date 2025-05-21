from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/about")
def about():
    name = "Pranta"
    return render_template('about.html',userName = name)

@app.route("/bootstrap")
def bootstrap():
    name = "Pranta"
    return render_template('bootstrap.html',userName = name)

if __name__ == "__main__":
    app.run(debug=True)