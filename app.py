from flask import Flask, render_template

app = Flask(__name__)

# Main dashboard route
@app.route('/')
def dashboard():
    # Add dynamic data such as total_users, total_items_tracked, etc.
    return render_template('dashboard.html', total_users=120, total_items_tracked=300, 
                           recent_payments=25, recognized_faces=15, receipts_generated=20, cars_in_parking=5)


if __name__ == '__main__':
    app.run(debug=True)
