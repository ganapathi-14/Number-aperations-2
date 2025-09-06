from flask import Flask, request, redirect, url_for, session, render_template_string
import math, datetime, os, sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_FILE = "user_activity.db"
ADMIN_PASSWORD = "admin123"

# ---------------- Database Setup ---------------- #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            action TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Initialize DB on startup

# ---------------- Utility ---------------- #
def log_activity(username, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, username, action, details) VALUES (?, ?, ?, ?)",
              (timestamp, username, action, details))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, username, action, details FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- Math Functions ---------------- #
def is_armstrong(n): 
    return sum(int(d)**len(str(n)) for d in str(n)) == n

def is_even(n): 
    return n % 2 == 0

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_palindrome(n): 
    return str(n) == str(n)[::-1]

def factorial(n): 
    return math.factorial(n)

def sum_digits(n): 
    return sum(int(d) for d in str(n))

def reverse_number(n): 
    return int(str(n)[::-1])

def square(n): 
    return n**2

def cube(n): 
    return n**3

def count_digits(n): 
    return len(str(n))

functions_dict = {
    "armstrong": "Check Armstrong",
    "evenodd": "Even or Odd",
    "prime": "Check Prime",
    "palindrome": "Check Palindrome",
    "factorial": "Factorial",
    "sumdigits": "Sum of Digits",
    "reverse": "Reverse Number",
    "square": "Square",
    "cube": "Cube",
    "countdigits": "Count Digits"
}

# ---------------- Templates ---------------- #
index_template = """<!DOCTYPE html>
<html>
<head><title>Welcome - Sai Ganapathi</title></head>
<body style="background:#0288d1;color:white;text-align:center;font-family:Arial;">
  <div style="margin-top:5%; margin-bottom:30px;">
    <h1 style="color:#ffeb3b; font-size:32px; font-weight:bold; text-shadow:1px 1px 5px #000;">
      👋 Hello, Welcome! This page is created by Sai Ganapathi
    </h1>
  </div>
  <div style="margin-top:5%; background:#003f7f; padding:40px; border-radius:12px; display:inline-block; box-shadow:0px 0px 20px rgba(0,0,0,0.3);">
    <h1 style="margin-bottom:20px;">Choose Mode</h1>
    <a href="{{ url_for('home') }}">
      <button style="margin:10px; padding:15px 25px; font-size:18px; border:none; border-radius:8px; background:#ff9800; color:white; cursor:pointer;">User/NewUser</button>
    </a>
    <a href="{{ url_for('admin_login') }}">
      <button style="margin:10px; padding:15px 25px; font-size:18px; border:none; border-radius:8px; background:#1976d2; color:white; cursor:pointer;">Admin</button>
    </a>
  </div>
</body>
</html>"""

home_template = """<!DOCTYPE html><html><head><title>User Login</title></head>
<body style="background:#0288d1;color:white;text-align:center;font-family:Arial;">
  <div style="margin-top:10%; display:inline-block; background:#1976d2; padding:30px; border-radius:12px; box-shadow:0px 0px 20px rgba(0,0,0,0.3);">
    <h1 style="margin-bottom:20px;">Enter Your Name</h1>
    <form method="POST">
      <input type="text" name="username" placeholder="Your Name" style="padding:10px; border:none; border-radius:5px;" required>
      <button type="submit" style="padding:10px 20px; margin-left:10px; background:#ff9800; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Submit</button>
    </form>
  </div>
</body></html>"""

menu_template = """<!DOCTYPE html><html><head><title>Menu</title></head>
<body style="background:#0288d1;color:white;text-align:center;font-family:Arial;">
  <h1>Hello {{ username }}! Welcome 🎉</h1>
  <div style="margin:20px;">
    {% for func, label in functions.items() %}
      <a href="{{ url_for('check', function_name=func) }}">
        <button style="margin:10px; padding:15px 25px; font-size:16px; font-weight:bold; border:none; border-radius:8px; color:#FFFFFF; background:#003399; cursor:pointer;">
          {{ label }}
        </button>
      </a>
    {% endfor %}
  </div>
  <br><h3>Give Me Feedback Here👇</h3>
  <form id="feedback-form">
    <input type="text" name="body" placeholder="Enter feedback here..." style="width:600px; padding:10px;" required>
    <button type="submit" style="padding:10px 20px; background:#ff9800; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Submit Feedback</button>
  </form>
  <div id="feedback-status" style="margin-top:10px;"></div>
  <br><a href="{{ url_for('logout') }}" style="color:white;">Exit</a>
<script>
document.getElementById('feedback-form').addEventListener('submit', async function(e){
  e.preventDefault();
  const endpoint = "https://formspree.io/f/xpwjovby";
  const form = e.target;
  const formData = new FormData(form);
  formData.append("username", "{{ username }}");
  const statusDiv = document.getElementById('feedback-status');
  statusDiv.textContent = "Sending...";
  try {
    const res = await fetch(endpoint, {method:"POST",body:formData,headers:{ "Accept":"application/json"}});
    if (res.ok) {statusDiv.style.color="lightgreen";statusDiv.textContent="✅ Feedback submitted. Thank You😊!";form.reset();}
    else {statusDiv.style.color="salmon";statusDiv.textContent="❌ Failed to submit.";}
  } catch {statusDiv.style.color="salmon";statusDiv.textContent="❌ Network error.";}
});
</script>
<script>
window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/track_exit");
});
</script>
</body></html>"""

check_template = """<!DOCTYPE html><html><head><title>{{ function_name }}</title></head>
<body style="background:#0288d1;color:white;text-align:center;font-family:Arial;">
  <div style="margin-top:10%; display:inline-block; background:#003f7f; padding:40px; border-radius:12px; box-shadow:0px 0px 20px rgba(0,0,0,0.3);">
    <h1>{{ function_name.replace("_"," ").title() }}</h1>
    <form method="POST">
      <input type="number" name="number" placeholder="Enter number" required>
      <button type="submit" style="margin-top:10px; padding:10px 20px; background:#ff9800; color:white; border:none; border-radius:5px; cursor:pointer;">Check</button>
    </form>
{% if result is not none %}
  <div style="margin-top:20px; font-size:18px; font-weight:bold; color:{% if 'NOT' in result or 'Not' in result %}#f44336{% else %}#4caf50{% endif %};">
    Result: {{ result }}
  </div>
{% endif %}
    <a href="{{ url_for('menu') }}" style="display:block; margin-top:20px; color:white;">← Back to Menu</a>
  </div>
</body></html>"""

admin_login_template = """<!DOCTYPE html><html><head><title>Admin Login</title></head>
<body style="background:#0288d1;color:white;text-align:center;font-family:Arial;">
  <div style="margin-top:15%; display:inline-block; background:#003f7f; padding:40px; border-radius:12px; box-shadow:0px 0px 20px rgba(0,0,0,0.3);">
    <h2>Admin Login</h2>
    <form method="POST">
      <input type="password" name="password" placeholder="Enter password" required>
      <button type="submit" style="margin-top:10px; padding:10px 20px; background:#ff9800; color:white; border:none; border-radius:5px; cursor:pointer;">Login</button>
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <br><a href="{{ url_for('index') }}" style="color:white;">← Back</a>
  </div>
</body></html>"""

logs_template = """<!DOCTYPE html><html><head><title>Logs</title></head>
<body style="font-family:monospace;background:#111;color:#0f0;padding:20px;">
  <h2>User Activity Logs</h2>
  <pre>{{ logs }}</pre>
  <br><a href="{{ url_for('index') }}" style="color:yellow;">← Back to Home</a>
</body></html>"""

# ---------------- Routes ---------------- #
@app.route("/")
def index():
    session.clear()
    return render_template_string(index_template)

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session['username'] = request.form['username']
        session['login_time'] = datetime.datetime.now().timestamp()
        log_activity(session['username'], "Login", "Entered the site")
        return redirect(url_for('menu'))
    return render_template_string(home_template)

@app.route("/menu")
def menu():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template_string(menu_template, username=session['username'], functions=functions_dict)

@app.route("/check/<function_name>", methods=["GET", "POST"])
def check(function_name):
    if 'username' not in session:
        return redirect(url_for('home'))
    result = None
    if request.method == "POST":
        try:
            number = int(request.form['number'])
            if function_name == "armstrong": 
                result = f"{number} is {'an Armstrong number✅' if is_armstrong(number) else 'NOT an Armstrong number❌'}"
            elif function_name == "evenodd": 
                result = f"{number} is {'Even' if is_even(number) else 'Odd'}"
            elif function_name == "prime": 
                result = f"{number} is {'Prime✅' if is_prime(number) else 'Not Prime❌'}"
            elif function_name == "palindrome": 
                result = f"{number} is {'Palindrome✅' if is_palindrome(number) else 'Not Palindrome❌'}"
            elif function_name == "factorial":
                if number < 0:
                    result = "❌ Factorial not defined for negative numbers"
                else:
                    result = f"Factorial of {number} is {factorial(number)}"
            elif function_name == "sumdigits": 
                result = f"Sum of digits of {number} is {sum_digits(number)}"
            elif function_name == "reverse": 
                result = f"Reverse of {number} is {reverse_number(number)}"
            elif function_name == "square": 
                result = f"Square of {number} is {square(number)}"
            elif function_name == "cube": 
                result = f"Cube of {number} is {cube(number)}"
            elif function_name == "countdigits": 
                result = f"{number} has {count_digits(number)} digits"
            log_activity(session['username'], function_name, f"Input: {number}, Result: {result}")
        except Exception as e:
            result = f"❌ Error: {str(e)}"
    return render_template_string(check_template, function_name=function_name, result=result)

@app.route("/logout")
def logout():
    if 'username' in session and 'login_time' in session:
        duration = datetime.datetime.now().timestamp() - session['login_time']
        minutes = round(duration / 60, 2)
        log_activity(session['username'], "Logout", f"Stayed {minutes} minutes")
    session.clear()
    return redirect(url_for('index'))

@app.route("/track_exit", methods=["POST"])
def track_exit():
    if 'username' in session and 'login_time' in session:
        duration = datetime.datetime.now().timestamp() - session['login_time']
        minutes = round(duration / 60, 2)
        log_activity(session['username'], "Exit", f"Closed browser after {minutes} minutes")
    return ("", 204)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            logs_rows = get_all_logs()  # all logs from DB
            logs_rows.sort(key=lambda x: x[0])  # sort by timestamp

            sessions = []
            current_session = []
            in_session = False

            for timestamp, username, action, details in logs_rows:
                line = f"[{timestamp}] {username} - {action} - {details}"

                if action == "Login":
                    # Start a new session
                    if current_session:
                        sessions.append(current_session)
                    current_session = [line]
                    in_session = True
                elif action in ["Logout", "Exit"]:
                    if in_session:
                        current_session.append(line)
                        sessions.append(current_session)
                        current_session = []
                        in_session = False
                    else:
                        # Exit without Login, treat as single-session
                        sessions.append([line])
                else:
                    # Any other action
                    if not in_session:
                        # Action without login, treat as pseudo-session
                        current_session = [line]
                        in_session = True
                    else:
                        current_session.append(line)

            # Append remaining session if any
            if current_session:
                sessions.append(current_session)

            # Format logs for display
            formatted_logs = ""
            for session_block in sessions:
                for line in session_block:
                    formatted_logs += line + "\n"
                formatted_logs += "\n\n"  # 2 blank lines between sessions

            return render_template_string(logs_template, logs=formatted_logs)
        else:
            error = "❌ Incorrect password"
    return render_template_string(admin_login_template, error=error)


# ---------------- Main ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
