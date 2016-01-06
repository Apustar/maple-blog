#*************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: __init__.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-11-18 08:03:11
#*************************************************************************
#!/usr/bin/env python
# -*- coding=UTF-8 -*-
from flask import Flask, render_template,send_from_directory,request,\
    Markup,g
from flask_assets import Environment, Bundle
from flask_mail import Mail
from flask_login import LoginManager,current_user
from flask_principal import Principal
from config import load_config
from misaka import Markdown, HtmlRenderer
from redis import StrictRedis

def create_app():
    app = Flask(__name__,static_folder='static')
    config = load_config()
    app.config.from_object(config)
    return app


def register(app):
    register_routes(app)
    register_assets(app)
    register_db(app)
    register_jinja2(app)


def register_routes(app):
    from .views import index,admin, book
    app.register_blueprint(index.site, url_prefix='')
    app.register_blueprint(admin.site, url_prefix='/admin')
    app.register_blueprint(book.site, url_prefix='/book')
    from .views import question
    app.register_blueprint(question.site, url_prefix='/question')
    from .views.blog import site
    app.register_blueprint(site, url_prefix='/blog')


def register_db(app):
    from .models import db

    db.init_app(app)

# def register_cache(app):

    # cache = Cache(config={'CACHE_TYPE': 'simple'})
    # cache.init_app(app)
    # return cache


def register_jinja2(app):
    def safe_markdown(text):
        html = HtmlRenderer()
        markdown = Markdown(html)
        return Markup(markdown(text))
    def visit_total(id):
        visit_total = redis_data.get("visit:%s:totals"%str(id))
        if visit_total:
            visit_total = str(visit_total,'utf-8')
        else:
            visit_total = '0'
        return visit_total
    app.jinja_env.filters['safe_markdown'] = safe_markdown
    app.jinja_env.filters['visit_total'] = visit_total
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

def register_assets(app):
    bundles = {

        'home_js': Bundle(
            'style/js/jquery.min.js',      #这里直接写static目录的子目录 ,如static/bootstrap是错误的
            'style/js/bootstrap.min.js',
            output='style/assets/home.js',
            filters='jsmin'),

        'home_css': Bundle(
            'style/css/bootstrap.min.css',
            output='style/assets/home.css',
            filters='cssmin')
        }

    assets = Environment(app)
    assets.register(bundles)

def register_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "index.login"
    login_manager.session_protection = "strong"
    login_manager.login_message = u"这个页面要求登陆，请登陆"
    return login_manager


app = create_app()
mail = Mail(app)
login_manager = register_login(app)
principals = Principal(app)
redis_data = StrictRedis()
register(app)


@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found(error):
    return render_template('templet/error_404.html'), 404

@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
