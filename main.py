from flask import Flask, render_template

from shmu_scrapper import get_aladin_url_img

app = Flask(__name__)

@app.route("/")
@app.route("/aladin")
def shmu_aladin():
    return render_template("shmu_aladin.html", aladin_img_src=get_aladin_url_img())

@app.route("/radar")
def shmu_radar():
    return render_template("shmu_radar.html")


