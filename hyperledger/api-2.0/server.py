# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_data():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract information from the data
    client_id = data.get('clientID')
    train_count = data.get('trainCount')
    val_count = data.get('valCount')
    print("Currently in the python server")
    print(client_id)
    print(train_count)
    print(val_count)


    # Perform some processing with the data (example: summing counts)
    total_count = train_count + val_count

    # Create a response
    response = {
        'clientID': client_id,
        'totalCount': total_count,
        'message': 'Data processed successfully'
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
