from flask import Flask, render_template_string, request, redirect, url_for, jsonify, make_response
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import copy
import seaborn as sns
import io
import base64
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)




form_template = """
<!DOCTYPE html>
<html>
<head>
    <title>N-layer Model</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Open Sans', sans-serif;
        }
        .navbar {
            background-color: #007bff;
            color: #fff;
        }
        .navbar-brand {
            color: #fff;
            font-weight: bold;
        }
        .container-fluid {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            min-width: 250px;
            max-width: 250px;
            background-color: #343a40;
            padding: 20px;
            color: #fff;
        }
        .sidebar .nav-link {
            color: #fff;
            font-weight: bold;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .sidebar .nav-link:hover {
            background-color: #495057;
        }
        .main-content {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
        }
        .card-header {
            background-color: #007bff;
            color: #fff;
            border-radius: 10px 10px 0 0;
            padding: 20px;
            text-align: center;
        }
        .card-body {
            padding: 30px;
        }
        .form-group label {
            font-weight: bold;
        }
        .btn-primary {
            background-color: #007bff;
            border-color: #007bff;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        .btn-primary:hover {
            background-color: #0069d9;
            border-color: #0062cc;
        }
        .model-description {
            margin-top: 20px;
            text-align: center;
            font-size: 16px;
            color: #6c757d;
        }
        .form-check-input:checked ~ .form-check-label::before {
            background-color: #007bff;
        }
        .footer {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            position: fixed;
            width: 100%;
            bottom: 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <a class="navbar-brand" href="#">N-layer Model</a>
    </nav>
    <div class="container-fluid">
        <div class="sidebar">
            <nav class="nav flex-column">
                <a class="nav-link" href="/">Model</a>
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/contact">Contact</a>
            </nav>
        </div>
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">Configuration</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <form action="/results" method="post">
                                <div class="form-group">
                                    <label>Model Type:</label>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="model_type" id="prob" value="prob" checked>
                                        <label class="form-check-label" for="prob">Probabilistic Model</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="model_type" id="stra" value="stra">
                                        <label class="form-check-label" for="stra">Strategic Model</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="total_layers">Total Layers:</label>
                                    <input type="number" class="form-control" name="total_layers" id="total_layers" required>
                                </div>
                                <div class="form-group">
                                    <label for="C_bar_init">Cost:</label>
                                    <input type="number" class="form-control" name="C_bar_init" id="C_bar_init" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Submit</button>
                            </form>
                        </div>
                        <div class="col-md-6">
                            <h4 class="text-center"><i class="fas fa-sitemap"></i> Game Tree</h4>
                            <img src="{{ url_for('static', filename='image.png') }}" alt="Model Configuration Image" class="img-fluid rounded">
                            <div id="model-description" class="model-description">
                                Probabilistic model is to model Non-Strategic Attackers.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

results_template = """

<!DOCTYPE html>
<html>
<head>
    <title>N-layer App Results</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Open Sans', sans-serif;
        }
        .navbar {
            background-color: #007bff;
            color: #fff;
        }
        .navbar-brand {
            color: #fff;
            font-weight: bold;
        }
        .container-fluid {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            min-width: 250px;
            max-width: 250px;
            background-color: #343a40;
            padding: 20px;
            color: #fff;
        }
        .sidebar .nav-link {
            color: #fff;
            font-weight: bold;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .sidebar .nav-link:hover {
            background-color: #495057;
        }
        .main-content {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
        }
        .card-header {
            background-color: #007bff;
            color: #fff;
            border-radius: 10px 10px 0 0;
            padding: 20px;
            text-align: center;
        }
        .card-body {
            padding: 30px;
        }
        .form-group label {
            font-weight: bold;
        }
        .btn-primary {
            background-color: #007bff;
            border-color: #007bff;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        .btn-primary:hover {
            background-color: #0069d9;
            border-color: #0062cc;
        }
        .table {
            margin-bottom: 0;
        }
        .table thead th {
            background-color: #f8f9fa;
            border-top: none;
        }
        .table td, .table th {
            vertical-align: middle;
        }
        .plot-container {
            margin-top: 30px;
            width: 105%;
            height: 400px;
            overflow: hidden;
        }
        .plot-container img {
            max-width: 100%;
            height: auto;
        }
        .model-description {
            margin-top: 20px;
            text-align: center;
            font-size: 16px;
            color: #6c757d;
        }
        .footer {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            position: fixed;
            width: 100%;
            bottom: 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <a class="navbar-brand" href="#">N-layer Model</a>
    </nav>
    <div class="container-fluid">
        <div class="sidebar">
            <nav class="nav flex-column">
                <a class="nav-link" href="/">Model</a>
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/contact">Contact</a>
            </nav>
        </div>
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">N-layer Model Results</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h4><i class="fas fa-cog"></i> Configuration</h4>
                            <form action="/results" method="post">
                                <div class="form-group">
                                    <label>Model Type:</label>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="model_type" id="prob" value="prob" {% if model_type == 'prob' %}checked{% endif %}>
                                        <label class="form-check-label" for="prob">Probabilistic Model</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="model_type" id="stra" value="stra" {% if model_type == 'stra' %}checked{% endif %}>
                                        <label class="form-check-label" for="stra">Strategic Model</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="total_layers">Total Layers:</label>
                                    <input type="number" class="form-control" name="total_layers" id="total_layers" value="{{ total_layers }}" required>
                                </div>
                                <div class="form-group">
                                    <label for="C_bar_init">Cost:</label>
                                    <input type="number" class="form-control" name="C_bar_init" id="C_bar_init" value="{{ C_bar_init }}" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Update</button>
                            </form>
                        </div>
                        <div class="col-md-6">
                            <h4><i class="fas fa-sitemap"></i> Game Tree</h4>
                            <img src="{{ url_for('static', filename='image.png') }}" alt="Model Configuration Image" class="img-fluid rounded">
                            <div id="model-description" class="model-description">
                                {% if model_type == 'prob' %}
                                Probabilistic model is to model Non-Strategic Attackers.
                                {% else %}
                                Strategic model is to model Strategic Attackers.
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h4><i class="fas fa-table"></i> Optimization Outputs</h4>
                            <table class="table table-striped">
                                <tbody>
                                    <tr>
                                        <th>Model</th>
                                        <td>{{ model }}</td>
                                    </tr>
                                    <tr>
                                        <th>Solutions</th>
                                        <td>{{ solutions }}</td>
                                    </tr>
                                </tbody>
                            </table>
                            <h5>Values:</h5>
                            <ul class="list-unstyled">
                                <li><strong>s:</strong> {{ s }}</li>
                                <li><strong>beta:</strong> {{ beta }}</li>
                                <li><strong>alpha:</strong> {{ alpha }}</li>
                                <li><strong>theta:</strong> {{ theta }}</li>
                                <li><strong>gamma:</strong> {{ gamma }}</li>
                                <li><strong>cost:</strong> {{ cost }}</li>
                                <li><strong>C_bar:</strong> {{ C_bar }}</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h4><i class="fas fa-chart-area"></i> Optimal Investment Across Layers</h4>
                            <div class="plot-container">
                                <img src="data:image/png;base64,{{ plot_url }}" alt="N-layer Results Plot" class="img-fluid rounded">
                            </div>
                        </div>
                    </div>
                    <!-- New section for layer-specific images -->
                    <div class="row mt-4">
                        <div class="col-12">
                            <h4><i class="fas fa-layer-group"></i> Layer-Specific Configuration</h4>
                            {% if layer_image %}
                                <img src="{{ url_for('static', filename=layer_image) }}" alt="Layer Configuration" class="img-fluid rounded">
                            {% else %}
                                <p>No specific layer configuration image available for {{ total_layers }} layers.</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
       

# About template

about_template = """
<!DOCTYPE html>
<html>
<head>
    <title>About</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Open Sans', sans-serif;
        }
        .navbar {
            background-color: #007bff;
            color: #fff;
        }
        .navbar-brand {
            color: #fff;
            font-weight: bold;
        }
        .container-fluid {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            min-width: 250px;
            max-width: 250px;
            background-color: #343a40;
            padding: 20px;
            color: #fff;
        }
        .sidebar .nav-link {
            color: #fff;
            font-weight: bold;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .sidebar .nav-link:hover {
            background-color: #495057;
        }
        .main-content {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
        }
        .card-header {
            background-color: #007bff;
            color: #fff;
            border-radius: 10px 10px 0 0;
            padding: 20px;
            text-align: center;
        }
        .card-body {
            padding: 30px;
        }
        .footer {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            position: fixed;
            width: 100%;
            bottom: 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <a class="navbar-brand" href="#">About</a>
    </nav>
    <div class="container-fluid">
        <div class="sidebar">
            <nav class="nav flex-column">
                <a class="nav-link" href="/">N-layer Model</a>
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/contact">Contact</a>
            </nav>
        </div>
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">About</h2>
                </div>
                <div class="card-body">
                    <p class="text-center">About Model.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>


"""
# Contact template

contact_template = """


<!DOCTYPE html>
<html>
<head>
    <title>Contact</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Open Sans', sans-serif;
        }
        .navbar {
            background-color: #007bff;
            color: #fff;
        }
        .navbar-brand {
            color: #fff;
            font-weight: bold;
        }
        .container-fluid {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            min-width: 250px;
            max-width: 250px;
            background-color: #343a40;
            padding: 20px;
            color: #fff;
        }
        .sidebar .nav-link {
            color: #fff;
            font-weight: bold;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .sidebar .nav-link:hover {
            background-color: #495057;
        }
        .main-content {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
        }
        .card-header {
            background-color: #007bff;
            color: #fff;
            border-radius: 10px 10px 0 0;
            padding: 20px;
            text-align: center;
        }
        .card-body {
            padding: 30px;
        }
        .footer {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            position: fixed;
            width: 100%;
            bottom: 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <a class="navbar-brand" href="#">Contact</a>
    </nav>
    <div class="container-fluid">
        <div class="sidebar">
            <nav class="nav flex-column">
                <a class="nav-link" href="/">N-layer Model</a>
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/contact">Contact</a>
            </nav>
        </div>
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">Contact</h2>
                </div>
                <div class="card-body">
                    <p class="text-center">For any inquiries or feedback, please contact us at: <a href="mailto:support@nlayermodel.com">support@nlayermodel.com</a></p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


# Initialization functions
class instance_nLY:
    def __init__(self, s=[], beta=[], alpha=[], theta=[], gamma=[], cost=[], C_bar=[]):
        self.s = s
        self.beta = beta
        self.alpha = alpha
        self.theta = theta
        self.gamma = gamma
        self.cost = cost
        self.C_bar = C_bar

    def print_values(self):
        print("s =", self.s)
        print("beta =", self.beta)
        print("alpha =", self.alpha)
        print("theta =", self.theta)
        print("gamma =", self.gamma)
        print("cost =", self.cost)
        print("C_bar =", self.C_bar)

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

def objective_prob(Y, _nLayers):
    global obj2
    f = [None] * _nLayers
    for i in range(len(f)):
        f[i] = np.exp(-1 * sum([obj2.gamma[i-k] * obj2.theta[k] * Y[k] for k in range(i+1)]))
    raw_risk = [_s * _beta * _alpha for _s, _beta, _alpha in zip(obj2.s, obj2.beta, obj2.alpha)]
    return sum(a * b for a, b in zip(raw_risk, f))

def objective_stra(Y, _nLayers):
    global obj2
    f = [None] * _nLayers
    for i in range(len(f)):
        f[i] = np.exp(-1 * sum([obj2.gamma[i-k] * obj2.theta[k] * Y[k] for k in range(i+1)]))
    raw_risk = [_s * _alpha for _s, _alpha in zip(obj2.s, obj2.alpha)]
    return max(a * b for a, b in zip(raw_risk, f))

def constraint(Y, obj2):
    return obj2.C_bar - sum(a * b for a, b in zip(obj2.cost, Y))

def get_numerical_sol(init_val, _model, _nLayers, obj2):
    Y0 = init_val
    b = (0.0, None)
    bnds = (b,) * _nLayers
    con1 = {'type': 'eq', 'fun': lambda Y: constraint(Y, obj2)}
    cons = ([con1])
    if _model == 'prob':
        solution = minimize(lambda Y: objective_prob(Y, _nLayers), Y0, method='SLSQP', bounds=bnds, constraints=cons)
        x = solution.x
        x = [round(i, 4) for i in x]
        obj_value = round(objective_prob(x, _nLayers), 4)
    elif _model == 'stra':
        solution = minimize(lambda Y: objective_stra(Y, _nLayers), Y0, method='SLSQP', bounds=bnds, constraints=cons)
        x = solution.x
        x = [round(i, 4) for i in x]
        obj_value = round(objective_stra(x, _nLayers), 4)
    else:
        print("Something is wrong here......(get_numerical_sol)")
    return flatten_list([obj_value, x])

def addRow(df, ls):
    numEl = len(ls)
    newRow = pd.DataFrame(np.array(ls).reshape(1, numEl), columns=list(df.columns))
    df = pd.concat([df, newRow], ignore_index=True)
    return df

def get_full_sol(_nLayers, whichmodel, obj2, vars_col):
    intial_sol = [3] * _nLayers
    solutions = get_numerical_sol(intial_sol, whichmodel, _nLayers, obj2)
    required_length = len(vars_col)
    while len(solutions) < required_length:
        solutions.append(0)
    return solutions[:required_length]

def initialization(_nLayers, C_bar_init):
    gam = 0.5
    s_init = [500 for i in range(1, _nLayers+1)]
    alpha_init = [0.5] * _nLayers
    beta_init = [1 / _nLayers] * _nLayers
    theta_init = [0.4] * _nLayers
    cost_init = [1 for i in range(1, _nLayers+1)]
    gamma_init = [1] + [gam**i for i in range(1, _nLayers)]
    obj_base = instance_nLY(s=s_init, alpha=alpha_init, beta=beta_init, theta=theta_init, cost=cost_init, gamma=gamma_init, C_bar=C_bar_init)
    return obj_base

def generate_plot(whichmodel, solution_df, total_layers, obj2):
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    global obj2

    if request.method == 'POST':
        model_type = request.form.get('model_type')
        total_layers = int(request.form.get('total_layers'))
        C_bar_init = float(request.form.get('C_bar_init'))

        app.logger.info(f"Total Layers: {total_layers}")
        app.logger.info(f"C_bar_init: {C_bar_init}")

        vars_col = ['obj_value'] + ['y' + str(i+1) for i in range(total_layers)]
        model_set = ['prob', 'stra']
        prob_solutions = None
        stra_solutions = None

        labels = ['Layer ' + str(i+1) for i in range(total_layers)]
        plot_urls = {}

        # Select the appropriate image based on total_layers
        layer_image = None
        if total_layers in [1, 2, 3, 4]:
            layer_image = f"layer{total_layers}.png"

        for m in range(len(model_set)):
            whichmodel = model_set[m]
            solution_df = pd.DataFrame(columns=vars_col)

            for i in range(total_layers):
                _nLayers = i + 1
                obj_base = initialization(_nLayers, C_bar_init)
                obj2 = copy.deepcopy(obj_base)
                solutions = get_full_sol(_nLayers, whichmodel, obj2, vars_col)
                solution_df = addRow(solution_df, solutions)
            
            solution_df["Layers"] = [i for i in range(1, total_layers+1)] 

            if whichmodel == 'prob':
                prob_solutions = solutions
            elif whichmodel == 'stra':
                stra_solutions = solutions
            else:
                print("Something is wrong.")

            finaldata = pd.DataFrame()
            for i in range(0, total_layers):
                new_name = 'invest' + str(i+1)
                old_name = 'y' + str(i+1)
                finaldata[new_name] = obj2.cost[i] * solution_df[old_name]

            data_perc = 100 * finaldata[finaldata.columns.values.tolist()].divide(finaldata[finaldata.columns.values.tolist()].sum(axis=1), axis=0)
            data_perc["Layers"] = [i for i in range(1, total_layers+1)]

            for i in range(1, total_layers + 1):
                col = 'invest' + str(i)
                data_perc[col] = pd.to_numeric(data_perc[col], errors='coerce')

            plt.stackplot(data_perc['Layers'],
                          [data_perc['invest' + str(i+1)] for i in range(total_layers)],
                          labels=labels,
                          colors=sns.color_palette(("Greys"), total_layers),
                          alpha=1, edgecolor='grey')

            plt.margins(x=0)
            plt.margins(y=0)
            plt.rcParams['font.size'] = 15
            if whichmodel == 'prob':
                plt.ylabel("Budget allocation (%)", fontsize=18)
                plt.xlabel("Number of layers for LRA-PR Model", fontsize=18)
            if whichmodel == 'stra':
                plt.xlabel("Number of layers for LRA-SR Model", fontsize=18)

            plt.legend(fontsize=14, markerscale=2, loc='center left', bbox_to_anchor=(1.2, 0.5), fancybox=True, shadow=True, ncol=1)

            plot_urls[whichmodel] = generate_plot(whichmodel, solution_df, total_layers, obj2)

        if model_type == 'prob':
            display_solutions = prob_solutions
            display_model = 'prob'
        else:
            display_solutions = stra_solutions
            display_model = 'stra'

        return render_template_string(
            results_template,
            model_type=model_type,
            plot_url=plot_urls[display_model],
            total_layers=total_layers,
            C_bar_init=C_bar_init,
            model=display_model,
            solutions=str(display_solutions),
            s=str(obj2.s),
            beta=str(obj2.beta),
            alpha=str(obj2.alpha),
            theta=str(obj2.theta),
            gamma=str(obj2.gamma),
            cost=str(obj2.cost),
            C_bar=str(obj2.C_bar),
            layer_image=layer_image)  # New parameter for layer-specific image

    return render_template_string(form_template)

@app.route('/about')
def about():
    return render_template_string(about_template)

@app.route('/contact')
def contact():
    return render_template_string(contact_template)

@app.route('/results', methods=['POST'])
def results():
    return index()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

#if __name__ == "__main__":
#    app.run(debug=True, port=5000)
