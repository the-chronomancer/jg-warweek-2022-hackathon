import json
from apig_wsgi import make_lambda_handler
from flask import Flask, Response, request
import psycopg2

from datetime import date, timedelta

app = Flask(__name__)

DBUSER = ""
DBPASS = ""
DBHOST = ""
DBNAME = ""
USER_ID = ""

CONVERSION=124

conn = psycopg2.connect(f"dbname='{DBNAME}' user='{DBUSER}' host='{DBHOST}' password='{DBPASS}'")

def json_response(body, status=200):
  return Response(json.dumps(body), mimetype="application/json", status=status)

@app.route("/api/total")
def total():
  cur = conn.cursor()
  cur.execute("""SELECT count(user_id) from climbs""")
  rows = cur.fetchall()
  data = rows[0][0] 

  return json_response({"count": data})

# typical flask route, app.route creates a context for the handler that contains request/response objects
@app.route("/api/personalStats")
def personal_aggs():
  today = date.today()

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where user_id='{}' and climb_date='{}'".format(USER_ID, today))
  rows = cur.fetchall()
  day = rows[0][0]

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where user_id='{}' and climb_date>'{}' and climb_date<='{}'".format(USER_ID, today - timedelta(days=7), today))
  rows = cur.fetchall()
  week = rows[0][0] 

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where user_id='{}' and climb_date>'{}' and climb_date<='{}'".format(USER_ID, today - timedelta(days=30), today))
  rows = cur.fetchall()
  month = rows[0][0] 

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where user_id='{}' and climb_date>'{}' and climb_date<='{}'".format(USER_ID, today - timedelta(days=90), today))
  rows = cur.fetchall()
  qtr = rows[0][0] 

  return json_response({
    "day": day,
    "week": week,
    "month": month,
    "quarter": qtr,
    "conversion": CONVERSION
  })

@app.route("/api/jgStats")
def jg_aggs():
  today = date.today()

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where climb_date='{}'".format(today))
  rows = cur.fetchall()
  day = rows[0][0]

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where climb_date>'{}' and climb_date<='{}'".format(today - timedelta(days=7), today))
  rows = cur.fetchall()
  week = rows[0][0] 

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where climb_date>'{}' and climb_date<='{}'".format(today - timedelta(days=30), today))
  rows = cur.fetchall()
  month = rows[0][0] 

  cur = conn.cursor()
  cur.execute("SELECT count(user_id) from climbs where climb_date>'{}' and climb_date<='{}'".format(today - timedelta(days=90), today))
  rows = cur.fetchall()
  qtr = rows[0][0] 

  return json_response({
    "day": day,
    "week": week,
    "month": month,
    "quarter": qtr,
    "conversion": CONVERSION
  })

@app.route("/api/personalBests")
def personal_bests():
  bestdayever = { "count": "27", "time": "8/12/2021" }
  bestweekever = { "count": "158", "time": "Week of 1/7/2021" }
  bestmonthever = { "count": "283", "time": "Jan 2021" }
  bestquarterever = { "count": "459", "time": "Q1 2021" }

  return json_response({
    "day": bestdayever,
    "week": bestweekever,
    "month": bestmonthever,
    "quarter": bestquarterever,
  })

@app.route("/api/myHistorical", methods=["GET"])
def personal_historical():
  today = date.today()

  cur = conn.cursor()
  cur.execute("SELECT climb_date, COUNT(user_id) from climbs where user_id='{}' and climb_date>'{}' and climb_date<='{}' GROUP BY climb_date".format(USER_ID, today - timedelta(days=7), today))
  rows = cur.fetchall()
  daily = []
  for row in rows:
    daily.append({"label": row[0], "count": row[1]})
    print( row)

  print(request.args)
  rng = request.args.get("range")
  groupBy = request.args.get("groupby")
  
  if not rng or not groupBy:
    msg = "must supply range and groupby parameters to /mystats/historical"
    print("msg")
    return Response(msg, status=401)

  result = {
    "day": daily,
    "week": [
      {"label":"Week of 02-11", "count":"0"}, 
      {"label":"Week of 02-18", "count":"2"}, 
      {"label":"Week of 02-25", "count":"7"}, 
      {"label":"Week of 03-04", "count":"30"}, 
    ],
    "month": [
      {"label":"Oct 2021", "count":"22"}, 
      {"label":"Nov 2021", "count":"9"}, 
      {"label":"Dec 2021", "count":"12"}, 
      {"label":"Jan 2022", "count":"3"}, 
      {"label":"Feb 2022", "count":"24"}, 
      {"label":"Mar 2022", "count":"10"}, 
    ],
    "quarter": [
      {"label":"Q2 2021", "count":"52"}, 
      {"label":"Q3 2021", "count":"78"}, 
      {"label":"Q4 2021", "count":"43"}, 
      {"label":"Q1 2022", "count":"37"}, 
    ]
  }[groupBy]

  return json_response({"stats":result, "conversion": CONVERSION})

@app.route("/api/jgHistorical", methods=["GET"])
def jg_historical():
  today = date.today()

  cur = conn.cursor()
  cur.execute("SELECT climb_date, COUNT(user_id) from climbs where climb_date>'{}' and climb_date<='{}' GROUP BY climb_date".format(today - timedelta(days=7), today))
  rows = cur.fetchall()
  daily = []
  for row in rows:
    daily.append({"label": row[0], "count": row[1]})
    print( row)

  print(request.args)
  rng = request.args.get("range")
  groupBy = request.args.get("groupby")
  
  if not rng or not groupBy:
    msg = "must supply range and groupby parameters to /mystats/historical"
    print("msg")
    return Response(msg, status=401)

  result = {
    "day": daily,
    "week": [
      {"label":"Week of 02-11", "count":"9"}, 
      {"label":"Week of 02-18", "count":"25"}, 
      {"label":"Week of 02-25", "count":"7"}, 
      {"label":"Week of 03-04", "count":"13"}, 
    ],
    "month": [
      {"label":"Oct 2021", "count":"52"}, 
      {"label":"Nov 2021", "count":"73"}, 
      {"label":"Dec 2021", "count":"94"}, 
      {"label":"Jan 2022", "count":"192"}, 
      {"label":"Feb 2022", "count":"128"}, 
      {"label":"Mar 2022", "count":"86"}, 
    ],
    "quarter": [
      {"label":"Q2 2021", "count":"1134"}, 
      {"label":"Q3 2021", "count":"1525"}, 
      {"label":"Q4 2021", "count":"2319"}, 
      {"label":"Q1 2022", "count":"1776"}, 
    ]
  }[groupBy]

  return json_response({"stats":result, "conversion": CONVERSION})

lambda_handler = make_lambda_handler(app)
