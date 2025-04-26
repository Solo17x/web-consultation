@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        reset_code = request.form.get("reset_code")
        new_password = request.form.get("password")

        if not reset_code or reset_code not in RESET_CODES:
            flash("Invalid reset code.", "danger")
            return redirect(url_for("auth.reset_password"))

        user_id = RESET_CODES.pop(reset_code)["user_id"]
        user = Patient.query.get(user_id) or Doctor.query.get(user_id)

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))

        # ✅ Debugging: Print before update
        print("Before update - Doctor Password Hash:", user.password_hash)

        user.set_password(new_password)  # ✅ Ensure correct hashing
        db.session.add(user)  # ✅ Force SQLAlchemy to detect changes
        db.session.commit()

        # ✅ Debugging: Print after update
        print("After update - Doctor Password Hash:", user.password_hash)

        flash("Password reset successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")



            license_front = save_profile_picture(form.license_front.data) if form.license_front.data else None
            license_back = save_profile_picture(form.license_back.data) if form.license_back.data else None
            board_cert = save_profile_picture(form.board_cert.data) if form.board_cert.data else None
            other_documents = save_profile_picture(form.other_documents.data) if form.other_documents.data else None