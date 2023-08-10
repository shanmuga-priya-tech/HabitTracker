import uuid
from flask import Blueprint,current_app,render_template,request,url_for,redirect#importing bluerint instead of flask
import datetime


#replace all app to pages and everywhere in url use habits. both in html and routesfile
pages=Blueprint("habits",__name__,static_folder="static",template_folder="templates")#instead of ap=flask ,pages=blueprint



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


@pages.route("/")
def home():
    date_str=request.args.get("date")#this is the selected date we get from endpoint
    if date_str:
        selected_date=datetime.datetime.fromisoformat(date_str)
    else:
        selected_date=today_at_midnight()

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date})
    ]
 
    return render_template("index.html",
                           habits=habits_on_date,#it is a list of dict of habitid
                           selected_date=selected_date,
                           completions=completions)



@pages.route("/add",methods=["GET","POST"])
def add_habits():
    today=today_at_midnight()

    if request.method == "POST":
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )
 
        return redirect(url_for("habits.home")) #this will redirect to homepage when add btn is clicked
    return render_template("add_habits.html",
                selected_date=today#becoz newhabits r added only on todays date not on selected date 
                           )



@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")#data we get from hidden fields
    date = datetime.datetime.fromisoformat(date_string)
    habit = request.form.get("habitId")
    current_app.db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for("habits.home", date=date_string))