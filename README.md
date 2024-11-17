# N-layer Model Web Application - https://n-layer.uc.r.appspot.com/

This repository contains the code for the N-layer model web application built with Flask. The N-layer model is a tool for analyzing and optimizing multi-layered security systems. The application provides two main types of analysis: **Probabilistic Model** and **Strategic Model**, allowing the user to configure the number of layers and associated costs.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Running the Web Application](#running-the-web-application)
  - [Using the N-layer Model](#using-the-n-layer-model)
  - [Models and Configuration](#models-and-configuration)
  - [Result Visualization](#result-visualization)
- [Code Structure](#code-structure)
- [Model Output](#Model-Output)


---



## Installation

To set up the project, you need to have Python 3.x installed on your system. Follow these steps to get started:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mohanagolleru/N_layer.git
   cd N_layer

2. Install the required dependencies:
```bash
   pip install -r requirements.txt
```
3. Start the Flask server:
```bash
   python app.py
```
---
# Usage

## Running the Web Application

Once the Flask server is running, open your web browser and navigate to the following address:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

This will take you to the **N-layer model** web interface, where you can interact with the application. You will be able to configure the model, select different options, and view the results in an intuitive interface.

### Steps to Use the N-layer Model:

1. **Select a Model Type**:
   - **Probabilistic Model**: This model evaluates systems facing non-strategic attackers.
   - **Strategic Model**: This model incorporates game theory to analyze systems dealing with strategic attackers.

2. **Configure the Model**:
   - Use the slider to set the **Total Layers**. The number of layers represents the number of security layers in the system.
   - Use the slider to set the **Cost**, which defines the total available budget for securing the layers.

3. **Generate the Solution**:
   Once you've configured the parameters, click the **Solve** button to generate the optimal solution based on your inputs. The results, including a stacked plot showing budget allocation, will be displayed on the results page.
---
# Models and Configuration

## Probabilistic Model

This model is designed to analyze systems that are exposed to non-strategic attackers. It calculates the probabilistic nature of defense across multiple layers based on system characteristics such as cost, risk, and attacker behavior.

## Strategic Model

The strategic model involves game-theoretic concepts to model interactions between attackers and defenders. It is useful in systems where attackers behave strategically to exploit vulnerabilities in the defense system.

---
# Result Visualization

Once the model is solved, the application generates a stacked plot showing the optimal budget allocation across the configured layers. You can also view the layer-specific configuration and results in a table format.

---
### Optimization Outputs


Displays the model type, solutions, and parameters such as `s`, `beta`, `alpha`, `theta`, `gamma`, `cost`, and `C_bar`.

---
   # Code Structure

   ```bash
   .
   ├── app.py                 # Main application file (Flask server)
   ├── requirements.txt       # List of Python dependencies
   ├── static/                # Static files (images)
   │   ├── css/               # CSS files for styling
   │   │   └── styles.css     # Main stylesheet for the web application
   │   └── images/            # Image assets
   ├── templates/             # HTML templates for Flask
   │   ├── base.html          # Base template with common HTML structure
   │   ├── index.html         # Home page template with form input
   │   ├── results.html       # Page template to display results and plots
   │   └── about.html         # About page template
   ├── models/                # Directory for model-related Python code
   │   ├── probabilistic.py   # Code for the probabilistic model
   │   └── strategic.py       # Code for the strategic model 
   ├── utils/                 # Utility scripts for helper functions
   │   └── visualization.py   # Helper functions for result visualization        
   └── README.md              # Project documentation                 
   ```

- **app.py**: This file acts as the central hub of the application, defining all routes for handling form submissions, managing optimization logic, and generating results for the user.
- **templates/**: Contains HTML templates that render the interface for the user. These include the form for input data, result display, and other pages like the About page.
- **static/**: Holds static assets such as CSS files for styling and images used within the web application (e.g., logos or graphical assets).
- **models/**: Contains Python scripts for implementing the core logic of the probabilistic and strategic models. These files are responsible for running the calculations for each model type.
- **utils/**: Utility functions, including scripts to handle result visualization and other helper tasks.
- **data/**: Placeholder for storing input data or any pre-configured datasets.
- **tests/**: Contains test cases to verify the accuracy and functionality of the models and utility functions.

---


## Model Output


![Model Output](N_layer/static/Model_O.png)






