from flask import Flask, render_template, redirect, request, session, url_for, flash
import pymysql
import os

app = Flask(__name__)
app.secret_key = "kkk"
app.config['uploads'] = 'static/images'

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Kivykali1802',
    database='citeverse_db',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

@app.route("/")
def landing_page():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites")
    sites = cursor.fetchall()
    return render_template("landing.html", sites=sites)

@app.route("/admin")
def admin_login():
    return render_template("login.html")

@app.route("/dashboard")
def admin_dashboard():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_accounts WHERE admin_id=%s", (int(session["admin_id"]),))
    account = cursor.fetchone()
    cursor.execute("SELECT * FROM sites")
    sites = cursor.fetchall()
    if "username" in session:
        return render_template("/dashboard.html", account=account, sites=sites)
    else:
        return redirect(url_for("admin_login"))

@app.route("/add_admin_process", methods=['POST'])
def add_admin_process():
    cursor = conn.cursor()
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    username = request.form["userfield"]
    password = request.form["passfield"]
    profile_pic = request.files["profile_pic"]  # use request.files for uploaded file

    # check if a file was uploaded
    if profile_pic and profile_pic.filename != "":
        # save to static/uploads/
        filename = profile_pic.filename
        upload_path = os.path.join("static", "uploads", filename)
        profile_pic.save(upload_path)
        
        # store the relative path in the database
        profile_path = f"static/uploads/{filename}"
    else:
        # if no file uploaded, use a default image
        profile_path = "static/images/default.jpg"

    # ✅ fixed SQL syntax and parameters
    sql = """
        INSERT INTO admin_accounts (firstname, lastname, admin_username, admin_password, profile_pic)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (firstname, lastname, username, password, profile_path))
    conn.commit()

    flash("Admin account added successfully!", "success")
    return redirect("/dashboard")

@app.route("/add_site_process", methods=['POST'])
def add_site_process():
    cursor = conn.cursor()
    sitename = request.form["site_name"]
    sitelink = request.form["site_link"]
    description = request.form["description"]
    image = request.files["image"]  # use request.files for uploaded file

    # check if a file was uploaded
    if image and image.filename != "":
        # save to static/uploads/
        filename = image.filename
        upload_path = os.path.join("static", "uploads", filename)
        image.save(upload_path)
        
        # store the relative path in the database
        profile_path = f"static/uploads/{filename}"
    else:
        # if no file uploaded, use a default image
        profile_path = "static/images/default.jpg"

    # ✅ fixed SQL syntax and parameters
    sql = """
        INSERT INTO sites (site_name, site_link, description, image)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (sitename, sitelink, description, profile_path))
    conn.commit()

    flash(f"{sitename} added successfully!", "success")
    return redirect("/dashboard")

@app.route("/login_process", methods=['POST'])
def login_process():
    username = request.form["userfield"]
    password = request.form["passfield"]

    cursor.execute("SELECT * FROM admin_accounts WHERE admin_username=%s AND admin_password=%s", (username, password))
    account_found = cursor.fetchone()

    if account_found:
        session["username"] = username
        session["admin_id"] = account_found['admin_id']
       
        return redirect("/dashboard")
    else:
        return redirect("/admin")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin_login"))

    

if __name__ == "__main__":
    app.run(debug=True)