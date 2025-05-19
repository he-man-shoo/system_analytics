# Importing necessary libraries
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, redirect, url_for
from flask_dance.contrib.azure import azure, make_azure_blueprint
import os
from PIL import Image
import dash
import dash_bootstrap_components as dbc
from flask import send_file
from dash import Dash, html, Output, Input, dcc
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, redirect, url_for, session
from flask_session import Session
from flask_dance.contrib.azure import azure, make_azure_blueprint

# Only if running on Local Environment
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# On Production
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Initialize a global variable to store the user name
user_name = None

blueprint = make_azure_blueprint(
    client_id="5a5ba74f-0259-4318-88fb-2fd94bf0b862",
    # client_secret="LdU8Q~W_e9JQDte4hZXdWTNCHLuL0PhGfSzKCbzk",
    tenant="fda0a4a7-3813-444d-808d-54bb327d0367",
    scope=["openid", "email", "profile", "User.Read"],
)

server = Flask(__name__)
server.config["SECRET_KEY"] = "secretkey"
server.config["SESSION_TYPE"] = "filesystem"  # Set the session type to filesystem

server.register_blueprint(blueprint, url_prefix="/login")

Session(server)

def login_required(func):
    """Require a login for the given view function."""

    def check_authorization(*args, **kwargs):
        global user_name
        if not azure.authorized or azure.token.get("expires_in") < 0:
            return redirect(url_for("azure.login"))
        else:
            if user_name is None:
                resp = azure.get("/v1.0/me")
                assert resp.ok, resp.text
                user_info = resp.json()
                session['user_name'] = user_info['displayName']
                dash_app.layout.children[-1].data = session.get('user_name', 'Guest')  # Update the last instance of dcc.Store data
            return func(*args, **kwargs)

    return check_authorization


# Colors
prevalon_purple = 'rgb(72,49,120)'
prevalon_lavender = 'rgb(166,153,193)'
prevalon_yellow = 'rgb(252,215,87)'
prevalon_cream = 'rgb(245,225,164)'
prevalon_slate = 'rgb(208,211,212)'
prevalon_gray = 'rgb(99,102,106)'



dash_app = Dash(__name__, server=server, use_pages=True,
                external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/litera/bootstrap.min.css",
                                      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# use this in your production environment since you will otherwise run into problems
# https://flask-dance.readthedocs.io/en/v0.9.0/proxies.html#proxies-and-https
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

for view_func in server.view_functions:
    if not view_func.startswith("azure"):
        server.view_functions[view_func] = login_required(server.view_functions[view_func])

logo = Image.open("Prevalon Logo.png")

page_layout = []
for page in dash.page_registry.values():
    page_layout.append(dbc.NavItem(dbc.NavLink(page["name"], href=page["path"], active="exact"),))


dash_app.layout = dbc.Container([

    dbc.Row([
                dbc.Col(
                    html.A(
                        children=html.Img(src = logo, width=180),
                        href= 'https://prevalonenergy.com/', 
                        target="_blank",
                    ),
                    width = {'size':1}, ),

                dbc.Col(html.H2(id='user_name_display', 
                                className="btn", style={'backgroundColor': prevalon_purple, 'color':'white'}),
                        width = {'size':6}, style = {'text-align': 'center', "margin-top": "25px"}),

                    dbc.NavbarSimple(
                                    children = page_layout,
                                    color=prevalon_purple,
                                    dark=True,
                                ),
                    ],justify='between'),
    
    html.A(
        dbc.Container([
                        dash.page_container, 
                        ], fluid=True, ), ), 

    dcc.Store(id="stored_bol_qtys"),
    dcc.Store(id="stored_edit_project_details"),
    dcc.Store(id="stored_user_name", data=user_name), # user_name should be always the last dcc.Store


 ], fluid=True,) 

@dash_app.server.route('/download/<path:path>')
def serve_static(path):
    return send_file(path, as_attachment=True)

@dash_app.callback(
    Output('user_name_display', 'children'),
    Input('stored_user_name', 'data')
)
def update_user_name_display(user_name):
    if user_name:
        return f"Welcome, {user_name}!"
    return "Welcome, Guest!"

if __name__ == '__main__':
    dash_app.run(debug=True)