# Presentation guide — concepts by file (Java OOP focus)

This document supports a **four-person team presentation** of the **OOP Neural Network Playground** backend. Each section lists **what the file is responsible for** and **which OOP ideas it illustrates**. Use it to assign slides and speaking roles without overlapping content.

**Scope:** The explanations below target the **Java backend** (`backend/src/main/java`). The **React frontend** is the visualization shell; it is not required for an OOP-centred Java grade, but you can mention it as “client” in one slide if needed.

---

## Suggested division for four team members

| Member | Theme | Primary packages / files | OOP story (one sentence) |
| ------ | ----- | ------------------------ | ------------------------- |
| **1** | **API & session lifecycle** | `Main`, `api/*` | *Interfaces, composition, encapsulation of configuration, HTTP as a boundary that maps exceptions to status codes.* |
| **2** | **Network core & polymorphism** | `nn/*`, `nn/activation/*`, `nn/regularization/*` | *Abstract classes and interfaces, late-bound behaviour in forward/back-prop, “Tell, Don’t Ask” on `Node`/`Link`.* |
| **3** | **Data, features, datasets** | `data/*`, `data/datasets/*` | *Inheritance for dataset generators, enum-as-class for features, immutability, static registries.* |
| **4** | **Exceptions & infrastructure** | `exceptions/*`, `util/Json.java` | *Custom exception hierarchy, layered inheritance, defensive I/O, minimal generic JSON walking.* |

**Timing tip:** Each member can use **4–5 minutes**: (1) problem, (2) 2–3 files with code pointers, (3) one OOP term tied to a method name, (4) takeaway.

---

## Member 1 — entry point, HTTP API, sessions

### `com/playground/Main.java`

- **Concepts:** application **composition root**; `public static void main`; starts `ApiServer` on a port from args or default.
- **OOP:** thin entry; no domain logic — **separation of concerns**.

### `com/playground/api/ApiServer.java`

- **Concepts:** embedded `com.sun.net.httpserver.HttpServer`; **routing** by path/method; JSON request/response; **`PlaygroundException` → HTTP status** mapping.
- **OOP:** **centralized exception handling** (`catch (PlaygroundException)` then fallbacks); **composition** (`SessionManager`, `RequestHandlers`); **try-with-resources** in `readBody` for streams; handling `BindException` for UX.

### `com/playground/api/RequestHandlers.java`

- **Concepts:** façade for REST-style actions: create/configure session, train, boundary, regenerate data, etc.
- **OOP:** coordinates `SessionManager` and `Session`; validates input; throws **`ConfigurationException`**, **`TrainingException`**, **`SessionNotFoundException`**; **delegation** instead of god-class logic.

### `com/playground/api/SessionManager.java`

- **Concepts:** in-memory `Map<String, Session>`; create/remove; optional idle eviction; concurrency **per-session locks**.
- **OOP:** **encapsulation** of the map; factory-like `create()`; **`require` / `requireLockFor`** throwing **`SessionNotFoundException`** — fail-fast API.

### `com/playground/api/Session.java`

- **Concepts:** one playground run: dataset, network shape, activations, regularization, **train/test data**, **`List<List<Node>>` network**, training loop state.
- **OOP:** **`implements Trainable`** (interface); **encapsulation** with validating setters (`setNoise`, `setDataset`, …); **`final` fields** where appropriate; **composition** (has-a `DataGenerator`, `ActivationFunction`, `RegularizationFunction`, network); **method overloading** — `trainOneEpoch(...)` vs `trainOneEpoch()` with defaults; inner enum **`Problem`** (**classification / regression**).

### `com/playground/api/Trainable.java`

- **Concepts:** contract “object that can be trained for one epoch and expose losses/iteration”.
- **OOP:** **interface segregation**; allows tests or alternate frontends to depend on behaviour, not on `Session` internals.

---

## Member 2 — neural network package (`nn`)

### `com/playground/nn/DifferentiableFunction.java`

- **Concepts:** `output(double)`, `derivative(double)` — shared math contract for activations and regularizers.
- **OOP:** **interface**; **abstraction** of “something differentiable” shared by unrelated hierarchies.

### `com/playground/nn/ActivationFunction.java`

- **Concepts:** base for hidden/output activations; holds **`name`**; subclasses implement `output`/`derivative`.
- **OOP:** **abstract class** (shared state + **`final getName()`**); **`implements DifferentiableFunction`**; concrete classes are **`final`**.

### `com/playground/nn/activation/TanhActivation.java`, `ReluActivation.java`, `SigmoidActivation.java`, `LinearActivation.java`

- **Concepts:** each implements one activation’s formulas.
- **OOP:** **inheritance + polymorphism** — same method names, different bodies; **`final` classes**.

### `com/playground/nn/activation/Activations.java`

- **Concepts:** registry `byKey(String)`; static instances `TANH`, `RELU`, …; **singleton-like** reuse of stateless objects.
- **OOP:** **`final` class**, **private constructor**, **static factory** `byKey`; **encapsulated** `Map`; throws **`ConfigurationException`** for unknown keys.

### `com/playground/nn/RegularizationFunction.java`

- **Concepts:** L1/L2/none penalty on weights; **`crossesZero`** hook for L1 dead-link behaviour.
- **OOP:** **abstract class** + **template-style hook** (`crossesZero` overridable in `L1Regularization`); **`implements DifferentiableFunction`**.

### `com/playground/nn/regularization/NoRegularization.java`, `L1Regularization.java`, `L2Regularization.java`

- **Concepts:** derivatives and optional **zero-crossing** detection for L1.
- **OOP:** **inheritance**; **`L1Regularization` overrides `crossesZero`** — polymorphism used from **`Link`**.

### `com/playground/nn/regularization/Regularizations.java`

- **Concepts:** same pattern as `Activations` — `NONE`, `L1`, `L2`, `byKey(String)`.
- **OOP:** static factory + registry; **final** utility class.

### `com/playground/nn/ErrorFunction.java`

- **Concepts:** loss: `error(output, target)`, `derivative(output, target)`.
- **OOP:** **interface** — loss is pluggable (currently only squared error in use).

### `com/playground/nn/SquaredError.java`

- **Concepts:** MSE-style squared error implementation.
- **OOP:** **`implements ErrorFunction`**; **`INSTANCE` singleton** (stateless).

### `com/playground/nn/Node.java`

- **Concepts:** one neuron: **bias**, **activation function**, **forward** update, **backward** gradient steps, links to neighbours.
- **OOP:** **strong encapsulation** (private fields); **composition** (`ActivationFunction`, `List<Link>`); **Tell, Don’t Ask** — `updateOutput`, `seedOutputDer`, `computeAndAccumulateInputDer`, `applyBiasUpdate`, etc.

### `com/playground/nn/Link.java`

- **Concepts:** weighted edge between two `Node`s; accumulates error derivative; **`applyWeightUpdate`** with regularization.
- **OOP:** encapsulation; **polymorphism** via **`regularization.crossesZero(...)`** for L1; no `if (type == L1)` in caller.

### `com/playground/nn/NeuralNetwork.java`

- **Concepts:** **`buildNetwork`**, **`forwardProp`**, **`backProp`**, **`updateWeights`**, iteration helpers.
- **OOP:** **static utility class** (`private` constructor) — algorithms only; **orchestration** over `Node`/`Link`; **composition** walking the graph; uses **`ErrorFunction`** (e.g. `SquaredError.INSTANCE`) polymorphically.

---

## Member 3 — data, features, datasets

### `com/playground/data/Example2D.java`

- **Concepts:** one training example: **x, y, label** in 2D input space.
- **OOP:** **`final` class**, **`private final` fields**, getters only — **immutable value object**.

### `com/playground/data/InputFeatures.java`

- **Concepts:** enum **`Feature`** with keys `x`, `y`; **`build(activeFeatures, x, y)`** builds input vector; **`fromKey`** parsing.
- **OOP:** **enum as class** — each constant holds a **`DoubleBinaryOperator`**; calling **`apply`** is **polymorphic** without `switch`; **`InputFeatures` is a `final` utility** (private constructor).

### `com/playground/data/datasets/DataGenerator.java`

- **Concepts:** abstract **`generate(n, noise, rng)`**, **`getKey`**, **`isRegression`**.
- **OOP:** **abstract class**; **`protected static` helpers** (`randUniform`, …) for subclasses — **inheritance + reuse**.

### `com/playground/data/datasets/CircleDataset.java`, `XorDataset.java`, `GaussianDataset.java`, `SpiralDataset.java`

- **Concepts:** classification dataset recipes.
- **OOP:** **concrete `final` subclasses** of **`DataGenerator`**.

### `com/playground/data/datasets/PlaneRegressionDataset.java`, `GaussianRegressionDataset.java`

- **Concepts:** regression surfaces / noise.
- **OOP:** same inheritance pattern; **`final` classes**.

### `com/playground/data/datasets/DatasetRegistry.java`

- **Concepts:** maps string keys to `DataGenerator` instances; **`byKey(String)`**.
- **OOP:** static factory/registry (parallel to `Activations`, `Regularizations`); **ConfigurationException** on bad keys.

---

## Member 4 — exceptions, JSON, wrap-up

### `com/playground/exceptions/PlaygroundException.java`

- **Concepts:** abstract base with **`httpStatus`** and message; **`getHttpStatus()` is `final`**.
- **OOP:** **inheritance from `RuntimeException`**; **abstraction** — concrete subclasses supply status in constructor.

### `com/playground/exceptions/ConfigurationException.java`

- **Concepts:** bad user/config input → **HTTP 400**.
- **OOP:** **is-a** `PlaygroundException`; overloaded constructors with **cause** chaining.

### `com/playground/exceptions/NotFoundException.java`

- **Concepts:** missing resource → **HTTP 404**; base for “not found” family.

### `com/playground/exceptions/SessionNotFoundException.java`

- **Concepts:** unknown session id.
- **OOP:** **multi-level inheritance** — extends **`NotFoundException`** → ... → **`RuntimeException`**.

### `com/playground/exceptions/TrainingException.java`

- **Concepts:** training-time failure → **HTTP 500**; often wraps inner **`RuntimeException`**.

### `com/playground/util/Json.java`

- **Concepts:** minimal **encoder/decoder** for maps/lists/numbers/strings/booleans used by the API.
- **OOP:** **`final` utility class**; recursion over **`Map<?, ?>`** / **`List<?>`** — **generics**; no reflection libraries — shows **separation** of transport encoding from domain.

### Closing slide ideas (any member)

- **Single table:** Encapsulation → `Node`/`Link`/`Session`; Inheritance → activations, regularizers, datasets, exceptions; Polymorphism → `ActivationFunction`, `crossesZero`, `Trainable`, `PlaygroundException`; Abstraction → interfaces + abstract classes; Composition → `Session`, `ApiServer`.
- **Mention:** zero Maven/Gradle dependencies — pure JDK demonstrates OOP without framework noise.

---

## Quick reference — OOP term → where to point in code

| OOP / Java concept | Example location |
| ------------------ | ---------------- |
| Abstract class | `ActivationFunction`, `RegularizationFunction`, `DataGenerator`, `PlaygroundException` |
| Interface | `DifferentiableFunction`, `ErrorFunction`, `Trainable` |
| Enum class | `InputFeatures.Feature`, `Session.Problem` |
| Inheritance (IS-A) | `TanhActivation extends ActivationFunction`; `CircleDataset extends DataGenerator`; `SessionNotFoundException extends NotFoundException` |
| Polymorphism (dynamic dispatch) | `activation.output(...)` in `Node`; `crossesZero` in `Link`; `catch (PlaygroundException pe)` in `ApiServer` |
| Encapsulation | Private fields + methods on `Node`, `Link`, `Session` |
| Composition (HAS-A) | `Session` has network, datasets, functions; `Node` has `ActivationFunction` and `Link`s |
| Static factory / registry | `Activations.byKey`, `Regularizations.byKey`, `DatasetRegistry.byKey` |
| Singleton (stateless) | `SquaredError.INSTANCE` |
| Method overloading | `Session.trainOneEpoch(...)` vs `trainOneEpoch()` |
| Custom exceptions + HTTP | `PlaygroundException` hierarchy + `ApiServer.dispatch` |
| `final` | Concrete activations/datasets; `Example2D`; `getHttpStatus()`; many fields |
| Generics | `Map<String, Session>`, `List<List<Node>>`, `Json` traversal |
| try-with-resources | `ApiServer.readBody` |

---

## Related project docs

- Deeper academic mapping of OOP principles: **`backend/OOP_DESIGN.md`**
- How to run and API overview: **`backend/README.md`**

---

*Document version: generated for team presentations — align slide decks with the four-member themes above to minimize overlap and maximize coverage.*
