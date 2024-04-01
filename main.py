from flask import Flask,request,render_template,redirect
import requests
import json

app = Flask(__name__,template_folder="templates")

word = ["'",'"',"\\"]

host = "http://slinkapi.pythonanywhere.com"

@app.route("/")
def homepage():
    return "<meta name='viewport' content='width=device-width'>Go to <a href='/manage/generate'>Generate page</a> to get a slink for yourself."

@app.route("/manage/generate")
def generate():
    return render_template("index.html")


@app.route("/generate/start",methods=["POST"])
def gen():
    global host
    p = request.form["pass"]
    url = request.form["url"]
    sc = request.form["scode"]
    if any(chr in word for chr in p):
        return """<script>localStorage.setItem("status","spc1");localStorage.setItem("pass","");window.location='/generate/result'</script>Please wait..."""

    p = "" if p == None else p
    sc = "" if sc == None else sc

    data = {"pass":p,
            "url":url,
            "scode":sc}

    s = requests.post(f"{host}/create",data=data)

    s = json.loads(s.text)
    return f'''
<!DOCTYPE html>
<html>
<head>
<title>Please wait...</title>

</head>
<body>
<script>
localStorage.setItem("status","{s["s"]}");
localStorage.setItem("scode","{s["scode"]}");
localStorage.setItem("pass","{s["pass"]}");
window.location="/generate/result";

</script>
<div>
Please wait...<br>
</div>
</body>
</html>
'''

@app.route("/generate/result")
def result():
    return r"""
<meta name="viewport" content="width=device-width">
<span id="scode">Null</span> <span id="passwd"></span>
<script>
var status = localStorage.getItem("status");
s = document.getElementById("scode");
var scode =localStorage.getItem("scode");
var pass = localStorage.getItem("pass");
if (status == "d") {
    s.textContent = "Duplicate scode.Try again!";
} else {if (status == "spc") {s.textContent="Sorry,Scode cannot include spectial character!"} else {
    var s1 = document.createElement("b");
    s1.textContent= scode;
    s.textContent = "Your Scode is: ";
    s1.setAttribute("style","color : red;");
    s.appendChild(s1);
}};

if (status == "spc1") {s.textContent="Password cannot include some special character."};

if (pass=="") {} else {                                                                     var show_pass = document.getElementById("passwd");
    show_pass.textContent = "and your password is: ";
    s2 = document.createElement("b");
    s2.textContent = pass;
    s2.setAttribute("style","color : blue;");
    show_pass.appendChild(s2);
};
</script>
"""


@app.errorhandler(404)
def not_found(e):
    global host
    p = request.path
    p = p[1:]
    pwd = request.args.get("p")
    if pwd == None:
        pwd = ""

    data = {"scode":p,
            "pass":pwd}
    s = requests.post(f"{host}/get",data=data)
    s = json.loads(s.text)

    if s["status"] == 403:
        if (pwd != ""):
            return f'<script>document.location.replace("/{p}");</script>'
        else:
            res = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width">

</head>

<body>

<div id="sol">Calling prompt...</div>

<script>
let sleep = ms => {
return new Promise(resolve => setTimeout(resolve, ms));
};

sleep(1500).then(() => {
const path = window.location.pathname;
let p = window.prompt("Enter password:","");
if (p == null || p == "") {
d = document.getElementById("sol");
d.textContent = "User cancelled or didn't enter anything!";
} else {
d = document.getElementById("sol");
d.textContent = "Checking password...";
window.location=path+"?p="+p}
});
</script>

</body>
</html>
"""
            return res
    elif s["status"] == 202:
        return f'<script>document.location.replace("{s["link"]}");</script>'
    elif s["status"] == 404:
        return "<meta name='viewport' content='width=device-width'>Not found."
