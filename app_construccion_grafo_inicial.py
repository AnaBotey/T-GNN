from flask import Flask, render_template
import folium

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('graph_vis1.html')

if __name__ == '__main__':
    app.run(debug=True)
