from flask import Flask, render_template
from server import content, get_static, user, devices, friend, voice

app = Flask(__name__)

app.register_blueprint(content.content)
app.register_blueprint(get_static.get_static)
app.register_blueprint(user.user)
app.register_blueprint(devices.devices)
app.register_blueprint(friend.friend)
app.register_blueprint(voice.voice)


@app.route('/')
def WebToy():
    return render_template('web_toy.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 9527, debug=True)
