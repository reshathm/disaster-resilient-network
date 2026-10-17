# RESQ-MESH
### Disaster-Resilient Emergency Communication Network

RESQ-MESH is a software-based emergency communication network simulator that demonstrates how rescue teams can maintain communication when network nodes fail, move out of range, or become temporarily unreachable.

It combines mesh topology management, self-healing routing, lost-node recovery, priority-based emergency messaging, and an interactive web dashboard.

> **Scope:** This project simulates network behavior in software. It does not establish real wireless mesh connections or communicate with physical rescue devices.

## Features

- **Mesh Network Simulation:** Models interconnected rescue teams, drones, fire rescue units, and a command center.
- **Live Monitoring:** Displays node positions, connectivity, battery levels, simulated signal strength, and network status.
- **Failure Detection:** Identifies unavailable nodes and communication loss.
- **Self-Healing Routing:** Finds alternative paths when nodes become unavailable.
- **Dijkstra Routing:** Calculates paths across the simulated network.
- **A* Search Routing:** Supports route planning during lost-node recovery.
- **Location Prediction:** Estimates a search area using a lost node's movement information.
- **Collaborative Recovery:** Selects helpers, simulates node discovery, and restores connections.
- **Emergency Messaging:** Routes priority-tagged messages through the network.
- **Event Logging:** Records network operations and recovery events.
- **Interactive Dashboard:** Visualizes topology, routing, recovery, and messaging.
- **Repeatable Demo:** Resets the simulation for another recovery scenario.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| API Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Routing | Dijkstra and A* |
| Testing | pytest |
| Development | Ubuntu / WSL2 |
| Version Control | Git and GitHub |

The frontend is self-contained and requires no JavaScript framework or build process.

## System Architecture

```text
                 RESQ-MESH Dashboard
                  HTML / CSS / JS
                         |
                      HTTP API
                         |
                   FastAPI Backend
                         |
        +----------------+----------------+
        |                |                |
  Network Manager   Recovery System   Messaging
        |                |                |
  Node Monitoring   Location Tracking  Priorities
  Topology          Helper Selection   Route Delivery
  Failure Detection A* Search          Event Logging
  Self-Healing      Reconnection
        |                |                |
        +----------------+----------------+
                         |
                In-Memory Simulation
```

## Initial Network

The simulator starts with five emergency communication nodes:

| Node | Type | X | Y |
|---|---|---:|---:|
| R01 | Rescue Team | 0 | 0 |
| R02 | Rescue Team | 5 | 0 |
| R03 | Drone | 10 | 0 |
| R04 | Fire Rescue | 5 | 5 |
| C01 | Command Center | 15 | 0 |

The default topology has 10 configured connections and a communication range of 16 simulation units.

Node positions, connectivity, and status can change during the simulation.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/reshathm/disaster-resilient-network.git
cd disaster-resilient-network
```

### 2. Create the Python Environment

Python 3.10 or newer is recommended.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start the Backend

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

### 4. Start the Frontend

Keep the backend running. Open a second terminal from the repository root:

```bash
cd frontend
python3 -m http.server 5500 --bind 127.0.0.1
```

Open http://127.0.0.1:5500 in your browser.

The dashboard connects to the backend at `http://127.0.0.1:8000` by default.

For WSL2 users, open the dashboard in your Windows browser while the Ubuntu servers are running.

## API Reference

FastAPI provides interactive documentation at `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| GET | `/network/status` | Network summary |
| GET | `/network/nodes` | Node telemetry |
| GET | `/network/topology` | Nodes and connections |
| GET | `/network/events` | Event history |
| POST | `/network/reset` | Reset simulation |
| POST | `/network/nodes/{node_id}/fail` | Fail a node |
| POST | `/network/nodes/{node_id}/recover` | Recover offline node |
| POST | `/network/nodes/{node_id}/move` | Move node |
| POST | `/network/nodes/{node_id}/recover-lost` | Recover lost node |
| GET | `/network/nodes/{node_id}/recovery` | Recovery status |
| GET | `/network/nodes/{node_id}/helper-candidates` | Rank helpers |
| GET | `/network/route/{source_id}/{destination_id}` | Find route |
| POST | `/network/messages/send` | Send priority message |

### Example: Move R02

```bash
curl -X POST http://127.0.0.1:8000/network/nodes/R02/move \
  -H "Content-Type: application/json" \
  -d '{"x":32,"y":0}'
```

## Lost-Node Recovery Workflow

The dashboard provides a guided recovery demonstration:

1. **Initialize:** Start with five online nodes.
2. **Move:** Move R02 outside communication range.
3. **Detect:** Identify R02 as LOST.
4. **Predict:** Estimate the missing node's search area.
5. **Select Helper:** Rank available recovery helpers.
6. **Plan Search:** Calculate an A*-based search route.
7. **Discover:** Simulate rediscovery of R02.
8. **Reconnect:** Restore eligible mesh connections.
9. **Deliver Message:** Route an emergency message to C01.

The dashboard visualizes node states, recovery stages,
routing information, and recorded network events.

Recovery and message delivery are software simulations,
not real-world wireless transmissions.

## Routing and Self-Healing

**Dijkstra:** Finds paths through the weighted network.
Unavailable nodes are excluded from route calculations.

**A*:** Supports search-related route planning during
lost-node recovery.

**Topology Reconnection:** Updates connections when
nodes move and restores eligible links when nodes
return within communication range.

## Automated Testing

The backend includes automated tests using pytest.

From the repository root:

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

The latest verified development run passed **49 tests**.

Tests cover topology management, reconnection, routing,
failure detection, lost-node recovery, messaging,
network monitoring, and simulation behavior.

## Current Limitations

- Communication and node movement are simulated in software.
- No physical mesh radios or GPS devices are connected.
- Network state is stored in memory, not a database.
- The default demonstration contains five nodes.
- Large-scale network performance has not been evaluated.
- The API is configured for local development, not production.
- CORS currently permits all origins.
- Simulated delivery does not guarantee real-world delivery.

## Future Improvements

- Support larger, configurable mesh networks.
- Simulate network latency, interference, and packet loss.
- Add realistic node mobility and wireless propagation.
- Store telemetry and events in a database.
- Introduce authentication and deployment security.
- Evaluate routing performance with larger topologies.
- Explore integration with physical communication devices.

## Project Purpose

RESQ-MESH demonstrates how adaptive routing, topology
management, and coordinated recovery can support
prototyping of disaster-resilient communication systems.

---

**Developed by Reshath M**

**GitHub:** https://github.com/reshathm/disaster-resilient-network
