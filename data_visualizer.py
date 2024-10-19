import plotly.graph_objects as go
from typing import List, Dict

def create_engagement_chart(engagement_rate: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = engagement_rate,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Engagement Rate (%)"},
        gauge = {
            'axis': {'range': [None, 10]},
            'steps': [
                {'range': [0, 3], 'color': "lightgray"},
                {'range': [3, 7], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': engagement_rate
            }
        }
    ))
    return fig

def create_posting_schedule_chart(content_plan: List[Dict]) -> go.Figure:
    days = [post['day'] for post in content_plan]
    post_types = [post['post_type'] for post in content_plan]
    posting_times = [post['posting_time'] for post in content_plan]

    fig = go.Figure(data=[go.Table(
        header=dict(values=['Day', 'Post Type', 'Posting Time'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[days, post_types, posting_times],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(width=700, height=400)
    return fig
