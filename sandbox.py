from flask import Flask, render_template, request
import psycopg2
import plotly.graph_objs as go
import plotly.utils
import json
from config import db_host, db_database, db_userName, db_password, db_port, db_table

# app = Flask(__name__)

sixPillars = [
    "1-Maintenance/Operations",
    "2-Service Requests",
    "3-Projects",
    "4-Planning/Optimization/Continuous Improvement",
    "5-Professional Development/Growth",
    "6-Administrative Activities/Overhead"
]

def get_db_connection():
    conn = psycopg2.connect(
        dbname=db_database,
        user=db_userName,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

# @app.route('/', methods=['GET', 'POST'])
def display_noko_time():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get unique user names
    cur.execute("SELECT DISTINCT user_name FROM noko_time ORDER BY user_name;")
    user_names = [row[0] for row in cur.fetchall()]
    
    # selected_user = request.form.get('user_name', 'All')
    selected_user = "Eunice Kong"
    graphs = []
    for pillar in sixPillars:
        print(pillar)
        print(selected_user)
        print (db_table)

        if selected_user != 'All':
            queryCommand = f"""
                SELECT date, SUM(hours) 
                FROM {db_table} 
                WHERE project_name = '{pillar}' AND user_name = '{selected_user}'
                GROUP BY date 
                ORDER BY date;
            """
        else:
            queryCommand =f"""
                SELECT date, SUM(hours) 
                FROM {db_table} 
                WHERE project_name = '{pillar}'
                GROUP BY date 
                ORDER BY date;
            """
        print(queryCommand)
    #     cur.execute(queryCommand)
        
    #     results = cur.fetchall()
    #     dates = [row[0] for row in results]
    #     hours = [row[1] for row in results]
        
    #     trace = go.Scatter(x=dates, y=hours, mode='lines+markers', name=pillar)
    #     layout = go.Layout(title=f'{pillar} Hours', xaxis={'title': 'Date'}, yaxis={'title': 'Hours'})
    #     fig = go.Figure(data=[trace], layout=layout)
    #     graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    # cur.close()
    # conn.close()
    
    # return render_template('noko_time.html', graphs=graphs, user_names=user_names, selected_user=selected_user)

if __name__ == '__main__':
    display_noko_time()