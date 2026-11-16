from flask import Flask, request, render_template
from wikidata_local_reconciliator import WikidataLocalReconciliator
from wikidata_occupation import WikidataOccupation
import json

app = Flask(__name__)

DEFAULT_YEAR = 2024


def candidate_names(name, surname):
    """Nomi completi da provare, in ordine.
    - name + surname -> "nome cognome", poi "cognome nome"
    - solo name      -> name così com'è (compatibilità: nome completo in un solo campo)
    - solo surname   -> surname
    """
    name = ' '.join((name or '').split())
    surname = ' '.join((surname or '').split())
    if name and surname:
        return [f'{name} {surname}', f'{surname} {name}']
    if name:
        return [name]
    if surname:
        return [surname]
    return []


def parse_year(year):
    try:
        return int(year) if year else DEFAULT_YEAR
    except ValueError:
        return DEFAULT_YEAR


def reconcile(names, year, occupations):
    reconciliator = WikidataLocalReconciliator()
    try:
        for full_name in names:
            result = reconciliator.ask(full_name, year, occupations)
            if result:
                return result
        return None
    finally:
        reconciliator.close()


def json_response(data, status=200):
    return app.response_class(
        response=json.dumps(data, default=tuple),
        status=status,
        mimetype='application/json')


@app.route('/api/v1/s', methods=['GET'])
def api_search():
    names = candidate_names(request.args.get('name'), request.args.get('surname'))
    if not names:
        return json_response({'error': 'name or surname is required'}, 400)

    try:
        result = reconcile(names,
                           parse_year(request.args.get('year')),
                           request.args.get('occupations'))
    except KeyError as e:
        return json_response({'error': f'unknown occupation: {e.args[0]}'}, 400)

    return json_response(result)


@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name')
    names = candidate_names(name, request.form.get('surname'))
    if not names:
        return "No result"

    try:
        result = reconcile(names,
                           parse_year(request.form.get('year')),
                           ", ".join(request.form.getlist('occupations')))
    except KeyError as e:
        return f"Unknown occupation: {e.args[0]}"

    if result:
        return render_template('search.html', name=name, result=result)
    return "No result"


@app.route('/', methods=['GET'])
def index():
    wd_occupation = WikidataOccupation()
    return render_template('index.html', occupations=wd_occupation.occupations_by_name)


if __name__ == '__main__':
    app.run(debug=True)
