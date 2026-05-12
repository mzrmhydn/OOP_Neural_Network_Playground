# Neural Network Playground — OOP in Java & file guide

This document explains **what the project does**, how **standard Java OOP ideas** show up in the code, and **what each backend Java file is responsible for**. The backend lives under `backend/src/main/java/com/playground` and has **no external libraries** (JDK only).

---

## Part A — What is this project?

The **Neural Network Playground** is an educational clone of the classic browser “playground” idea: the user chooses a **2D dataset**, a **small feed-forward network** (layers and neurons), **hyperparameters** (learning rate, activation, regularization, …), and **trains** the network with **mini-batch SGD** while watching **loss** and a **decision boundary**.

- The **Java backend** trains the network (forward pass, backpropagation, weight updates) and exposes a small **HTTP JSON API** so a **React frontend** can drive training and draw charts.
- The codebase is structured so a **Java OOP course** can point to **real** encapsulation, inheritance, polymorphism, interfaces, abstract classes, custom exceptions, composition, and static factories—not toy `Animal`/`Dog` examples only.

---

## Part B — Basic OOP concepts and how this project implements them

### 1. Encapsulation (hiding state, exposing behaviour)

**Idea:** Fields are not public blobs of data; the object controls *how* they change through methods, so invariants stay true.

**Implementation:**

- **`Node`**: Private fields for bias, activations, gradients, and link lists. Training steps go through methods like `updateOutput()`, `seedOutputDer(double)`, `applyBiasUpdate(double)`—callers cannot poke partial derivatives directly.
- **`Link`**: Weight and gradient accumulators are private; updates run through `computeAndAccumulateErrorDer()` and `applyWeightUpdate(double, double)`.
- **`Session`**: Configuration (noise, shape, seeds, dataset references) uses getters and setters; setters validate (e.g. throw `ConfigurationException` for bad values) before mutating state.
- **`Example2D`**: Immutable point—`private final` coordinates and label, exposed only via getters.

---

### 2. Inheritance (IS-A, code reuse from a superclass)

**Idea:** A subclass **extends** a superclass, inherits members, and overrides or adds behaviour.

**Implementation:**

- **`ActivationFunction`** ← **`TanhActivation`**, **`ReluActivation`**, **`SigmoidActivation`**, **`LinearActivation`** — each overrides `output` and `derivative` for its maths.
- **`RegularizationFunction`** ← **`NoRegularization`**, **`L1Regularization`**, **`L2Regularization`** — same pattern for penalty on weights; **`L1Regularization`** additionally overrides **`crossesZero`** for the “dead link” rule.
- **`DataGenerator`** ← **`CircleDataset`**, **`XorDataset`**, **`GaussianDataset`**, **`SpiralDataset`**, **`PlaneRegressionDataset`**, **`GaussianRegressionDataset`** — each implements **`generate(...)`** for its pattern of points.
- **`PlaygroundException`** ← **`ConfigurationException`**, **`NotFoundException`**, **`TrainingException`**; **`SessionNotFoundException`** extends **`NotFoundException`** (multi-level hierarchy ending at **`RuntimeException`**).

---

### 3. Polymorphism (one interface, many behaviours at runtime)

**Idea:** The same method call can run **different implementations** depending on the **actual object type** (dynamic dispatch).

**Implementation:**

- **`Node.updateOutput()`** calls **`activation.output(...)`** — the concrete activation class (Tanh, ReLU, …) is chosen when the network is built; **`Node`** does not branch on type names.
- **`Link.applyWeightUpdate`** calls **`regularization.derivative(...)`** and **`regularization.crossesZero(...)`** — L1 vs L2 vs none is handled by the subclass **without `instanceof` in `Link`**.
- **`ApiServer.dispatch`** catches **`PlaygroundException`** and uses **`getHttpStatus()`** — each concrete exception subclass was constructed with its status; the handler does not switch on exception class for HTTP codes.
- **`InputFeatures.Feature`**: Each enum constant holds a **`DoubleBinaryOperator`**; **`apply(x,y)`** runs the right formula polymorphically.

---

### 4. Abstraction (interfaces and abstract classes)

**Idea:** Hide **how** something works; publish **what** contract callers depend on.

**Implementation:**

- **`DifferentiableFunction`**: Interface with `output` and `derivative` — implemented by both **`ActivationFunction`** and **`RegularizationFunction`** (two unrelated hierarchies sharing a mathematical contract).
- **`ActivationFunction`** / **`RegularizationFunction`**: Abstract classes sharing a **name** and **`final getName()`**, leaving activation/derivative math abstract.
- **`DataGenerator`**: Abstract **`generate`**, **`getKey`**, **`isRegression`** — concrete datasets fill in generation only.
- **`PlaygroundException`**: Abstract base so only **meaningful** subtypes are thrown; **`getHttpStatus()`** is **`final`**.

---

### 5. Interfaces as contracts only

**Idea:** A type defines **obligation** without dictating **inheritance** of implementation state.

**Implementation:**

- **`Trainable`**: **`Session`** implements it so anything that can “run epochs” can be used through **`Trainable`** without importing all of **`Session`**.
- **`ErrorFunction`**: Implemented by **`SquaredError`** — loss for backprop is pluggable at the type level.
- **`DifferentiableFunction`**: Already mentioned — shared “calculus shape” for activations and regularizers.

---

### 6. Composition & aggregation (HAS-A)

**Idea:** Build complex objects from **parts** (fields), prefer composition over exaggerated inheritance.

**Implementation:**

- **`Session` has-a** **`DataGenerator`**, **`ActivationFunction`**, **`RegularizationFunction`**, lists of **`Feature`**, **`List<List<Node>>` network**, train/test **`Example2D`** lists — it does **not** subclass those types.
- **`Node` has-a** **`ActivationFunction`** and **lists of `Link`**.
- **`Link` has-a** **`source` and `dest`** **`Node`**, and **one** **`RegularizationFunction`**.
- **`ApiServer` has-a** **`SessionManager`** and **`RequestHandlers`**.
- **`SessionManager` has-a** **`Map<String, Session>`** (many sessions).

---

### 7. Exception handling (custom hierarchy + HTTP mapping)

**Idea:** Represent error cases as types with data; central handling where appropriate.

**Implementation:**

- **`PlaygroundException`** stores **HTTP status**; subclasses pick **400 / 404 / 500**.
- **`ConfigurationException`**: bad request body or invalid config.
- **`SessionNotFoundException`**: unknown session id (via **`SessionManager.require`**).
- **`TrainingException`**: wraps failures during training (may chain **`cause`**).
- **`RequestHandlers`** and **`ApiServer`** let these exceptions bubble to **`ApiServer`**, which maps them to responses.
- **`try-with-resources`** in **`ApiServer.readBody`** closes streams reliably.

---

### 8. Static factories, registries, singletons

**Idea:** Construct or look up objects through **named methods** or **single shared instances** when construction policy should be centralized.

**Implementation:**

- **`Activations.byKey(String)`**, **`Regularizations.byKey(String)`**, **`DatasetRegistry.byKey(String)`**: map lookup + **`ConfigurationException`** if unknown.
- **`SquaredError.INSTANCE`**: stateless loss object reused everywhere.
- Public static **`TANH`**, **`NONE`**, **`CIRCLE`**, … constants for default wiring.

---

### 9. `final` keyword

**Idea:** Prevent subclassing or override where the design is closed; mark immutable references.

**Implementation:**

- Concrete activations, regularizers, many datasets: **`final class`**.
- **`Example2D`**: **`final`** immutable object.
- **`PlaygroundException.getHttpStatus()`**, **`ActivationFunction.getName()`** where applicable: **`final`** methods.
- Many identity fields **`private final`** on **`Node`**, **`Link`**, **`Session`** id, etc.

---

### 10. Method overloading

**Idea:** Same method name, different parameter lists.

**Implementation:**

- **`Session`**: **`trainOneEpoch(double, double, int)`** and **`trainOneEpoch()`** (defaults for learning rate, reg rate, batch size).

---

### 11. Generics (standard library usage)

**Idea:** Type-safe collections and APIs.

**Implementation:**

- **`Map<String, Session>`**, **`List<List<Node>>`**, **`List<Feature>`**, **`Json`** walking **`Map<?, ?>`** / **`List<?>`** shapes.

---

### 12. Static vs instance design

**Idea:** Put **stateless algorithms** on static helpers; put **per-session or per-object state** on instances.

**Implementation:**

- **`NeuralNetwork`**: only **static** methods — no network-wide singleton object; the graph is **`List<List<Node>>`** owned by **`Session`**.
- **`Activations`**, **`Regularizations`**, **`DatasetRegistry`**, **`Json`**: private constructors, static API.
- **`Session`**, **`Node`**, **`Link`**: rich **instance** state and methods.

---

## Part C — What each Java file does

Paths are under `backend/src/main/java/com/playground/`.

### Root

| File | Role |
| ---- | ---- |
| **`Main.java`** | Reads port from args/env; starts **`ApiServer`**; registers JVM shutdown hook to stop the server. |

### `api/` — HTTP-facing layer

| File | Role |
| ---- | ---- |
| **`ApiServer.java`** | Creates **`HttpServer`**, wires **`/api/`** to **`RequestHandlers`**, handles CORS/OPTIONS, maps **`PlaygroundException`** (and fallbacks) to status codes, reads bodies with **`try-with-resources`**. |
| **`RequestHandlers.java`** | Dispatches routes: create/delete session, get state, configure, regenerate data, build network, train, boundary snapshot. Parses JSON with **`Json`**, calls **`Session`** / **`SessionManager`**. |
| **`SessionManager.java`** | In-memory **`Map<String, Session>`**; create/remove/get; **`require`** throws **`SessionNotFoundException`**; per-session locks; optional idle cleanup. |
| **`Session.java`** | One user session: config, **`Trainable`** implementation, data generation, **`NeuralNetwork.buildNetwork`**, training loop calling **`NeuralNetwork`** + **`SquaredError`**, loss fields. |
| **`Trainable.java`** | Interface: one epoch + iteration + train/test loss getters. |

### `nn/` — Network math and graph

| File | Role |
| ---- | ---- |
| **`DifferentiableFunction.java`** | Interface: scalar **`output`** and **`derivative`**. |
| **`ErrorFunction.java`** | Interface: loss **`error`** and **`derivative`** vs label. |
| **`SquaredError.java`** | **`ErrorFunction`** implementation; **`INSTANCE`** singleton for squared loss. |
| **`ActivationFunction.java`** | Abstract activation: name + abstract **`output`/`derivative`**; implements **`DifferentiableFunction`**. |
| **`NeuralNetwork.java`** | Static **`buildNetwork`**, **`forwardProp`**, **`backProp`**, **`updateWeights`**, graph iterators — orchestrates **`Node`**/**`Link`**. |
| **`Node.java`** | One neuron: **`ActivationFunction`**, links, forward/backward methods, bias update. |
| **`Link.java`** | Weighted edge between two **`Node`s**; gradient accumulation; **`applyWeightUpdate`** with **`RegularizationFunction`**. |

### `nn/activation/`

| File | Role |
| ---- | ---- |
| **`TanhActivation.java`** | Tanh and its derivative. |
| **`ReluActivation.java`** | ReLU and derivative. |
| **`SigmoidActivation.java`** | Sigmoid and derivative. |
| **`LinearActivation.java`** | Identity activation for regression-style output. |
| **`Activations.java`** | Registry: static instances, **`byKey(String)`**, **`all()`**. |

### `nn/regularization/`

| File | Role |
| ---- | ---- |
| **`RegularizationFunction.java`** | Abstract penalty on weight; **`crossesZero`** hook for L1 edge case. |
| **`NoRegularization.java`** | Zero penalty / zero derivative. |
| **`L1Regularization.java`** | L1 penalty + derivative; overrides **`crossesZero`**. |
| **`L2Regularization.java`** | L2 penalty + derivative. |
| **`Regularizations.java`** | Registry like **`Activations`**. |

### `data/`

| File | Role |
| ---- | ---- |
| **`Example2D.java`** | Immutable training point **`(x, y, label)`**. |
| **`InputFeatures.java`** | Enum **`Feature`** (`x`, `y`) with **`DoubleBinaryOperator`**; builds feature vector **`build`**, parses keys **`parseKeys`**. |

### `data/datasets/`

| File | Role |
| ---- | ---- |
| **`DataGenerator.java`** | Abstract: **`generate`**, **`getKey`**, **`isRegression`**, shared random helpers. |
| **`CircleDataset.java`** | Two-moon / circle-like classification cloud. |
| **`XorDataset.java`** | XOR pattern. |
| **`GaussianDataset.java`** | Two Gaussians classification. |
| **`SpiralDataset.java`** | Spiral classification. |
| **`PlaneRegressionDataset.java`** | Regression on a plane. |
| **`GaussianRegressionDataset.java`** | Regression with Gaussian response. |
| **`DatasetRegistry.java`** | Static dataset instances and **`byKey`**. |

### `exceptions/`

| File | Role |
| ---- | ---- |
| **`PlaygroundException.java`** | Abstract base with **`httpStatus`**; **`final getHttpStatus()`**. |
| **`ConfigurationException.java`** | HTTP 400 — invalid configuration or request. |
| **`NotFoundException.java`** | HTTP 404 — resource not found (base). |
| **`SessionNotFoundException.java`** | HTTP 404 — unknown session id. |
| **`TrainingException.java`** | HTTP 500 — training failure; may wrap cause. |

### `util/`

| File | Role |
| ---- | ---- |
| **`Json.java`** | Minimal JSON encode/decode for request/response maps and lists (no third-party JSON library). |

---

## Part D — One-line “study map”

- **Training mechanics:** `NeuralNetwork.java` + `Node.java` + `Link.java`  
- **“Which activation / regularizer / dataset?”** subclass hierarchies + `Activations` / `Regularizations` / `DatasetRegistry`  
- **“How does the UI talk to Java?”** `ApiServer.java` + `RequestHandlers.java` + `Session.java`  
- **“How do we teach OOP?”** encapsulation in `Node`/`Link`/`Session`, polymorphism on activations and `PlaygroundException`, interfaces `Trainable` / `DifferentiableFunction` / `ErrorFunction`, inheritance in datasets and exceptions.

---

For **UML-style relationships** between classes, see **`CLASS_AND_RELATIONSHIPS.md`**. For a **four-speaker presentation split**, see **`PRESENTATION_GUIDE.md`**. For the original detailed OOP map, see **`backend/OOP_DESIGN.md`**.
