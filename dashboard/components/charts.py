"""
AIVONEX – Brand Monitoring System
Dashboard Components: Charts (Fixed)
"""

import plotly.graph_objects as go
import pandas as pd

COLORS = {
    "positive": "#00FF88",
    "negative": "#FC4E6E",
    "neutral":  "#4A5568",
    "green":    "#00FF88",
    "yellow":   "#F6C453",
    "blue":     "#5B9EFF",
}

# Base layout — NO legend key (set per-chart to avoid duplicate kwarg error)
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Sora, Inter, sans-serif", color="#718096", size=11),
    margin=dict(l=16, r=16, t=24, b=16),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        showgrid=True, zeroline=False,
        tickfont=dict(size=10, color="#4A5568"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        showgrid=True, zeroline=False,
        tickfont=dict(size=10, color="#4A5568"),
    ),
)


def sentiment_donut(pos: int, neg: int, neu: int) -> go.Figure:
    total = pos + neg + neu
    fig = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[pos, neg, neu],
        hole=0.68,
        marker=dict(
            colors=[COLORS["positive"], COLORS["negative"], COLORS["neutral"]],
            line=dict(color="#07090F", width=3),
        ),
        textinfo="percent",
        textfont=dict(size=11, color="#EDF2F7"),
        hovertemplate="<b>%{label}</b><br>%{value} mentions<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>Mentions</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color="#EDF2F7"),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Sora, Inter, sans-serif"),
    )
    return fig


def sentiment_timeline(df: pd.DataFrame, brand_name: str = "") -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    daily = df.groupby(["date", "sentiment_label"]).size().reset_index(name="count")

    fill_rgba = {
        "positive": "rgba(0,255,136,0.07)",
        "negative": "rgba(252,78,110,0.07)",
        "neutral":  "rgba(74,85,104,0.07)",
    }

    fig = go.Figure()
    for label in ["positive", "negative", "neutral"]:
        subset = daily[daily["sentiment_label"] == label]
        fig.add_trace(go.Scatter(
            x=subset["date"], y=subset["count"],
            name=label.capitalize(),
            mode="lines+markers",
            line=dict(color=COLORS[label], width=2.5),
            marker=dict(size=5, color=COLORS[label]),
            fill="tozeroy" if label == "positive" else "none",
            fillcolor=fill_rgba[label],
            hovertemplate=f"<b>{label.capitalize()}</b><br>%{{x}}<br>%{{y}} mentions<extra></extra>",
        ))

    # Apply base layout first, then legend separately — avoids duplicate kwarg
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        legend=dict(
            orientation="h", y=-0.18, x=0.5, xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#718096"),
        ),
        hovermode="x unified",
    )
    return fig


def compound_histogram(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    colors = df["vader_compound"].apply(
        lambda v: COLORS["positive"] if v > 0.05
        else (COLORS["negative"] if v < -0.05 else COLORS["neutral"])
    )
    fig = go.Figure(go.Histogram(
        x=df["vader_compound"],
        nbinsx=28,
        marker=dict(color=colors, line=dict(color="#07090F", width=0.5)),
        hovertemplate="Score: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        xaxis_title="VADER Compound Score",
        yaxis_title="Count",
        bargap=0.04,
    )
    return fig


def source_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    src = (df.groupby("source").size()
             .reset_index(name="count")
             .sort_values("count", ascending=True))

    fig = go.Figure(go.Bar(
        x=src["count"], y=src["source"],
        orientation="h",
        marker=dict(color=COLORS["green"], opacity=0.85,
                    line=dict(color="#07090F", width=0.5)),
        text=src["count"], textposition="outside",
        textfont=dict(size=10, color="#718096"),
        hovertemplate="%{y}: <b>%{x}</b> mentions<extra></extra>",
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(xaxis_title="Mentions")
    return fig


def health_gauge(score: float) -> go.Figure:
    color = (COLORS["positive"] if score >= 60
             else (COLORS["yellow"] if score >= 40 else COLORS["negative"]))

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Brand Health", "font": {"size": 12, "color": "#718096"}},
        number={"suffix": "/100", "font": {"size": 30, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#2D3748",
                     "tickfont": {"size": 9, "color": "#4A5568"}},
            "bar":  {"color": color, "thickness": 0.28},
            "bgcolor": "#0D1321",
            "bordercolor": "rgba(255,255,255,0.05)",
            "borderwidth": 1,
            "steps": [
                {"range": [0,  35],  "color": "rgba(252,78,110,0.08)"},
                {"range": [35, 60],  "color": "rgba(246,196,83,0.08)"},
                {"range": [60, 100], "color": "rgba(0,255,136,0.08)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 2},
                "thickness": 0.75, "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sora, sans-serif"),
        margin=dict(l=20, r=20, t=30, b=10),
        height=260,
    )
    return fig


def engagement_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    for label in ["positive", "negative", "neutral"]:
        sub = df[df["sentiment_label"] == label]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["vader_compound"], y=sub["engagement"],
            mode="markers", name=label.capitalize(),
            marker=dict(color=COLORS[label], size=7, opacity=0.75,
                        line=dict(color="#07090F", width=0.5)),
            hovertemplate=f"<b>{label}</b><br>Score: %{{x:.3f}}<br>Engagement: %{{y}}<extra></extra>",
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#718096")),
        xaxis_title="Sentiment Score",
        yaxis_title="Engagement",
    )
    return fig


def sentiment_badge(label: str) -> str:
    cls = {"positive": "badge-pos", "negative": "badge-neg"}.get(label, "badge-neu")
    return f'<span class="{cls}">{label.upper()}</span>'


def format_score(score: float) -> str:
    color = "#00FF88" if score > 0.05 else ("#FC4E6E" if score < -0.05 else "#4A5568")
    return f'<span style="color:{color};font-family:monospace;font-weight:600">{score:+.3f}</span>'