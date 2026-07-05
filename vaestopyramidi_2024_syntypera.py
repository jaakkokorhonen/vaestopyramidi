from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import json

data_path = Path('output/vaestopyramidi_2024_syntypera_data.csv')
out_path = Path('output/vaestopyramidi_2024_syntypera_recreated.png')
meta_path = Path('output/vaestopyramidi_2024_syntypera_recreated.png.meta.json')

df = pd.read_csv(data_path)
age_order = df[['age','age_label']].drop_duplicates().sort_values('age')
age_labels = age_order['age_label'].tolist()

colors = {
    'naimaton': '#1a3a6b',
    'naimisissa': '#5b9bd5',
    'eronnut': '#c0392b',
    'leski': '#d4841a',
}
colors_i = {
    'naimaton': '#6fa3d8',
    'naimisissa': '#aed6f5',
    'eronnut': '#e89b8a',
    'leski': '#f0c87a',
}
labels = {'naimaton':'Naimaton','naimisissa':'Naimisissa','eronnut':'Eronnut','leski':'Leski'}
cats = ['naimaton','naimisissa','eronnut','leski']

fig = go.Figure()

for sex, sign, showlegend in [('male', -1, True), ('female', 1, False)]:
    for background, palette, pattern_shape, suffix in [
        ('native', colors, '', ''),
        ('immigrant_background', colors_i, '/', ' (ulkom.tausta)')
    ]:
        for cat in cats:
            sub = df[(df.sex == sex) & (df.background == background) & (df.marital_status == cat)].sort_values('age')
            x = (sub['population_thousands'] * sign).tolist()
            fig.add_trace(go.Bar(
                y=sub['age_label'].tolist(),
                x=x,
                name=labels[cat] + suffix,
                orientation='h',
                marker=dict(
                    color=palette[cat],
                    pattern=dict(shape=pattern_shape, size=4, solidity=0.4),
                    line=dict(width=0)
                ),
                legendgroup=f'{cat}_{background}',
                showlegend=showlegend,
                hovertemplate=f'Ikä %{{y}}, {"Mies" if sex=="male" else "Nainen"}, {labels[cat]}{suffix}: %{{customdata:.2f}}k<extra></extra>',
                customdata=sub['population_thousands'].tolist(),
            ))

fig.update_layout(
    barmode='relative',
    bargap=0.04,
    title=dict(
        text='Väestö iän, sukupuolen ja siviilisäädyn mukaan 31.12.2024',
        font=dict(size=17, color='#1a1a1a', family='Arial'),
        x=0.5, xanchor='center'
    ),
    xaxis=dict(
        tickvals=[-35,-25,-15,-5,0,5,15,25,35],
        ticktext=['35k','25k','15k','5k','0','5k','15k','25k','35k'],
        title_text='← Miehet                    Naiset →',
        title_font=dict(size=12),
        zeroline=True, zerolinecolor='#111', zerolinewidth=1.8,
        range=[-43, 43], tickfont=dict(size=10),
        gridcolor='#e0e0e0', gridwidth=0.5,
    ),
    yaxis=dict(
        title_text='Ikä',
        tickmode='array',
        tickvals=[str(a) for a in range(0, 96, 5)] + ['95+'],
        ticktext=[str(a) for a in range(0, 96, 5)] + ['95+'],
        tickfont=dict(size=9),
        title_font=dict(size=12),
    ),
    legend=dict(
        orientation='h',
        yanchor='bottom', y=1.01,
        xanchor='center', x=0.5,
        font=dict(size=10),
        tracegroupgap=5,
        itemwidth=40,
    ),
    annotations=[
        dict(x=-22, y=98, xref='x', yref='y', text='<b>MIEHET</b>', showarrow=False, font=dict(size=13, color='#333')),
        dict(x=22, y=98, xref='x', yref='y', text='<b>NAISET</b>', showarrow=False, font=dict(size=13, color='#333')),
        dict(x=0, y=-5, xref='x', yref='y', text='<i>Raidoitus = ulkomaalaistaustaiset | Tasainen = kantaväestö</i>', showarrow=False, font=dict(size=10, color='#666'), xanchor='center'),
    ],
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=1150,
    width=1080,
    margin=dict(t=140, b=80, l=65, r=35),
)

fig.write_image(out_path, scale=2)
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump({
        'caption': 'Suomen väestöpyramidi 2024 – syntyperä erotettuna',
        'description': 'Väestöpyramidi 31.12.2024. Tasainen väri = kantaväestö, raidoitettu = ulkomaalaistaustaiset.'
    }, f, ensure_ascii=False)
