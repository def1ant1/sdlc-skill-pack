# Network Topology Graph Schema Reference

## Graph Model

The network topology is represented as a directed weighted graph:
- **Nodes:** Network devices (servers, switches, routers, load balancers, firewalls)
- **Edges:** Network links with capacity, latency, and utilization attributes

---

## Node Schema

```yaml
node_types:
  - type: "host"
    properties:
      id: string           # e.g., "server-42.rack-3.dc-east"
      hostname: string
      ip_addresses: list[string]
      rack_id: string
      pod_id: string
      datacenter_id: string
      role: "compute" | "storage" | "gateway" | "management"
      services: list[string]  # Running service names
      hardware:
        cpu_cores: integer
        memory_gb: integer
        nic_speed_gbps: integer
        nic_count: integer

  - type: "switch"
    properties:
      id: string
      hostname: string
      switch_type: "ToR" | "aggregation" | "spine" | "border"
      rack_id: string
      port_count: integer
      switching_capacity_gbps: integer
      protocol: "ethernet" | "infiniband" | "fibre_channel"
      managed: boolean

  - type: "router"
    properties:
      id: string
      hostname: string
      router_type: "core" | "edge" | "border"
      routing_protocols: list[string]  # BGP, OSPF, IS-IS
      asn: integer  # Autonomous System Number

  - type: "load_balancer"
    properties:
      id: string
      lb_type: "hardware" | "software" | "cloud"
      vip_addresses: list[string]
      backend_pool: list[string]  # Node IDs in backend
      algorithm: "round_robin" | "least_connections" | "ip_hash"
      health_check_interval_s: integer

  - type: "firewall"
    properties:
      id: string
      firewall_type: "stateful" | "next_gen" | "waf"
      zone_from: string
      zone_to: string
      rule_count: integer
```

---

## Edge Schema

```yaml
edge_schema:
  id: string                # "{from_node_id}:{from_port}-{to_node_id}:{to_port}"
  from_node: string
  to_node: string
  from_port: string
  to_port: string

  physical:
    media: "copper" | "fiber" | "wireless" | "virtual"
    speed_gbps: float
    duplex: "full" | "half"

  logical:
    vlan_id: integer | null
    encapsulation: "ethernet" | "infiniband" | "fiber_channel" | "vxlan"
    mtu: integer  # Maximum Transmission Unit

  operational:
    utilization_pct: float      # Current utilization (0.0–1.0)
    utilization_p95_pct: float  # P95 utilization over last 24h
    latency_us: float           # One-way latency in microseconds
    packet_loss_pct: float      # Current packet loss rate
    errors_per_second: float
    status: "UP" | "DOWN" | "DEGRADED" | "MAINTENANCE"
```

---

## Topology Graph Serialization

```json
{
  "@type": "NetworkTopologyGraph",
  "graph_id": "NET-TOPO-DC-EAST-20260507",
  "captured_at": "2026-05-07T12:00:00Z",
  "datacenter": "us-east-1",
  "nodes": [
    {
      "id": "spine-sw-01",
      "type": "switch",
      "switch_type": "spine",
      "switching_capacity_gbps": 12800,
      "port_count": 64
    },
    {
      "id": "tor-sw-rack3",
      "type": "switch",
      "switch_type": "ToR",
      "rack_id": "rack-3",
      "switching_capacity_gbps": 800
    }
  ],
  "edges": [
    {
      "id": "spine-sw-01:eth1-tor-sw-rack3:uplink1",
      "from_node": "spine-sw-01",
      "to_node": "tor-sw-rack3",
      "speed_gbps": 100,
      "utilization_pct": 0.34,
      "latency_us": 1.2,
      "status": "UP"
    }
  ]
}
```

---

## Topology Analysis Queries

### Query 1: Shortest Path (Minimum Latency)

```python
def shortest_path_latency(graph, source, destination):
    """Dijkstra's algorithm weighted by latency_us"""
    return nx.shortest_path(
        graph,
        source=source,
        target=destination,
        weight="latency_us"
    )
```

### Query 2: Bottleneck Detection

```python
def find_bottlenecks(graph, threshold=0.80):
    """Find edges with utilization above threshold"""
    bottlenecks = [
        edge for edge in graph.edges(data=True)
        if edge[2].get("utilization_pct", 0) > threshold
    ]
    return sorted(bottlenecks, key=lambda e: -e[2]["utilization_pct"])
```

### Query 3: Fault Domain Analysis

```python
def fault_domains(graph, node_id):
    """
    Find all nodes that would lose connectivity if node_id fails.
    Returns list of affected node sets.
    """
    graph_without_node = graph.copy()
    graph_without_node.remove_node(node_id)

    # Find newly disconnected components
    original_components = nx.number_weakly_connected_components(graph)
    new_components = list(nx.weakly_connected_components(graph_without_node))

    if len(new_components) > original_components - 1:
        # Network partitioned — identify isolated nodes
        return [comp for comp in new_components if len(comp) < 3]
    return []
```

### Query 4: Redundancy Check

```python
def check_redundancy(graph, source, destination, min_paths=2):
    """Verify at least min_paths node-disjoint paths exist"""
    paths = list(nx.node_disjoint_paths(graph, source, destination))
    return {
        "has_redundancy": len(paths) >= min_paths,
        "path_count": len(paths),
        "paths": paths[:5]  # Return up to 5 paths
    }
```

---

## Topology Health Metrics

```yaml
topology_health_metrics:
  as_of: "2026-05-07T12:00:00Z"

  connectivity:
    total_nodes: 342
    reachable_nodes: 342
    unreachable_nodes: 0
    partitioned_segments: 0

  redundancy:
    nodes_with_single_uplink: 4  # WARN: no redundancy
    links_without_redundant_path: 2  # WARN

  utilization:
    high_utilization_links: 3  # > 80%
    critical_utilization_links: 0  # > 95%
    average_utilization_pct: 34.2

  performance:
    average_east_west_latency_us: 8.4
    max_east_west_latency_us: 42.1
    packet_loss_above_threshold: 0  # Links with > 0.01% loss

  health_score: 0.94  # 0.0 worst, 1.0 best
```