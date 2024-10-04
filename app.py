from flask import Flask, render_template, Response, request
from new_customer import recognize_and_store_face, generate_frames
from view_customer import view_customer_bp  # Import the blueprint

app = Flask(__name__)
app.register_blueprint(view_customer_bp)  # Register the blueprint


@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    return recognize_and_store_face(request)

@app.route('/enroll_face', methods=['GET', 'POST'])
def enroll_face():
    if request.method == 'POST':
        return recognize_and_store_face(request, enroll=True)
    return render_template('enroll_face.html')

@app.route('/view_customers')
def view_customers_route():
    # Fetch customer data and render it in the template
    customer_data = view_customers().get_json()  # Call the function directly here
    return render_template('view_customer.html', customers=customer_data)

if __name__ == '__main__':
    app.run(debug=True)
