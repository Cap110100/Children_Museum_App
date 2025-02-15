import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server  # For deployment if needed

# App Layout
app.layout = html.Div(
    style={
        # Darkest at top, lightest at bottom
        'background': 'linear-gradient(to bottom, #ff6666, #ff9999, #ffcccc, #ffe6e6)',
        'fontFamily': 'Comic Sans MS',
        'padding': '20px',
        'minHeight': '100vh'  # ensure full-screen height coverage
    },
    children=[
        # Logo + Title Section
        html.Div(
            style={'textAlign': 'center', 'marginBottom': '20px'},
            children=[
                html.Img(
                    src='assets/shhs.png',
                    style={
                        'width': '300px',  # enlarge the SHHS logo
                        'height': 'auto',
                        'display': 'block',
                        'margin': '0 auto 10px auto'
                    }
                ),
                html.H1(
                    "Children's Museum of Indianapolis: President's Day Hand Grip Strength Challenge! 💪",
                    style={'color': 'crimson'}
                )
            ]
        ),
        
        html.Div(
            style={
                'backgroundColor': 'rgba(255,255,255,0.7)',
                'border': '3px dashed crimson',
                'borderRadius': '10px',
                'padding': '15px',
                'margin': '20px auto',
                'width': '50%'
            },
            children=[
                # Input fields for participant details
                html.Label("Name (your strong nickname!):", style={'fontSize': '16px', 'color': 'crimson'}),
                dcc.Input(
                    id='name', 
                    type='text', 
                    placeholder='e.g. IronGrip',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label("Age (in years):", style={'fontSize': '16px', 'color': 'crimson'}),
                dcc.Input(
                    id='age', 
                    type='number', 
                    placeholder='e.g. 10',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label("Hand Grip Strength (lbs):", style={'fontSize': '16px', 'color': 'crimson'}),
                dcc.Input(
                    id='strength', 
                    type='number', 
                    placeholder='e.g. 30',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Button(
                    "Submit Your Strength!", 
                    id='submit', 
                    n_clicks=0, 
                    style={
                        'backgroundColor': 'crimson', 
                        'color': '#FFFFFF', 
                        'border': 'none', 
                        'padding': '10px 20px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold'
                    }
                ),
            ]
        ),
        
        # Display messages comparing grip strength
        html.Div(
            id='message',
            style={
                'padding': '10px',
                'fontSize': '18px',
                'fontWeight': 'bold',
                'color': 'crimson'
            }
        ),
        
        # Bar chart to visualize the grip strengths
        dcc.Graph(id='strength-graph'),
        
        # Display top 3 participants
        html.Div(
            id='top3',
            style={
                'padding': '10px',
                'marginTop': '20px', 
                'border': '3px solid crimson', 
                'borderRadius': '10px', 
                'backgroundColor': 'rgba(255,255,255,0.7)'
            }
        ),
        
        # Store to keep track of participants' data across callbacks
        dcc.Store(id='participants-data', data=[])
    ]
)

# Callback to update data, messages, graph, and top 3
@app.callback(
    [
        Output('participants-data', 'data'),
        Output('message', 'children'),
        Output('strength-graph', 'figure'),
        Output('top3', 'children')
    ],
    Input('submit', 'n_clicks'),
    [
        State('name', 'value'),
        State('age', 'value'),
        State('strength', 'value'),
        State('participants-data', 'data')
    ]
)
def update_participants(n_clicks, name, age, strength_val, data):
    # If submit hasn't been clicked yet, do nothing
    if not n_clicks:
        return data, "", {}, ""

    # Validate inputs
    if not name or not age or strength_val is None:
        return data, "Please fill in all the fields to record your strength!", {}, ""
    
    try:
        age = int(age)
        strength_val = float(strength_val)
    except ValueError:
        return data, "Age must be an integer, and Strength must be numeric.", {}, ""
    
    # Create new entry and add to data
    new_entry = {"name": name, "age": age, "strength": strength_val}
    data.append(new_entry)
    
    # Generate message
    if len(data) == 1:
        message = f"Welcome {name}! You’re the first participant! 🥳"
    else:
        # Calculate average strength of previous participants
        prev_strengths = [p['strength'] for p in data[:-1]]
        avg_strength = sum(prev_strengths) / len(prev_strengths)
        
        if strength_val > avg_strength:
            message = (
                f"Wow, {name}! You posted {strength_val:.1f} lbs, which is higher "
                f"than the average of {avg_strength:.1f} lbs!"
            )
        elif strength_val < avg_strength:
            message = (
                f"Keep practicing, {name}! You posted {strength_val:.1f} lbs, "
                f"which is below the average of {avg_strength:.1f} lbs."
            )
        else:
            message = (
                f"Amazing, {name}! You exactly matched the average at {avg_strength:.1f} lbs!"
            )
    
    # Create bar chart
    participant_names = [p['name'] for p in data]
    participant_strengths = [p['strength'] for p in data]
    
    fig = go.Figure(data=[go.Bar(
        x=participant_names, 
        y=participant_strengths, 
        marker_color='crimson'
    )])
    fig.update_layout(
        title="Hand Grip Strength (lbs)",
        xaxis_title="Participant Name",
        yaxis_title="Strength (lbs)",
        template="plotly_white"
    )
    
    # Determine top 3
    sorted_data = sorted(data, key=lambda x: x['strength'], reverse=True)
    top_three = sorted_data[:3]
    
    # Build display for top three
    trophy_emojis = ['🥇', '🥈', '🥉']
    top3_display = [
        html.H3(
            "Top 3 Grip Strength ✨",
            style={'textAlign': 'center', 'color': 'crimson', 'marginBottom': '10px'}
        )
    ]
    
    for idx, participant in enumerate(top_three):
        strength_lbs = participant['strength']
        top3_display.append(
            html.Div(
                f"{trophy_emojis[idx]} {participant['name']} posted {strength_lbs:.1f} lbs",
                style={
                    'padding': '10px',
                    'margin': '5px',
                    'fontSize': '16px',
                    'backgroundColor': '#ffe6e6',
                    'borderRadius': '5px',
                    'color': '#2d3436'
                }
            )
        )
    
    return data, message, fig, top3_display

if __name__ == '__main__':
    app.run_server(debug=True)
