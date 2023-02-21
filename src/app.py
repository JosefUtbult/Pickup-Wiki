from flask import Flask, render_template, abort, request, jsonify
from pathlib import Path
import json
from math import floor, ceil

app = Flask(__name__)

# Exception raised if the type of a key is incorrect 
class PickupParsingException(Exception):
    pass

def parse_pickup_instance(instance):
    instance_id = instance['id'] if 'id' in instance else "unspecified"
    # instance_id = instance['id'] if 'id' in instance else 'unspecified'

    # Check for mandatory keys that should be strings
    for key in ("id", "name", "brand", "type", "strings"):
        if not key in instance:
            raise KeyError(f"{key} not in instance {instance_id}")

    for key in ("id", "name", "brand", "type"):
        if not type(instance[key]) is str:
            raise PickupParsingException(f"{key} should be of the type string in instance {instance_id}")

    for key in ("strings",):
        if not type(instance[key]) in (int, float):
            raise PickupParsingException(f"{key} should be of the type int or float in instance {instance_id}")


def generate_set(instrument, key):
    res = []
    for _key in app.pickup_data[instrument]:
        try:
            res.append(app.pickup_data[instrument][_key][key])
        except (IndexError, KeyError):
            pass

    res = list(dict.fromkeys(res))
    return res


def generate_range(instrument, key):
    set = generate_set(instrument, key)
    return (floor(min(set)), ceil(max(set)))


def setup():
    app.pickup_data = {
        "bass": {}
    }

    # Add checks for duplicate ids
    for filepath in (Path(__file__).resolve().parent / Path("static") / Path("data") / Path("pickups") / Path("bass")).iterdir():
        app.logger.info(f"Parsing file {filepath}")

        try:
            with open(filepath, 'r') as file:
                res = json.loads(file.read())
                for instance in res if type(res) is list else [res]:
                    parse_pickup_instance(instance)
                    instance_id = instance.pop('id')
                    app.pickup_data['bass'][instance_id] = instance

        except Exception as e:
            app.logger.error(f"Exception in reading file {filepath} - {type(e).__name__}: {e}")

    app.bass_pickup_filter = {
        'brands': generate_set('bass', 'brand'),
        'types': generate_set('bass', 'type'),
        'strings': generate_set('bass', 'strings'),
        'positions': generate_set('bass', 'position'),
        'width': generate_range('bass', 'width'),
        'height': generate_range('bass', 'height'),
        'depth': generate_range('bass', 'depth'),
    }


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/pickup_data.json", methods=['GET', 'POST'])
def pickup_data():
    return jsonify(app.pickup_data)
    

@app.route("/bass-pickups")
def bass_pickups():
    return render_template(
        "bass_pickups.html", 
        pickup_data=app.pickup_data, 
        filter=app.bass_pickup_filter
    )


@app.route("/bass-pickups/<key>")
def pickup_instance(key):
    if key in app.pickup_data['bass']:
        return render_template("pickup_instance.html", id=key, instance=app.pickup_data['bass'][key])
    else:
        return abort(404)


if __name__ == "__main__":
    setup()
    app.run(debug=True)


# TODO: Add program arguments for ignoring files with errors