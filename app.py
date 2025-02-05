from flask import Flask, render_template, request
import psycopg2
import plotly.graph_objs as go
import plotly.utils
import json
import numpy as np
from decimal import Decimal
from config import db_host, db_database, db_userName, db_password, db_port, db_table


app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def display_noko_time():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get unique user names
    cur.execute("SELECT DISTINCT user_name FROM noko_time ORDER BY user_name;")
    user_names = [row[0] for row in cur.fetchall()]
    
    selected_user = request.form.get('user_name', 'All')
    
    graphs = []
    for pillar in sixPillars:
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
        cur.execute(queryCommand)
        
        results = cur.fetchall()
        dates = [row[0] for row in results]
        hours = [float(row[1]) if isinstance(row[1], Decimal) else row[1] for row in results]  # Convert Decimal to float
        
        # Create scatter plot
        trace = go.Scatter(
            x=dates, 
            y=hours, 
            mode='lines+markers', 
            name='Actual Hours',
            line=dict(color='blue'),
            marker=dict(size=8)
        )
        
        # Calculate trend line
        z = np.polyfit(range(len(dates)), hours, 1)
        p = np.poly1d(z)
        trend_line = go.Scatter(
            x=dates,
            y=p(range(len(dates))),
            mode='lines',
            name='Trend Line',
            line=dict(color='red', dash='dash')
        )
        
        layout = go.Layout(
            title=f'{pillar} Hours',
            xaxis={'title': 'Date', 'rangeslider': {'visible': True}, 'rangeselector': {'buttons': [
                {'count': 1, 'label': '1m', 'step': 'month', 'stepmode': 'backward'},
                {'count': 6, 'label': '6m', 'step': 'month', 'stepmode': 'backward'},
                {'count': 1, 'label': '1y', 'step': 'year', 'stepmode': 'backward'},
                {'step': 'all'}
            ]}},
            yaxis={'title': 'Hours'},
            hovermode='closest',
            showlegend=True
        )
        fig = go.Figure(data=[trace, trend_line], layout=layout)
        graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    cur.close()
    conn.close()
    
    return render_template('noko_time.html', graphs=graphs, user_names=user_names, selected_user=selected_user)

if __name__ == '__main__':
    app.run(debug=True)