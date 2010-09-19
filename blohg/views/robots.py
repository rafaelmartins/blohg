from flask import Module, make_response, render_template

robots = Module(__name__)

@robots.route('/robots.txt')
def robots_txt():
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response
