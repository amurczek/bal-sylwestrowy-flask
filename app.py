from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.secret_key = "tajne_haslo"                              # ustawiam sekretne hasło dla sesji admina


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registrations_new.db"  # tworzę obiekt o nazwie db, połączony do flaska i do bazy danych
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False        # wyłączam funkcję śledzenia zmian w SQLAlchemy, bo nie jest potrzebna

db = SQLAlchemy(app)                                        # dopiero teraz podpinamy bazę do aplikacji
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    guests = db.Column(db.Integer)
    confirmed = db.Column(db.Boolean, default=False)

@app.route("/confirm/<int:id>")
def confirm(id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    registration = Registration.query.get_or_404(id)
    registration.confirmed = True
    db.session.commit()

    return redirect(url_for("admin"))

@app.route("/")                                             # jeśli ktoś wejdzie na stronę główną        gdzie?
def home():                                                 # to uruchomi funkcję home                   co się stanie?  
    return render_template("about.html")                     # wyświetla stronę główną

@app.route("/about")                                        # jeśli ktoś wejdzie na stronę /about
def about():                                                # to uruchomi funkcję about  
    return render_template("about.html")                    # wyświetla stronę o nas

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        guests = int(request.form["guests"])

        if guests > 10:
            return "Można zapisać maksymalnie 10 osób na jedno zgłoszenie."

        new_registration = Registration(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            guests=guests
        )

        db.session.add(new_registration)
        db.session.commit()

        return "Dziękujemy za zapis na Bal Sylwestrowy! Twoja rezerwacja została zapisana!"

    return render_template("register.html")

@app.route("/contact")                                      # jeśli ktoś wejdzie na stronę /contact
def contact():                                              # to uruchomi funkcję contact
    return render_template("contact.html")                  # wyświetla stronę kontaktową , co jest w pliku HTML

@app.route("/admin")
def admin():
    registrations = Registration.query.all()                # pobiera wszystkie zapisy z bazy danych
    return render_template("admin.html", registrations=registrations)   # przekazuje listę zapisów do szablonu admin.html

ADMIN_PASSWORD = "admin*!"                                  # ustawiam hasło admina
@app.route("/login", methods=["GET", "POST"])               # jeśli ktoś wejdzie na stronę /login
def login():
    if request.method == "POST":                            # jeśli formularz został wysłany
        password = request.form["password"]                 # pobiera hasło z formularza

        if password == ADMIN_PASSWORD:                      # sprawdza czy hasło jest poprawne
            session["admin"] = True                         # ustawia zmienną sesyjną admin na True
            return redirect(url_for("admin"))               # przekierowuje do strony admin
        else:                       
            return "Wpisz poprawne hasło!"                  # informuje o złym haśle

    return render_template("login.html")                    # Gdy ktoś wejdzie na /login normalnie: pokaż stronę z formularzem logowania

@app.route("/logout")                                       # jeśli ktoś wejdzie na stronę /logout
def logout():
    session.pop("admin", None)                              # usuwa informację: „jestem adminem”
    return redirect(url_for("login"))                       # przekierowuje do strony logowania

@app.route("/delete/<int:id>")                              # jeśli ktoś wejdzie na stronę /delete/id
def delete(id):                                             # to uruchomi funkcję delete z parametrem id
    if not session.get("admin"):                            # sprawdza czy użytkownik jest zalogowany jako admin
        return redirect(url_for("login"))                   # jeśli nie jest, przekierowuje do strony logowania

    registration = Registration.query.get_or_404(id)        # pobiera zapis o podanym id lub zwraca błąd 404, jeśli nie istnieje
    db.session.delete(registration)                         # usuwa zapis z bazy danych
    db.session.commit()                                     # zatwierdza zmiany w bazie danych

    return redirect(url_for("admin"))                       # przekierowuje z powrotem do strony admin

with app.app_context():                                     # tworzy tabele w bazie danych, jeśli jeszcze nie istnieją
    db.create_all()                                         

if __name__ == "__main__":
    app.run(debug=True)

