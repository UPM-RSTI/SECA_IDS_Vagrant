#!/usr/bin/env python3
# Simple Flask login demo for Suricata lab
# - GET / shows a login form
# - POST /login checks credentials (expects admin:admin)
#   * wrong credentials -> returns 401 Unauthorized (HTML body includes '401 Unauthorized')
#   * correct credentials -> 200 OK
#
# Usage: python3 server.py 8080

import sys
from flask import Flask, request, make_response, render_template_string
from waitress import serve

app = Flask(__name__)

LOGIN_FORM = """
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Demo Login</title></head>
<body>
  <h1>Demo Login</h1>
  <form method="POST" action="/login">
    <label>Usuario: <input type="text" name="username" /></label><br/>
    <label>Contraseña: <input type="password" name="password" /></label><br/>
    <button type="submit">Entrar</button>
  </form>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(LOGIN_FORM)

@app.post("/login")
def login():
    user = request.form.get("username", "")
    pwd  = request.form.get("password", "")
    if user == "admin" and pwd == "admin":
        return "<h2>Acceso concedido</h2>", 200
    # Return explicit 401 string in body to help Suricata rule matching
    body = "<h2>401 Unauthorized</h2><p>Credenciales inválidas</p>"
    resp = make_response(body, 401)
    resp.headers["WWW-Authenticate"] = 'Basic realm="Demo"'
    return resp

def main():
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    print(f" * Demo server listening on :{port}")
    serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
