from flask import Flask, request, redirect, url_for, session, render_template_string
import math, datetime, os

app = Flask(__name__)
app.secret_key = "your_secret_key"

LOG_FILE = "user_activity.log"
ADMIN_PASSWORD = "admin123"


'''
-------if the admin delete all the past stored data-------

with open("user_activity.log", "w", encoding="utf-8") as f:
    f.write("")  # Clears all content
print("User activity log cleared!") '''

# ---------------- Utility ---------------- #
def log_activity(username, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:  # UTF-8 safe
        f.write(f"[{timestamp}] {username} - {action} - {details}\n")

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
  
  <!-- Welcome Header -->
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
    session.clear()  # clear session on landing
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
            logs = ""
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, encoding="utf-8") as f:
                    raw_logs = f.readlines()
                    user_block = ""
                    for line in raw_logs:
                        # Split logout line to compute duration
                        if "Logout" in line:
                            parts = line.strip().split("Stayed")
                            if len(parts) == 2:
                                # Convert minutes to HH:MM:SS
                                minutes = float(parts[1].split()[0])
                                hours = int(minutes // 60)
                                mins = int(minutes % 60)
                                secs = int((minutes - int(minutes)) * 60)
                                time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
                                line = f"{parts[0]}Stayed {time_str} (HH:MM:SS)\n"
                        user_block += line
                        # Add two line breaks after each Logout
                        if "Logout" in line:
                            user_block += "\n\n"
                    logs = user_block
            return render_template_string(logs_template, logs=logs)
        else:
            error = "❌ Incorrect password"
    return render_template_string(admin_login_template, error=error)


# ---------------- Main ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

