from flask import Flask, request, jsonify, make_response
from functools import wraps

app = Flask(__name__)

def cors_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
        else:
            response = make_response(f(*args, **kwargs))

        # Add CORS headers to every response
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    return decorated_function

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

@app.route('/test', methods=['GET', 'OPTIONS'])
@cors_middleware
def test():
    return jsonify({"message": "CORS test successful"})

if __name__ == '__main__':
    print("Starting server on http://localhost:5001")
    print("CORS enabled for origin: http://localhost:3000")
    app.run(debug=True, port=5001, host='0.0.0.0')
