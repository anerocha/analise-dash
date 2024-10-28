import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc

# Carregar Dados
file_path = 'universal_top_spotify_songs.csv'
spotify_data = pd.read_csv(file_path)

# Limpeza de Dados
spotify_data.drop_duplicates(inplace=True)
spotify_data.dropna(inplace=True)

# Inicializar o aplicativo Dash com o tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

color_palette = ['#e8f5e9', '#c8e6c9', '#a5d6a7', '#81c784', '#66bb6a'] 

# Layout do Dashboard
app.layout = dbc.Container([ 
    dbc.Row([ 
        dbc.Col(html.H1("Análise de Preferências Musicais no Spotify", 
                         className="text-center text-primary mb-4"), width=12)
    ]), 

    dbc.Row([ 
        dbc.Col(html.P(""" 
            Este dashboard analisa dados de músicas populares do Spotify para identificar padrões de preferência musical.
            Ele mostra os artistas mais populares, a distribuição de popularidade e sugere músicas baseadas nas 
            características de popularidade, energia e dançabilidade.
        """, className="text-center mb-4"), width=12)
    ]), 

    dbc.Row([ 
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Top 10 Artistas Mais Populares"),
            dbc.CardBody(dcc.Graph(id='top-artists'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=6), 

        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Top 10 Álbuns Mais Populares"), 
            dbc.CardBody(dcc.Graph(id='top-albums'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=6), 
    ], className="mb-4"), 

    dbc.Row([ 
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Distribuição da Popularidade das Músicas"), 
            dbc.CardBody(dcc.Graph(id='popularity-distribution'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=12), 
    ], className="mb-4"), 

    dbc.Row([ 
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Popularidade vs Dançabilidade"), 
            dbc.CardBody(dcc.Graph(id='popularity-vs-danceability'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=6), 

        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Popularidade vs Energia"), 
            dbc.CardBody(dcc.Graph(id='popularity-vs-energy'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=6), 
    ], className="mb-4"), 

    dbc.Row([ 
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Recomendações de Músicas Baseadas nas Preferências"), 
            dbc.CardBody(html.Div(id='recommended-songs'), style={"padding": "10px"}), 
        ], className="shadow-sm"), width=12), 
    ]), 

    # Botão para atualizar gráficos
    dbc.Row([ 
        dbc.Col(dbc.Button("Atualizar Gráficos", id='update-button', n_clicks=0, color="primary", className="mt-3")) 
    ], className="text-center") 
], fluid=True) 

# Callback para gerar gráficos
@app.callback( 
    [dash.dependencies.Output('top-artists', 'figure'), 
     dash.dependencies.Output('top-albums', 'figure'), 
     dash.dependencies.Output('popularity-distribution', 'figure'), 
     dash.dependencies.Output('popularity-vs-danceability', 'figure'), 
     dash.dependencies.Output('popularity-vs-energy', 'figure'), 
     dash.dependencies.Output('recommended-songs', 'children')], 
    [dash.dependencies.Input('update-button', 'n_clicks')] 
) 
def update_graphs(n_clicks): 
    # Top 10 Artistas
    top_artists = spotify_data['artists'].value_counts().head(10) 
    fig_artists = px.bar(top_artists, x=top_artists.values, y=top_artists.index, 
                         labels={'x': 'Número de Ocorrências', 'y': 'Artista'}, 
                         title='Top 10 Artistas Mais Frequentes', 
                         color=top_artists.values,  
                         color_continuous_scale=color_palette)  
    fig_artists.update_layout(template="plotly_white") 

    # Top 10 Álbuns
    top_albums = spotify_data['album_name'].value_counts().head(10) 
    fig_albums = px.bar(top_albums, x=top_albums.values, y=top_albums.index, 
                        labels={'x': 'Número de Ocorrências', 'y': 'Álbum'}, 
                        title='Top 10 Álbuns Mais Populares', 
                        color=top_albums.values,  
                        color_continuous_scale=color_palette)  
    fig_albums.update_layout(template="plotly_white") 

    # Distribuição da Popularidade
    fig_popularity = px.histogram(spotify_data, x='popularity', nbins=30, title='Distribuição da Popularidade',
                                  color_discrete_sequence=color_palette)  
    fig_popularity.update_layout(template="plotly_white") 

    # Popularidade vs Dançabilidade
    fig_danceability = px.scatter(spotify_data, x='danceability', y='popularity', 
                                  title='Popularidade vs Dançabilidade', 
                                  color='danceability', 
                                  color_continuous_scale=color_palette)  
    fig_danceability.update_layout(template="plotly_white") 

    # Popularidade vs Energia
    fig_energy = px.scatter(spotify_data, x='energy', y='popularity', 
                            title='Popularidade vs Energia', 
                            color='energy', 
                            color_continuous_scale=color_palette)  
    fig_energy.update_layout(template="plotly_white") 

    # Recomendação de Músicas
    popularity_threshold = spotify_data['popularity'].quantile(0.75) 
    energy_threshold = spotify_data['energy'].quantile(0.75) 
    danceability_threshold = spotify_data['danceability'].quantile(0.75) 

    recommended_songs = spotify_data[ 
        (spotify_data['popularity'] >= popularity_threshold) & 
        (spotify_data['energy'] >= energy_threshold) & 
        (spotify_data['danceability'] >= danceability_threshold) 
    ][['name', 'artists', 'popularity', 'energy', 'danceability']].drop_duplicates() 

    recommended_list = recommended_songs.head(10).to_dict('records') 
    recommended_html = html.Table([ 
        html.Thead(html.Tr([html.Th(col) for col in recommended_songs.columns])), 
        html.Tbody([ 
            html.Tr([html.Td(song[col]) for col in recommended_songs.columns]) for song in recommended_list 
        ]) 
    ], className="table table-striped table-hover table-responsive") 

    return fig_artists, fig_albums, fig_popularity, fig_danceability, fig_energy, recommended_html 

# Executar o aplicativo
if __name__ == '__main__': 
    app.run_server(debug=False)
