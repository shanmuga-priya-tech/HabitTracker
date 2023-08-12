import uuid
from flask import Blueprint,session,current_app,flash,render_template,request,url_for,redirect#importing blueprint instead of flask
import datetime
from passlib.hash import pbkdf2_sha256



#replace all app to pages and everywhere in url use habits. both in html and routesfile
pages=Blueprint("habits",__name__,static_folder="static",template_folder="templates")#instead of app=flask ,pages=blueprint


    
@pages.route("/",methods=["GET","POST"])
def reg():
    if request.method =="POST":
            email=request.form.get("email")
            password=request.form.get("password")
            hash_pwd= pbkdf2_sha256.hash(password)

            current_app.db.user.insert_one({
                            "email":email,"password":hash_pwd})
            flash("Successfully signed up.")
            return redirect(url_for('habits.log')) 
    return render_template("reg.html")



@pages.route("/login",methods=["GET","POST"])
def log():
        if request.method =="POST":
            email=request.form.get("email")
            password=request.form.get("password")
            
            user=current_app.db.user.find_one({"email":email})
            if user and pbkdf2_sha256.verify(password, user["password"]):
                session["email"] = user["email"]
                return redirect(url_for('habits.home'))
            else:
                flash("Incorrect Email/Password !!!")
                return redirect(url_for('habits.log'))    
        return render_template("log.html")

@pages.route("/logout")
def logout():
   session.clear()
   return redirect(url_for("habits.log")) 
     

#this functn gives 3days before and after selected date.
# to make this functn available to all rendering temp we use contextprocessor.
@pages.context_processor
def calc_date_range():
    def date_range(start: datetime.datetime):
        dates=[start+ datetime.timedelta(days=diff) for diff in range(-3,4)]
        return dates
    return {"date_range":date_range}


def today_at_midnight():
    today = datetime.datetime.today()#it returns date hours mins sec
    return datetime.datetime(today.year, today.month, today.day)#we need only date


@pages.route("/home")
def home():
    date_str=request.args.get("date")#this is the selected date we get from endpoint
    if date_str:
        selected_date=datetime.datetime.fromisoformat(date_str)
    else:
        selected_date=today_at_midnight()

    user_id = session.get("email")

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date},"user_id":user_id})
    completions = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date,"user_id": user_id})
    ]
 
    return render_template("index.html",
                           habits=habits_on_date,#it is a list of dict of habitid
                           selected_date=selected_date,
                           completions=completions)



@pages.route("/add",methods=["GET","POST"])
def add_habits():
    today=today_at_midnight()

    user_id = session.get("email")

    if request.method == "POST":
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex,
              "added": today,
             "name": request.form.get("habit"),
            "user_id": user_id}
        )
        return redirect(url_for("habits.home")) #this will redirect to homepage when add btn is clicked
    return render_template("add_habits.html",
                selected_date=today#becoz newhabits r added only on todays date not on selected date 
                           )

@pages.route("/complete", methods=["POST"])
def complete():
    user_id = session.get("email")

    date_string = request.form.get("date")#data we get from hidden fields
    date = datetime.datetime.fromisoformat(date_string)
    habit = request.form.get("habitId")
    current_app.db.completions.insert_one({"date": date, "habit": habit,"user_id":user_id})

    return redirect(url_for("habits.home", date=date_string))

@pages.route("/delete/<habit_id>",methods=["POST"])
def delete(habit_id):
    current_app.db.habits.delete_one({"_id": habit_id})
    current_app.db.completions.delete_many({"habit": habit_id})
    return redirect(url_for("habits.home"))
