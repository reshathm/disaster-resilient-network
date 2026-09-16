# RESQ-MESH — New Frontend + Minimal Backend Patch

This delivers two things:

1. **`resqmesh-dashboard.html`** — a complete, self-contained emergency
   network operations dashboard (no build step, no framework). It only
   ever shows data that came back from your real FastAPI backend — it
   never invents topology, coordinates, scores, or routes.
2. **`backend-patch/`** — three files from your repo with small,
   clearly-commented additions, plus instructions to apply them. These
   are optional except for one: **CORS is required** or the dashboard
   cannot call your API from a browser at all.

Nothing in `app/models`, `app/network/topology.py`,
`app/network/routing.py`, `app/network/helper_selection.py`,
`app/network/connection_monitor.py`, `app/network/failure_detection.py`,
`app/network/monitor.py`, `app/network/messaging.py`,
`app/network/event_log.py`, or `app/simulation/simulator.py` was
touched. Only `main.py`, `search.py`, and `lost_node_recovery.py` change,
and only additively.

---

## 1. Apply the backend patch

Replace these three files in your repo with the ones in `backend-patch/`:

```
backend/app/main.py                        <- backend-patch/main.py
backend/app/network/search.py              <- backend-patch/search.py
backend/app/network/lost_node_recovery.py  <- backend-patch/lost_node_recovery.py
```

Then re-run your test suite to confirm nothing broke:

```bash
cd backend
source venv/bin/activate   # or however you activate your existing venv
pytest
```

I checked every existing test file (`test_search.py`,
`test_lost_node_recovery.py`, and all the rest) against these changes
before writing them. The only behavior that changes is the
`travel_required: True` branch of `SearchCoordinator.find_search_route`
— and none of the 33 existing tests exercise that branch, so nothing
should fail. If something does fail, don't force it through — send me
the failure and I'll fix the patch.

### What changed and why

**`main.py`**
- **CORS middleware (required).** The API currently has none, so a
  browser blocks every request from any page that isn't served by
  FastAPI itself. This adds `CORSMiddleware` with an open policy —
  fine for a local hackathon demo; tighten `allow_origins` before any
  real deployment.
- **Bug fix:** `GET /network/route/{source}/{destination}` and
  `POST /network/messages/send` were the only two endpoints that didn't
  catch `ValueError`. Ask for a route between two nodes with no
  surviving path (e.g. after failing a bridge node) and the API
  returned a raw 500 instead of a clean JSON error like every other
  endpoint. Fixed to match the existing pattern.
- **Event logging.** `EventLog` already existed but only
  `MessageService` ever called `.record()`. Added `.record()` calls at
  node fail/recover/move/lost and at each stage of `recover-lost`
  (prediction, helper selection, A* search, discovery, topology
  rebuild), plus a new `GET /network/events` endpoint to read them
  back. This is what makes the dashboard's event log authoritative
  instead of a client-side reconstruction.
- **`POST /network/reset`** (new). Rebuilds the initial 5-node topology
  and clears the event log, so you can re-run the demo without
  restarting the server.
- **`GET /network/nodes/{id}/helper-candidates`** (new). Your
  `HelperSelector.rank_helpers()` already computes a full ranked list
  of every candidate helper — it just wasn't wired to an endpoint, so
  only the single winner was ever visible. This exposes it so the UI
  can show the comparison table the brief asks for (distance, battery,
  signal, score per candidate), using your existing scoring logic
  unchanged.

**`search.py`**
- Your note was right: `find_search_route`'s "helper needs to travel"
  branch returned a fabricated `[helper_id, "SEARCH_AREA"]` route
  rather than running A*. `find_route_a_star` only works between two
  nodes that already exist in the topology, so this patch temporarily
  adds a waypoint node at the predicted location, wires it to whichever
  online nodes are within communication range of that point (same
  reachability rule `reconnect_node` already uses), runs the real
  `NetworkRouter.find_route_a_star(helper_id, waypoint_id)`, then
  removes the waypoint. It never appears in `/network/nodes` or
  `/network/topology`. The "already inside the radius" branch (the only
  one your tests cover) is untouched.

**`lost_node_recovery.py`**
- One-line change: passes `self.communication_range` through to
  `find_search_route` so the new A* waypoint wiring uses the same range
  as the rest of the simulation.

If you'd rather not touch the backend at all, the dashboard still
works with everything *except*: CORS (nothing will load — see below),
the authoritative event log (falls back to a local log built from the
dashboard's own actions), the full helper-candidate table (falls back
to showing just the selected helper), and genuine A* multi-hop routes
(the existing fake straight-line route still displays, just not
via A*).

---

## 2. Run it

```bash
# backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Open `resqmesh-dashboard.html` — don't just double-click it. Opening it
as a `file://` URL can trip browser CORS/mixed-content rules even with
the server-side CORS patch applied. Serve it instead:

```bash
cd wherever-you-put-the-html-file
python3 -m http.server 5500
```

then visit `http://127.0.0.1:5500/resqmesh-dashboard.html`. If your
backend isn't at `http://127.0.0.1:8000`, change it in the "API" field
in the header and click **Connect** — it's remembered for next time.

---

## 3. Data safety / what's real vs. derived

- Every node, coordinate, status, route, prediction, helper score, and
  message result on screen comes directly from an API response.
  Nothing is fabricated client-side.
- The one place the dashboard computes something itself: **Network
  Health** counts (`total/online/lost/offline`) are derived from
  `GET /network/nodes` rather than `GET /network/status`, because your
  existing `NetworkMonitor.get_network_summary()` only counts
  online + offline and doesn't count `LOST` nodes at all. I didn't
  patch `monitor.py` since it's used elsewhere and wasn't part of the
  requested scope — flagging it here in case you want it fixed too.
- If the optional `/network/events` or `/helper-candidates` endpoints
  aren't present (patch not applied), the dashboard says so in the UI
  (small tag next to the panel header) rather than silently pretending
  they're there.
- All state lives in memory in your FastAPI process, same as before —
  the dashboard doesn't add a database or any new persistence.

---

## 4. Using the dashboard

- **Move / Fail / Recover / Recover Lost Node** in the Node Details
  panel call the real endpoints directly.
- **Run Recovery Demo** in the header runs the exact spec sequence:
  moves R02 out of range → confirms LOST → calls `recover-lost` →
  looks up the Dijkstra route to C01 → sends a CRITICAL message — each
  step paced with a short delay so you can narrate it live, and each
  step reads its result from the real API response. **Pause** stops
  between steps; there's no fake "instant" mode.
- **Reset Network** calls `/network/reset` if you applied the patch;
  otherwise it tells you the endpoint isn't there instead of pretending
  to reset.
- Dijkstra routes render as bright animated cyan lines on the map;
  A* search routes render as dashed purple lines — kept visually and
  textually distinct per the spec, with each panel labeled which
  algorithm it's showing.
