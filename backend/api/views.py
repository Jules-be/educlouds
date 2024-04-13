from flask import Blueprint, render_template, request, jsonify, redirect, url_for

views = Blueprint('views', __name__)

lender_resources = []
borrower_requests = []

# For Lender specs and Borrowers required resources
# { high, medium, low }

# Home page
@views.route('/')
def home():
    return render_template("home.html")

# Routes for lenders
@views.route('/api/lenders/addResource', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        resource_type = request.form.get('type')
        specifications = request.form.get('specifications')
        availability_status = request.form.get('availabilityStatus')

        lender_resources.append({
            'type': resource_type,
            'specifications': specifications,
            'availabilityStatus': availability_status
        })
        return redirect(url_for('views.view_resources'))
    else:
        return render_template('lender.html')

@views.route('/api/lenders/viewResources', methods=['GET'])
def view_resources():
    return render_template('viewResources.html', resources=lender_resources)

# Routes for borrowers
@views.route('/api/borrowers/submitRequest', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        required_resources = request.form.get('requiredResources')
        estimated_workload = request.form.get('estimatedWorkload')

        borrower_requests.append({
            'requiredResources': required_resources,
            'python_version': python_version,
            'required_dependencies': required_dependencies,
        })
        return redirect(url_for('views.view_requests'))
    else:
        return render_template('borrower.html')

@views.route('/api/borrowers/viewRequests', methods=['GET'])
def view_requests():
    return render_template('viewRequest.html', requests=borrower_requests)



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = str(uuid.uuid4()) + '.py'
        filepath = os.path.join('./uploads', filename)
        file.save(filepath)

        # Run security checks
        bandit_output = run_bandit(filepath)
        safety_output = run_safety('requirements.txt')

        if "ERROR" in bandit_output or "ERROR" in safety_output:
            return jsonify({'error': 'Security check failed', 'bandit': bandit_output, 'safety': safety_output}), 400

        # Proceed to Docker execution if checks pass
        result = run_in_docker(filepath)
        return jsonify(result), 200
