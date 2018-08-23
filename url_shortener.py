import os
from flask import Flask, Response, request, redirect
import json

app_home = os.environ['URL_SHORTENER']

__REDIR_FILE__ = app_home + "/redirects.json"
with open(__REDIR_FILE__) as f:
    redirs = json.load(f)

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def splash():
    if request.method == 'GET':
        return Response(json.dumps({'success': 'the service is running. try visiting go/help'}))
    else:
        try:
            data = request.get_json()
            req_keys = data.keys()
        except AttributeError:
            return Response(json.dumps({'error': 'empty request body'}))
        if 'url' not in req_keys and 'link' not in req_keys:
            return Response(json.dumps({'error': 'invalid request body'}))
        elif 'url' in req_keys and 'link' in req_keys:
            redirs.update({data['link']: data['url']})
            with open(__REDIR_FILE__, 'w') as f:
                json.dump(redirs, f)
            return redirect(data['url'], 302)


@app.route("/<link>", methods=['GET'])
def go(link):
    if link in redirs.keys():
        return redirect(redirs[link], code=302)
    else:
        return Response(json.dumps({"error": "link does not exist for %s" % (link)}))


@app.route("/goog")
def goog():
    return redirect("https://www.google.com", code=302)


if __name__ == "__main__":
    app.run(debug=True)
