from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

class PipelinePayload(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


def check_is_dag(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> bool:
    node_ids = {node.get("id") for node in nodes if node.get("id") is not None}
    adjacency = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source is None or target is None:
            continue

        if source not in adjacency:
            adjacency[source] = []
            indegree[source] = indegree.get(source, 0)
        if target not in adjacency:
            adjacency[target] = []
            indegree[target] = indegree.get(target, 0)

        adjacency[source].append(target)
        indegree[target] = indegree.get(target, 0) + 1

    queue = [node_id for node_id, deg in indegree.items() if deg == 0]
    visited = 0

    while queue:
        node_id = queue.pop()
        visited += 1
        for neighbor in adjacency.get(node_id, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited == len(indegree)


@app.post('/pipelines/parse')
def parse_pipeline(payload: PipelinePayload):
    num_nodes = len(payload.nodes)
    num_edges = len(payload.edges)
    is_dag = check_is_dag(payload.nodes, payload.edges)
    return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': is_dag}
