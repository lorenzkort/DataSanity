import plotly.graph_objs as go
import networkx as nx
import json


def visualize_data_lineage(json_data):
    # Parse the JSON data
    data = json.loads(json_data) if isinstance(json_data, str) else json_data

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for entities
    for entity in data.get("entities", []):
        qualified_name = entity.get("qualifiedName", f"unknown_{len(G.nodes)}")
        G.add_node(
            qualified_name,
            type=entity.get("type", "unknown"),
            label=entity.get("name", qualified_name),
        )

        for column in entity.get("columns", []):
            column_name = f"{qualified_name}.{column.get('name', 'unknown')}"
            G.add_node(column_name, type="column", label=column.get("name", "unknown"))
            G.add_edge(qualified_name, column_name)

    # Add edges for processes
    for process in data.get("processes", []):
        process_name = process.get("name", "Unknown Process")
        for input_entity in process.get("inputs", []):
            for output_entity in process.get("outputs", []):
                input_name = input_entity.get("uniqueAttributes", {}).get(
                    "qualifiedName", f"unknown_input_{len(G.edges)}"
                )
                output_name = output_entity.get("uniqueAttributes", {}).get(
                    "qualifiedName", f"unknown_output_{len(G.edges)}"
                )
                G.add_edge(input_name, output_name, label=process_name)

    # Create Plotly figure
    pos = nx.spring_layout(G)

    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.5, color="#888"), hoverinfo="none", mode="lines"
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace["x"] += tuple([x0, x1, None])
        edge_trace["y"] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers+text",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
        ),
        textposition="top center",
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_info = f"{G.nodes[node].get('label', 'Unknown')} ({G.nodes[node].get('type', 'Unknown')})"
        node_trace["text"] += tuple([node_info])

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Data Lineage Visualization",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig
