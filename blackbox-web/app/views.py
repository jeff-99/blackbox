from flask import  Response, g, stream_with_context, render_template
import time, json


# @app.route('/')
def index():
    return render_template('index.html', zuiger='hannes')


# @app.route('/streamview')
def streamview():
    return render_template('streamtest.html')


# @app.route('/stream')
def stream():
    def generate():
        count = 44945
        while True:
            if hasattr(g,'shared_data') and not g.shared_data is None:
                msg = ""
                if 'measurement' in g.shared_data:
                    msg = "event:{}\ndata:{}\n\n".format('measurement',g.shared_data['measurement'])

                if count > 0:
                    msg += "event:{}\ndata:{}\n\n".format('other', count)
                count += 1
                yield msg
            else:
                yield "event:{}\ndata:{}\n\n".format('measurement', json.dumps({'measurement': {'latitude': 40.741895, 'longitude': -73.989308}}))
            time.sleep(5)

    return Response(stream_with_context(generate()),mimetype="text/event-stream")