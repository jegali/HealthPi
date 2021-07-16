#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8080/ in your web browser.

# Import used libraries
import os
import subprocess
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

# Load some external Stylesheets geladen.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                        'https://fonts.googleapis.com/icon?family=Material+Icons',
                        'myStyle.css',
                        dbc.themes.BOOTSTRAP
                        ]

# search all syslog files in /var/syslog/raspberry for health data
# write result to health.txt
# 9 devices, every 10 seconds, logdata for an hour = 9*6*60 = 3240
# so 4000 should be sufficient to get a good overwview
# do not take all records - acquiring the data by os takes so long, that the file is not written
# thus leading to empty health.txt thus leading to crash
#os.system('grep -h CPU /var/log/syslog* | sort | tail -3000 > health.txt')
logprocess = subprocess.Popen("grep -h CPU /var/log/raspberry/* | sort | tail -4000 > health.txt", shell=True)
logprocess.wait()

# open health.txt and use the accumulated data
log_data = open('health.txt','r')

health_list=[]

# parse health.txt ...
for line in log_data:
    spalten = line.split('|')
    dateDev = spalten[0]
    data = spalten[1]
    timestamp = dateDev.split(' ')[0]
    device = dateDev.split(' ')[1]

    cpu_current_temp = data.split(';')[0].split("=")[1]
    cpu_avg_usage_percent = data.split(';')[1].split("=")[1]
    core_usages_percent = data.split(';')[2].split("=")[1]
    number_of_cores = data.split(';')[3].split("=")[1]
    CPU_frequency_min = data.split(';')[4].split("=")[1]
    CPU_frequency_max = data.split(';')[5].split("=")[1]
    CPU_frequency_current = data.split(';')[6].split("=")[1]
    RAM_total_byte = data.split(';')[7].split("=")[1]
    RAM_available_byte = data.split(';')[8].split("=")[1]
    RAM_usage_byte = data.split(';')[9].split("=")[1]
    HDD_total_byte = data.split(';')[10].split("=")[1]
    HDD_used_byte = data.split(';')[11].split("=")[1]
    HDD_free_byte = data.split(';')[12].split("=")[1]

    # remove .fritz.box from device name
    device = device.replace(".fritz.box", "")

    health_list.append(
        [timestamp, device, cpu_current_temp, cpu_avg_usage_percent, core_usages_percent, number_of_cores,
         CPU_frequency_min, CPU_frequency_max, CPU_frequency_current, RAM_total_byte, RAM_available_byte,
         RAM_usage_byte,
         HDD_total_byte, HDD_used_byte, HDD_free_byte])

# and close the file
log_data.close()

# ... and create a pandas DataFrame
df = pd.DataFrame(health_list,
                  columns=['timestamp', 'device', 'CPU_current_temp_C', 'CPU_avg_usage_percent', 'Core_usages_percent',
                           'Number_of_Cores',
                           'CPU_frequency_min', 'CPU_frequency_max', 'CPU_frequency_current', 'RAM_total_byte',
                           'RAM_available_byte', 'RAM_usage_byte',
                           'HDD_total_byte', 'HDD_used_byte', 'HDD_free_byte'])

# sort the dataframe by timestamp... this should be done when GREPping the data
df = df.sort_values(['timestamp'], ascending=True)

# get the latest entry for each device
#latest_entries = df.loc[df.groupby('device').timestamp.idxmax()]
latest_entries = df.sort_values('timestamp').drop_duplicates(['device'], keep='last')

# get the line with aurorafox
aurorafox = latest_entries.loc[latest_entries['device'] == 'aurorafox']

# get a list of different devices
devices = df['device']
devices = devices.unique()
devices.sort()



# create app object and pass the stylesheets to dash
app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

myMenuStyle = {
    'color': '#fff',
    'font-size': '36px',
}

sidebar_isOpen = True

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Span("menu", className="material-icons hamburgerMenu")),
                    dbc.Col(html.Div("piHealth Dashboard", className="navbarBrand")),
                ],
                no_gutters=True,
            ),
            id="navButton",
        ),
        html.A(html.Button('Refresh Data'),href='/'),
        html.Div(id='live-update-text'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        ),
    ],
    color="dark",
    dark=True,
)

sidebar = html.Div(
    [
        dcc.Store(id='side_click'),
        html.P("Configuration", className="sidebar-config"),
        html.Hr(className="sidebar-hr"),
        html.P("Dashboard Style: ", className="lead"),
        dcc.RadioItems(
            options=[
                {'label': 'Overall Health', 'value': 'oah'},
                {'label': 'Single Nodes', 'value': 'cco'},
            ],
            className="label-style",
            value='oah',
            labelStyle={"display": "block", "padding": "10px", "max-width": "200px", "margin": "auto"},
            inputStyle={"margin-right": "8px"},
            id='nodes-toggle',
        ),
        html.Div(
            [
                html.P(
                    "Nodes: ", className="lead"
                ),
                # fill dropdown with device list
                dcc.Dropdown(
                    options=[
                        {'label': i, 'value': i} for i in devices
                    ],
                    value=devices[0],
                    multi=True,
                ),
            ],
            id='nodes-container',
        ),
        html.P(
            "", className="lead"
        ),
        dcc.Checklist (
            options=[
                {'label': 'Use Dark Theme', 'value': ''},
            ],
            className="label-style",
            labelStyle={"display": "block", "padding": "10px", "max-width": "200px", "margin": "auto"},
            inputStyle={"margin-right": "8px"},
        ),
    ],
    className="sidebar-hidden",
    id='sidebar',
)



def generate_device_dash(i, devices):
    actual_device = latest_entries.loc[latest_entries['device'] == devices[i]]
    temperatur=float(actual_device['CPU_current_temp_C'].astype(float))
    ram=(int)(actual_device['RAM_usage_byte'].astype(float) / actual_device['RAM_total_byte'].astype(float) * 100)
    disk=(int)(actual_device['HDD_used_byte'].astype(float) / actual_device['HDD_total_byte'].astype(float) * 100)
    cpu_load = float(actual_device['CPU_avg_usage_percent'].astype(float))

    cores=actual_device['Core_usages_percent'].to_string()
    cores = cores.split("[")[1]
    cores = cores.replace("]","")
    cores = cores.replace(" ","")
    core1=cores.split(",")[0]
    core2=cores.split(",")[1]
    core3=cores.split(",")[2]
    core4=cores.split(",")[3]
		
		    return html.Div([
        dbc.Row(
            html.A(
                dbc.Col(
                    [
                        html.I(className="fab fa-raspberry-pi"),
                        devices[i],
                        html.I(className="fas fa-plus",
                               id=
                               {
                                    'type': 'collapseIndicator',
                                    'index': (i),
                               },
                            ),
                    ],
                    className="dashCollapse",
                    xs=12, sm=12, md=12, lg=12, xl=12
                ),
                id={
                    'type': 'aurora-collapse-button',
                    'index': (i)
                },
            ),
        ),
        dbc.Collapse(
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4('CPU Temp: '+str(temperatur)+'°C'),
                                daq.Gauge(
                                    color={"default": "black", "gradient": True, "ranges": {"green": [0, 40], "yellow":>                                    value=temperatur,
                                    label=' ',
                                    max=100,
                                    min=0,
                                )
                            ],
                            className="myCard",
                        ),
                        className="myCardWrapper",
                        xs=12, sm=6, md=6, lg=3, xl=3
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4('RAM usage: '+str(ram)+'%'),
                                daq.Gauge(
                                    color={"default": "black", "gradient": True,
                                           "ranges": {"green": [0, 40], "yellow": [40, 60], "red": [60, 100]}},
                                    value=ram,
                                    label=' ',
                                    max=100,
                                    min=0,
                                )
                            ],
                            className="myCard",
                        ),
                        className="myCardWrapper",
                        xs=12, sm=6, md=6, lg=3, xl=3
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4('Disk usage: '+str(disk)+'%'),
                                daq.Gauge(
                                    color={"default": "black", "gradient": True,
                                           "ranges": {"green": [0, 40], "yellow": [40, 60], "red": [60, 100]}},
                                    value=disk,
                                    label={'label': ' ', 'style': {'fontSize': 4}},
                                    max=100,
                                    min=0,
                                )
                            ],
                            className="myCard",
                        ),
                        className="myCardWrapper",
                        xs=12, sm=6, md=6, lg=3, xl=3
                    ),
                    dbc.Col(
                        html.Div(
                        [
                            html.H4('CPU load: '+str(cpu_load)+'%'),
                            daq.GraduatedBar(
                                #id='1core-1',
                                min=0, max=100,
                                step=5,
                                value=float(core1),
                                color={"ranges":{"green":[0,40],"yellow":[40,70],"red":[70,100]}},
                                label='Core #1: ' + core1 + "%",
                                size=175,
                            ),
                            daq.GraduatedBar(
                                #id='1core-2',
                                min=0, max=100,
                                step=5,
                                value=float(core2),
                                color={"ranges":{"green":[0,40],"yellow":[40,70],"red":[70,100]}},
                                label='Core #2: ' + core2 + "%",
                                size=175,
                            ),
                            daq.GraduatedBar(
                                #id='1core-3',
                                min=0, max=100,
                                step=5,
                                value=float(core3),
                                color={"ranges":{"green":[0,40],"yellow":[40,70],"red":[70,100]}},
                                label='Core #3: ' + core3 + "%",
                                size=175,
                            ),
                            daq.GraduatedBar(
                                #id='1core-4',
                                min=0, max=100,
                                step=5,
                                value=float(core4),
                                color={"ranges":{"green":[0,40],"yellow":[40,70],"red":[70,100]}},
                                label='Core #4: ' + core4 + "%",
                                size=175,
                            )
                        ], className="myCard",
                        ),
                        className="myCardWrapper",
                        xs=12, sm=6, md=6, lg=3, xl=3
                    ),
                ],

            ),
            id={
                'type': 'aurora-collapse',
                'index': (i),
            },
            className="dashRow",
        ),
    ])

content2 = dbc.Container(
    [
        generate_device_dash(i, devices) for i in range(0,len(devices))
    ],
    fluid=True,
    id='content-id',
    className="content",
)


# Ohne ein Applayout kann die Anwendung nicht gestartet werden
app.layout = html.Div(children=[
    navbar,
    sidebar,
    content2,
])

@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update(n):
    #print("yohoo")
    return


# Der Benutzer klickt auf das Hamburger-Menu Item
# dadurch wird die Sidebar ausgeklappt oder eingeklappt
@app.callback(
    [
        Output(component_id='sidebar', component_property='className'),
        Output(component_id='side_click', component_property='data'),
    ],
    Input(component_id='navButton', component_property='n_clicks'),
    State('side_click', 'data'),
)
def navbarButtonClick(n_clicks, side_click):
    if n_clicks is None:
        raise PreventUpdate
    else:
        if side_click == "SHOW":
            sidebar = "sidebar-hidden"
            current_side_click = "HIDDEN"
        else:
            sidebar = "sidebar-show"
            current_side_click="SHOW"
        return sidebar, current_side_click

# Wenn der Benutzer die Sidebar öffnet, sieht er zwei Radiobuttons,
# wobei der obere für "overall" ausgewählt ist - damit wird die Multibox zu Beginn
# nicht ausgegeben.
@app.callback(
        Output(component_id='nodes-container', component_property='style'),
        Input(component_id='nodes-toggle', component_property='value'),
)
def nodeToggleClick(toggle_value):
    if toggle_value == "oah":
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@app.callback(
    [
         Output({'type': 'aurora-collapse', 'index': MATCH}, component_property="is_open"),
         Output({'type': 'collapseIndicator', 'index': MATCH}, component_property="className"),
    ],
    Input(component_id={'type': 'aurora-collapse-button', 'index': MATCH}, component_property="n_clicks"),
    State(component_id={'type': 'aurora-collapse', 'index': MATCH}, component_property="is_open")
)

def toggle_aurora(n_clicks, is_open):
    if n_clicks:
        if is_open:
            sidebar = "fas fa-plus"
        else:
            sidebar = "fas fa-minus"
        return not is_open, sidebar
    sidebar = "fas fa-plus"
    return is_open, sidebar


# Application entry point
# application is running on port 8080
# call application by http://localhost:8080 aufgerufen werden
if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
		