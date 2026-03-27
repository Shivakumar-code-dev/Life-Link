from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import firestore
from firebase_config import db, DONORS_COLLECTION, REQUESTS_COLLECTION, HISTORY_COLLECTION, ADMINS_COLLECTION
from datetime import datetime
import functools
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "blood-donation-secret-key-change-in-production")

# ─────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────

def donor_login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "donor_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("donor_login"))
        return f(*args, **kwargs)
    return decorated


def admin_login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            flash("Admin access required.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────

@app.route("/")
def index():
    # Gather quick statistics for the landing page
    try:
        total_donors   = len(db.collection(DONORS_COLLECTION).where("status", "==", "approved").get())
        total_requests = len(db.collection(REQUESTS_COLLECTION).get())
        cities_snap    = db.collection(DONORS_COLLECTION).where("status", "==", "approved").get()
        cities         = len(set(d.to_dict().get("city", "") for d in cities_snap))
    except Exception:
        total_donors = total_requests = cities = 0

    return render_template(
        "index.html",
        total_donors=total_donors,
        total_requests=total_requests,
        cities=cities,
    )


# ─────────────────────────────────────────────
# DONOR REGISTRATION
# ─────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def donor_register():
    if request.method == "POST":
        data = request.form

        # Check if email already exists
        existing = db.collection(DONORS_COLLECTION).where("email", "==", data["email"]).get()
        if existing:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("donor_register"))

        donor = {
            "name":               data["name"],
            "email":              data["email"],
            "phone":              data["phone"],
            "blood_group":        data["blood_group"],
            "city":               data["city"].strip().title(),
            "address":            data["address"],
            "age":                int(data["age"]),
            "last_donation_date": data.get("last_donation_date", ""),
            "password":           generate_password_hash(data["password"]),
            "status":             "pending",
            "registered_at":      datetime.utcnow().isoformat(),
        }

        db.collection(DONORS_COLLECTION).add(donor)
        flash("Registration successful! Please wait for admin approval before logging in.", "success")
        return redirect(url_for("donor_login"))

    return render_template("donor_register.html")


# ─────────────────────────────────────────────
# DONOR LOGIN / LOGOUT
# ─────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def donor_login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]

        donors = db.collection(DONORS_COLLECTION).where("email", "==", email).get()
        if not donors:
            flash("No account found with that email.", "danger")
            return redirect(url_for("donor_login"))

        doc  = donors[0]
        data = doc.to_dict()

        if not check_password_hash(data["password"], password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("donor_login"))

        if data["status"] == "pending":
            flash("Your account is pending admin approval.", "warning")
            return redirect(url_for("donor_login"))

        if data["status"] == "rejected":
            flash("Your account has been rejected. Please contact admin.", "danger")
            return redirect(url_for("donor_login"))

        session["donor_id"]   = doc.id
        session["donor_name"] = data["name"]
        return redirect(url_for("donor_dashboard"))

    return render_template("donor_login.html")


@app.route("/logout")
def donor_logout():
    session.pop("donor_id", None)
    session.pop("donor_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ─────────────────────────────────────────────
# DONOR DASHBOARD
# ─────────────────────────────────────────────

@app.route("/dashboard")
@donor_login_required
def donor_dashboard():
    doc  = db.collection(DONORS_COLLECTION).document(session["donor_id"]).get()
    donor = doc.to_dict()
    donor["id"] = doc.id

    # Fetch emergency requests in the same city
    city = donor.get("city", "")
    blood_group = donor.get("blood_group", "")
    requests_snap = (
        db.collection(REQUESTS_COLLECTION)
        .where("city", "==", city)
        .order_by("requested_at", direction=firestore.Query.DESCENDING)
        .limit(10)
        .get()
    )
    nearby_requests = [{"id": r.id, **r.to_dict()} for r in requests_snap]

    # Donation history
    history_snap = (
        db.collection(HISTORY_COLLECTION)
        .where("donor_id", "==", session["donor_id"])
        .order_by("donated_at", direction=firestore.Query.DESCENDING)
        .get()
    )
    history = [{"id": h.id, **h.to_dict()} for h in history_snap]

    return render_template(
        "donor_dashboard.html",
        donor=donor,
        nearby_requests=nearby_requests,
        history=history,
    )


@app.route("/dashboard/update", methods=["POST"])
@donor_login_required
def donor_update():
    data = request.form
    update_data = {
        "name":               data["name"],
        "phone":              data["phone"],
        "city":               data["city"].strip().title(),
        "address":            data["address"],
        "last_donation_date": data["last_donation_date"],
    }
    db.collection(DONORS_COLLECTION).document(session["donor_id"]).update(update_data)

    # Log donation if date updated
    if data["last_donation_date"]:
        db.collection(HISTORY_COLLECTION).add({
            "donor_id":    session["donor_id"],
            "donor_name":  session["donor_name"],
            "donated_at":  data["last_donation_date"],
            "logged_at":   datetime.utcnow().isoformat(),
        })

    flash("Profile updated successfully.", "success")
    return redirect(url_for("donor_dashboard"))


# ─────────────────────────────────────────────
# SEARCH DONORS
# ─────────────────────────────────────────────

@app.route("/search", methods=["GET", "POST"])
def search_donor():
    results = []
    blood_group = request.args.get("blood_group", "")
    city        = request.args.get("city", "").strip().title()

    if blood_group or city:
        query = db.collection(DONORS_COLLECTION).where("status", "==", "approved")
        if blood_group:
            query = query.where("blood_group", "==", blood_group)
        donors = query.get()

        for d in donors:
            data = d.to_dict()
            if city and data.get("city", "").lower() != city.lower():
                continue
            results.append({
                "id":         d.id,
                "name":       data.get("name"),
                "blood_group":data.get("blood_group"),
                "city":       data.get("city"),
                "phone":      data.get("phone"),
            })

    return render_template(
        "search_donor.html",
        results=results,
        blood_group=blood_group,
        city=city,
    )


# ─────────────────────────────────────────────
# EMERGENCY BLOOD REQUEST
# ─────────────────────────────────────────────

@app.route("/request-blood", methods=["GET", "POST"])
def request_blood():
    if request.method == "POST":
        data = request.form
        blood_request = {
            "patient_name":   data["patient_name"],
            "hospital_name":  data["hospital_name"],
            "blood_group":    data["blood_group"],
            "city":           data["city"].strip().title(),
            "contact_number": data["contact_number"],
            "urgency_level":  data["urgency_level"],
            "status":         "open",
            "requested_at":   datetime.utcnow().isoformat(),
        }
        db.collection(REQUESTS_COLLECTION).add(blood_request)
        flash("Emergency blood request submitted! Nearby donors have been notified.", "success")
        return redirect(url_for("request_blood"))

    return render_template("request_blood.html")


# ─────────────────────────────────────────────
# ADMIN LOGIN / LOGOUT
# ─────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]

        admins = db.collection(ADMINS_COLLECTION).where("email", "==", email).get()
        if not admins:
            flash("Admin account not found.", "danger")
            return redirect(url_for("admin_login"))

        doc  = admins[0]
        data = doc.to_dict()

        if not check_password_hash(data["password"], password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("admin_login"))

        session["admin_id"]   = doc.id
        session["admin_name"] = data.get("name", "Admin")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    return redirect(url_for("admin_login"))


# ─────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────

@app.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    # Pending donors
    pending_snap = db.collection(DONORS_COLLECTION).where("status", "==", "pending").get()
    pending_donors = [{"id": d.id, **d.to_dict()} for d in pending_snap]

    # All donors
    all_snap = db.collection(DONORS_COLLECTION).get()
    all_donors = [{"id": d.id, **d.to_dict()} for d in all_snap]

    # Emergency requests
    req_snap = (
        db.collection(REQUESTS_COLLECTION)
        .order_by("requested_at", direction=firestore.Query.DESCENDING)
        .get()
    )
    blood_requests = [{"id": r.id, **r.to_dict()} for r in req_snap]

    # Statistics
    stats = {
        "total":    len(all_donors),
        "approved": sum(1 for d in all_donors if d.get("status") == "approved"),
        "pending":  len(pending_donors),
        "rejected": sum(1 for d in all_donors if d.get("status") == "rejected"),
        "requests": len(blood_requests),
        "open_requests": sum(1 for r in blood_requests if r.get("status") == "open"),
    }

    return render_template(
        "admin_dashboard.html",
        pending_donors=pending_donors,
        all_donors=all_donors,
        blood_requests=blood_requests,
        stats=stats,
        admin_name=session.get("admin_name"),
    )


@app.route("/admin/donor/<donor_id>/approve")
@admin_login_required
def approve_donor(donor_id):
    db.collection(DONORS_COLLECTION).document(donor_id).update({"status": "approved"})
    flash("Donor approved.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/donor/<donor_id>/reject")
@admin_login_required
def reject_donor(donor_id):
    db.collection(DONORS_COLLECTION).document(donor_id).update({"status": "rejected"})
    flash("Donor rejected.", "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/donor/<donor_id>/delete")
@admin_login_required
def delete_donor(donor_id):
    db.collection(DONORS_COLLECTION).document(donor_id).delete()
    flash("Donor deleted.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/request/<req_id>/close")
@admin_login_required
def close_request(req_id):
    db.collection(REQUESTS_COLLECTION).document(req_id).update({"status": "closed"})
    flash("Request marked as closed.", "success")
    return redirect(url_for("admin_dashboard"))


# ─────────────────────────────────────────────
# ADMIN SETUP (run once to create first admin)
# ─────────────────────────────────────────────

@app.route("/admin/setup", methods=["GET", "POST"])
def admin_setup():
    # Only allow if NO admins exist yet
    existing = db.collection(ADMINS_COLLECTION).get()
    if existing:
        flash("Admin already exists. This route is disabled.", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name     = request.form["name"]
        email    = request.form["email"]
        password = request.form["password"]
        db.collection(ADMINS_COLLECTION).add({
            "name":       name,
            "email":      email,
            "password":   generate_password_hash(password),
            "created_at": datetime.utcnow().isoformat(),
        })
        flash("Admin account created. Please log in.", "success")
        return redirect(url_for("admin_login"))

    return render_template("admin_setup.html")


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
