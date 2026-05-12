# Neural Network Playground (Java + React)

A clone of the classic
[Tensorflow Playground](https://playground.tensorflow.org/), reimagined with
the neural-network engine running in **Java** (zero dependencies) and a fresh
**React + Tailwind** UI. The original project shipped everything as a single
client-side TypeScript bundle; this version splits the responsibilities cleanly:

| Concern | Implemented in | Folder |
| ------- | -------------- | ------ |
| Forward / back-prop, datasets, training loop | Java 11 (built-in `com.sun.net.httpserver`) | `backend/` |
| Visualisation, controls, network graph | React 18 + Vite + Tailwind | `frontend/` |

## Demo features

The UI faithfully reproduces every knob from the original:

* 4 classification datasets (circle, XOR, gaussian, spiral) and 2 regression
  datasets (plane, multi-gaussian)
* 2D input coordinates (X₁ and X₂) as the input layer
* 0 - 6 hidden layers, each with 1 - 8 neurons (configurable per layer)
* 4 activations (Tanh, ReLU, Sigmoid, Linear) and 3 regularisers (None, L1, L2)
* Live decision boundary heat-map, per-node mini heat-maps, hover tooltips
  for weights and biases, train / test loss line chart
* Adjustable learning rate, regularisation rate, batch size, noise, train /
  test ratio
* Play / Pause / Step / Reset, "Regenerate data", and "Discretise output"

## Quick start

You will need:

* JDK 11 or newer (works without Maven / Gradle - we just use `javac`)
* Node.js 18+

### 1. Start the backend

```bash
cd backend
./build.sh        # or build.bat on Windows
./run.sh          # or run.bat on Windows
# > Playground backend listening on http://localhost:8080
```

### 2. Start the frontend

```bash
cd frontend
npm install
npm run dev
# > Vite dev server at http://localhost:5173
```

Open http://localhost:5173 in your browser.

In production, run `npm run build` and serve `frontend/dist` from any static
file server pointing the `/api` path at the Java backend.

## Architecture

```
+-------------+   POST /api/sessions/{id}/train, /boundary, ...   +-------------+
|   React UI  | <--------------------------------------------->   | Java engine |
| (frontend/) |                                                   | (backend/)  |
+-------------+                                                   +-------------+
       ^                                                                 |
       | snapshot {iter, lossTrain, lossTest, layers, links, ...}        |
       +-----------------------------------------------------------------+
```

### Backend highlights (`backend/`)

* `nn/NeuralNetwork.java` - faithful port of the original `nn.ts`:
  `buildNetwork`, `forwardProp`, `backProp`, `updateWeights`, with mini-batch
  SGD and L1 / L2 regularisation (including the dead-link clamp at zero).
* `data/Datasets.java` - all six dataset generators using a seeded `Random`
  so runs are reproducible.
* `api/SessionManager.java` - per-session locks, idle timeout (30 min), and a
  256-session cap so the server never grows unbounded.
* `util/Json.java` - a tiny purpose-built JSON encoder / decoder; the project
  has zero third-party dependencies.

### Frontend highlights (`frontend/`)

* Decision boundary is rendered with a single `<canvas>` element using
  `putImageData` for very fast updates (matches the original's approach).
* Network graph is plain SVG; weights and biases live-update each frame
  because the snapshot returned by the backend already includes them.
* The play loop fires `POST /train` with `epochs=1` repeatedly so slider /
  drop-down changes apply mid-training. Boundary fetches are batched
  (one every five steps by default) to keep network traffic reasonable.

## Verifying the install

After both servers are running, hit the smoke endpoint:

```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

Or in the UI: pick **circle**, hit **Play**, and within ~50 epochs the loss
should plummet from ~0.5 to <0.01.

Switch to **spiral**, bump the network to 3 hidden layers of 8 neurons each, and watch the decision boundary morph as the network trains.

## Repository layout

```
OOP_NN_Playground/
  backend/          # Java REST service
  frontend/         # React + Tailwind UI
  playground/       # Original Tensorflow Playground (read-only reference)
  README.md         # this file
```
