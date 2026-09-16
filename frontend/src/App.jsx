import "./App.css";

const nodes = [
  { id: "R01", type: "Rescue Team", status: "ONLINE", x: 18, y: 48 },
  { id: "R02", type: "Rescue Team", status: "ONLINE", x: 38, y: 30 },
  { id: "R03", type: "Drone", status: "ONLINE", x: 58, y: 48 },
  { id: "R04", type: "Fire Rescue", status: "ONLINE", x: 38, y: 68 },
  { id: "C01", type: "Command Center", status: "ONLINE", x: 82, y: 48 },
];

const connections = [
  ["R01", "R02"],
  ["R01", "R04"],
  ["R02", "R03"],
  ["R04", "R03"],
  ["R03", "C01"],
];

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="brand">RESQ-MESH</div>
          <div className="subtitle">
            Disaster-Resilient Emergency Communication Network
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SYSTEM OPERATIONAL
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <p className="eyebrow">EMERGENCY NETWORK MONITOR</p>
            <h1>Self-Healing Mesh Network</h1>
            <p className="hero-text">
              Real-time simulation of resilient communication, node failures,
              lost-node recovery, and emergency message routing.
            </p>
          </div>

          <div className="hero-stat">
            <strong>5</strong>
            <span>ACTIVE NODES</span>
          </div>
        </section>

        <section className="stats">
          <div className="stat-card">
            <span>Total Nodes</span>
            <strong>5</strong>
          </div>

          <div className="stat-card">
            <span>Online</span>
            <strong className="green">5</strong>
          </div>

          <div className="stat-card">
            <span>Lost</span>
            <strong>0</strong>
          </div>

          <div className="stat-card">
            <span>Connections</span>
            <strong>5</strong>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel network-panel">
            <div className="panel-header">
              <div>
                <span className="panel-label">LIVE TOPOLOGY</span>
                <h2>Network Map</h2>
              </div>

              <span className="live-badge">
                <span className="status-dot" />
                LIVE
              </span>
            </div>

            <div className="network-map">
              <svg className="connections" viewBox="0 0 100 100">
                {connections.map(([source, target]) => {
                  const a = nodes.find((node) => node.id === source);
                  const b = nodes.find((node) => node.id === target);

                  return (
                    <line
                      key={`${source}-${target}`}
                      x1={a.x}
                      y1={a.y}
                      x2={b.x}
                      y2={b.y}
                      className="connection-line"
                    />
                  );
                })}
              </svg>

              {nodes.map((node) => (
                <div
                  key={node.id}
                  className="network-node"
                  style={{
                    left: `${node.x}%`,
                    top: `${node.y}%`,
                  }}
                >
                  <div className="node-ring">
                    <div className="node-core" />
                  </div>

                  <div className="node-info">
                    <strong>{node.id}</strong>
                    <span>{node.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <aside className="panel node-panel">
            <div className="panel-header">
              <div>
                <span className="panel-label">NODE STATUS</span>
                <h2>Network Units</h2>
              </div>
            </div>

            <div className="node-list">
              {nodes.map((node) => (
                <div className="node-row" key={node.id}>
                  <div className="node-name">
                    <span className="status-dot" />
                    <div>
                      <strong>{node.id}</strong>
                      <span>{node.type}</span>
                    </div>
                  </div>

                  <span className="online-pill">{node.status}</span>
                </div>
              ))}
            </div>
          </aside>
        </section>

        <section className="panel activity-panel">
          <div className="panel-header">
            <div>
              <span className="panel-label">SYSTEM ACTIVITY</span>
              <h2>Event Log</h2>
            </div>
          </div>

          <div className="event">
            <span className="event-time">NOW</span>
            <span className="event-dot" />
            <div>
              <strong>Network initialized</strong>
              <span>All communication links are currently operational.</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;