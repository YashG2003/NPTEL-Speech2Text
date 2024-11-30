import json
import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import re

# Function to read JSONL data into a DataFrame
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return pd.DataFrame(data)

# Function to calculate the required statistics
def calculate_statistics(df):
    # Total hours
    total_hours = df['duration'].sum() / 3600    # Convert seconds to hours
    
    # Total utterances
    total_utterances = len(df)
    
    # Vocabulary size (unique words across all utterances)
    vocabulary = set()
    for text in df['text']:
        words = text.split()
        vocabulary.update(words)
    vocabulary_size = len(vocabulary)
    
    # Alphabet size (unique characters across all utterances)
    alphabet = set()
    for text in df['text']:
        alphabet.update(set(re.sub(r'[^a-zA-Z ]', '', text).lower()))  # Extract letters and space only
    alphabet_size = len(alphabet)

    return total_hours, total_utterances, vocabulary_size, alphabet_size, alphabet

# Function to plot histograms
def plot_histograms(df):
    # Duration per file
    duration_hist = px.histogram(df, x='duration', nbins=20, title="Duration per File (sec)", color_discrete_sequence=["#4CAF50"])
    
    # Number of words per file
    df['num_words'] = df['text'].apply(lambda x: len(x.split()))
    words_hist = px.histogram(df, x='num_words', nbins=20, title="Number of Words per File", color_discrete_sequence=["#2196F3"])
    
    # Number of characters per file
    df['num_chars'] = df['text'].apply(lambda x: len(x))
    chars_hist = px.histogram(df, x='num_chars', nbins=20, title="Number of Characters per File", color_discrete_sequence=["#FF9800"])
    
    return duration_hist, words_hist, chars_hist

# Function to create the Dash app
def create_dashboard(df, total_hours, total_utterances, vocabulary_size, alphabet_size, duration_hist, words_hist, chars_hist, alphabet):
    app = dash.Dash(__name__)
    
    # Dashboard layout 
    app.layout = html.Div([
        html.H1("Speech Data Dashboard", style={'textAlign': 'center', 'color': '#3F51B5', 'fontFamily': 'Arial, sans-serif'}),
        
        # Statistics Section
        html.Div([
            html.Div([
                html.H3("Total number of hours", style={'color': '#4CAF50'}),
                html.P(f"{total_hours:.2f} hours", style={'fontSize': '24px', 'fontWeight': 'bold'})
            ], className="stat-card"),
            html.Div([
                html.H3("Total number of utterances", style={'color': '#2196F3'}),
                html.P(f"{total_utterances}", style={'fontSize': '24px', 'fontWeight': 'bold'})
            ], className="stat-card"),
            html.Div([
                html.H3("Vocabulary Size", style={'color': '#FF9800'}),
                html.P(f"{vocabulary_size} words", style={'fontSize': '24px', 'fontWeight': 'bold'})
            ], className="stat-card"),
            html.Div([
                html.H3("Alphabet Size", style={'color': '#E91E63'}),
                html.P(f"{alphabet_size} chars", style={'fontSize': '24px', 'fontWeight': 'bold'})
            ], className="stat-card"),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'marginBottom': '30px'}),

        # Alphabet Section
        html.Div([
            html.H2("Complete Alphabet", style={'textAlign': 'center', 'color': '#3F51B5'}),
            html.P(f"Alphabet: {', '.join(sorted(list(alphabet)))}", style={'fontSize': '18px', 'color': '#757575', 'textAlign': 'center'})
        ], style={'marginBottom': '40px'}),
        
        # Histograms Section
        html.Div([
            dcc.Graph(figure=duration_hist),
            dcc.Graph(figure=words_hist),
            dcc.Graph(figure=chars_hist)
        ], style={'marginTop': '20px'})
    ], style={'backgroundColor': '#FAFAFA', 'padding': '20px'})
    
    return app

# Main function to execute the entire process
def main(file_path):
    # Step 1: Read the data from the JSONL file
    df = read_jsonl(file_path)
    
    # Step 2: Calculate the statistics
    total_hours, total_utterances, vocabulary_size, alphabet_size, alphabet = calculate_statistics(df)
    
    # Step 3: Plot the histograms
    duration_hist, words_hist, chars_hist = plot_histograms(df)
    
    # Step 4: Create the Dash dashboard
    app = create_dashboard(df, total_hours, total_utterances, vocabulary_size, alphabet_size, duration_hist, words_hist, chars_hist, alphabet)
    
    # Step 5: Run the app
    app.run_server(debug=True)

# Run the code with your JSONL file path
if __name__ == "__main__":
    file_path = "./train_manifest.jsonl"  
    main(file_path)

