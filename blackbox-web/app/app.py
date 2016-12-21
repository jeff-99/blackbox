from flask import Flask, g
from .views import index, stream, streamview


def create_app(config, sharedData=None):
    app = Flask(__name__, static_folder='./static')
    app.config.update(config)

    app.add_url_rule('/',None,index)
    app.add_url_rule('/stream',None,stream)
    app.add_url_rule('/streamview',None,streamview)


    @app.context_processor
    def likker():
        return {'likker':'hallo'}

    @app.before_request
    def add_shared_data():
        g.shared_data = sharedData




    return app

if __name__ == '__main__':
    import yaml
    with open('../../measurement/config.yml') as f:
        config = yaml.load(f)

    app = create_app(config)
    app.run('localhost',5123,True)