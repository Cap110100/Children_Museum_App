import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server  # For deployment if needed

def inches_to_feet_in(inches):
    """Convert total inches to a (feet, inches) tuple."""
    ft = int(inches // 12)
    inch = int(inches % 12)
    return ft, inch

def feet_in_to_inches(ft, inch):
    """Convert feet and inches to total inches."""
    return (ft * 12) + inch

# App Layout
app.layout = html.Div(
    style={
        # Background gradient using crimson tones
        'background': 'linear-gradient(to bottom, #ffe6e6, #ffcccc, #ff9999, #ff6666)',
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
                        'width': '300px',      # ENLARGED IMAGE WIDTH
                        'height': 'auto',
                        'display': 'block',
                        'margin': '0 auto 10px auto'
                    }
                ),
                html.H1(
                    "Children's Museum of Indianapolis: President's Day Jump Challenge! 🏀",
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
                # Input fields for the child's details
                html.Label("Name (your jumping nickname!):", style={'fontSize': '16px', 'color': 'crimson'}),
                dcc.Input(
                    id='name', 
                    type='text', 
                    placeholder='e.g. JumpingJack',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label("Age (in years):", style={'fontSize': '16px', 'color': 'crimson'}),
                dcc.Input(
                    id='age', 
                    type='number', 
                    placeholder='e.g. 10',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                # Two inputs for the jump in feet and inches
                html.Label("Vertical Jump (feet and inches):", style={'fontSize': '16px', 'color': 'crimson'}),
                html.Div(
                    style={'display': 'flex', 'gap': '10px', 'marginBottom': '10px'},
                    children=[
                        dcc.Input(
                            id='feet', 
                            type='number', 
                            placeholder='feet',
                            style={'width': '100px'}
                        ),
                        dcc.Input(
                            id='inches', 
                            type='number', 
                            placeholder='inches',
                            style={'width': '100px'}
                        ),
                    ]
                ),
                
                html.Button(
                    "Submit Your Jump!", 
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
        
        # Display messages comparing jump height
        html.Div(
            id='message',
            style={
                'padding': '10px',
                'fontSize': '18px',
                'fontWeight': 'bold',
                'color': 'crimson'
            }
        ),
        
        # Bar chart to visualize the jumps
        dcc.Graph(id='jump-graph'),
        
        # Display top 3 jumpers in a creative way
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
        
        # Store to keep track of children data across callbacks
        dcc.Store(id='children-data', data=[])
    ]
)

# Callback to update data, messages, graph, and top 3
@app.callback(
    [
        Output('children-data', 'data'),
        Output('message', 'children'),
        Output('jump-graph', 'figure'),
        Output('top3', 'children')
    ],
    Input('submit', 'n_clicks'),
    [
        State('name', 'value'),
        State('age', 'value'),
        State('feet', 'value'),
        State('inches', 'value'),
        State('children-data', 'data')
    ]
)
def update_children(n_clicks, name, age, feet_val, inch_val, data):
    # If submit hasn't been clicked yet, do nothing
    if not n_clicks:
        return data, "", {}, ""

    # Validate inputs
    if not name or not age or feet_val is None or inch_val is None:
        return data, "Please fill in all the fields to record your jump!", {}, ""
    
    try:
        age = int(age)
        feet_val = float(feet_val)
        inch_val = float(inch_val)
    except ValueError:
        return data, "Age must be an integer, and Feet/Inches must be numeric.", {}, ""
    
    # Convert feet and inches to total inches
    total_inches = feet_in_to_inches(feet_val, inch_val)
    
    # Create new entry and add to data
    new_entry = {"name": name, "age": age, "jump": total_inches}
    data.append(new_entry)
    
    # Generate message
    if len(data) == 1:
        message = f"Welcome {name}! You’re the first jumper! 🥳"
    else:
        # Calculate average jump of previous jumpers (in inches)
        prev_jumps = [child['jump'] for child in data[:-1]]
        avg_jump = sum(prev_jumps) / len(prev_jumps)
        
        if total_inches > avg_jump:
            message = (
                f"Wow, {name}! You jumped {total_inches:.1f} inches, which is higher "
                f"than the average of {avg_jump:.1f} inches!"
            )
        elif total_inches < avg_jump:
            message = (
                f"Keep practicing, {name}! You jumped {total_inches:.1f} inches, "
                f"which is below the average of {avg_jump:.1f} inches."
            )
        else:
            message = (
                f"Awesome, {name}! You matched the average jump exactly at {avg_jump:.1f} inches!"
            )
    
    # Create bar chart
    jumper_names = [child['name'] for child in data]
    jumper_values = [child['jump'] for child in data]
    
    fig = go.Figure(data=[go.Bar(
        x=jumper_names, 
        y=jumper_values, 
        marker_color='crimson'
    )])
    fig.update_layout(
        title="Vertical Jump Scores (inches)",
        xaxis_title="Jumper Name",
        yaxis_title="Jump (inches)",
        template="plotly_white"
    )
    
    # Determine top 3 jumpers
    sorted_data = sorted(data, key=lambda x: x['jump'], reverse=True)
    top_three = sorted_data[:3]
    
    # Build display for top three
    trophy_emojis = ['🥇', '🥈', '🥉']
    top3_display = [
        html.H3(
            "Top 3 Jumpers ✨",
            style={'textAlign': 'center', 'color': 'crimson', 'marginBottom': '10px'}
        )
    ]
    
    for idx, child in enumerate(top_three):
        ft, inch = inches_to_feet_in(child['jump'])
        top3_display.append(
            html.Div(
                f"{trophy_emojis[idx]} {child['name']} jumped {ft} ft {inch} in",
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
