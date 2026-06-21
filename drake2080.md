# Drake — The 80/20

The ~20% of pydrake that covers ~80% of what you'll actually touch in the
Tedrake (underactuated / manipulation) context. Learn these deeply; the rest is lookup.

> Mental model: **decisions come from your head, syntax comes from reference.**
> Looking up API signatures is not a learning failure — it's how the tool is used.

---

## 1. MultibodyPlant / SceneGraph
The core. Loads URDF/SDFormat models; computes mass matrix, Coriolis, gravity, contact.
- `AddMultibodyPlantSceneGraph(builder, time_step)`
- `plant.CalcMassMatrix`, `CalcBiasTerm`, `CalcGravityGeneralizedForces`, `MakeActuationMatrix`
- SceneGraph handles geometry / collision queries.

You'll instantiate these in nearly every notebook.

## 2. Systems framework (Diagram / System / Context)
Drake is a block-diagram simulator.
- `DiagramBuilder`, `builder.AddSystem(...)`, `builder.Connect(...)`, `builder.Build()`
- **The Context holds all state. Systems are stateless — state lives in the context.**
  - `plant.GetMyContextFromRoot`, `SetPositions`, `GetPositions`
- The diagram is the *wiring*; the context is the *values*. Two separate phases.

> Misunderstanding context-vs-system is the #1 beginner stumble. Burn this in early.

## 3. Simulator
- `Simulator(diagram)`, `simulator.AdvanceTo(t)`, `set_target_realtime_rate(...)`
- Integrator settings matter once contact makes things stiff.

## 4. Ports / LeafSystem
Writing your own controller as a `LeafSystem`:
- `DeclareVectorInputPort`, `DeclareVectorOutputPort`
- How you inject a custom control law into a diagram. Pairs with cart-pole / LQR work.

## 5. MathematicalProgram
Drake's optimization frontend.
- `prog.NewContinuousVariables`, `AddCost`, `AddConstraint`, `Solve`
- Backs trajectory optimization, IK, and QP-based controllers.
- `InverseKinematics` is a convenience wrapper on top.

## 6. Controllers library
- `LinearQuadraticRegulator(plant, context, Q, R)`
- `InverseDynamicsController`, `PidController`
- The LQR call maps directly to the controls/estimation curriculum.

## 7. Meshcat visualization
- `StartMeshcat()` (prints a localhost:7000 URL — open it in the browser)
- `MeshcatVisualizer.AddToBuilder(builder, scene_graph, meshcat)`
- How you see anything.

## 8. Geometry / pose math
- `RigidTransform`, `RotationMatrix`, `RollPitchYaw`
- Constant companions. Same SE(3) bookkeeping as gimbal/galvo pose work.

---

## The long tail (defer — look up when needed)
- Hydroelastic contact internals
- Solver backend tuning (SNOPT / IPOPT)
- `SpatialInertia` construction from scratch
- Manipulation perception stacks (point cloud → grasp)
- Custom collision filtering

---

## One-line takeaway
Internalize **System / Context / Diagram + MultibodyPlant + MathematicalProgram**,
and the rest is lookup.

---

# Underactuated — The 80/20

Thin scaffolding on top of Drake from Tedrake's MIT course. Once you know what each
piece does, it gets out of your way.

> Mental model: **`underactuated` finds your models and configures your environment.
> Drake does the actual work.**

---

## 1. `running_as_notebook`
A boolean. `True` inside Jupyter/Deepnote, `False` when running as a plain `.py`.

Used to gate interactive loops:
```python
if running_as_notebook:
    while meshcat.GetButtonClicks("Stop") < 1:
        simulator.AdvanceTo(...)
else:
    simulator.AdvanceTo(5.0)   # just run and exit
```

You'll see this pattern in almost every notebook. When running locally, the `else`
branch fires — no hanging button-wait.

## 2. `ConfigureParser`
Sets up the URDF/SDFormat search paths so `Parser` can find the course's bundled
models (cart-pole, acrobot, double pendulum, etc.) by short name.

```python
parser = Parser(plant)
ConfigureParser(parser)
parser.AddModelsFromUrl("package://underactuated/models/cartpole.urdf")
```

Without this, `Parser` won't know where the course model files live and will throw
a file-not-found error. Call this at diagram setup time.

## 3. `MeshcatSliders` (from `underactuated.meshcat_utils`)
Adds interactive sliders to the Meshcat browser UI — useful for tuning parameters
(gains, setpoints) live without restarting the simulation.

```python
from underactuated.meshcat_utils import MeshcatSliders
sliders = MeshcatSliders(meshcat, {"Q": (0.1, 100.0, 1.0)})
```

Reach for it when you want interactive tuning; not needed just to get things running.

---

## The long tail (defer — look up when needed)
- `underactuated.jupyter_utils` — notebook display helpers, irrelevant outside Jupyter
- `underactuated.scenarios` — pre-built diagram factories for course homeworks
- `underactuated.plot_utils` — phase portrait / trajectory plot helpers

---

## One-line takeaway
`underactuated` gives you **`ConfigureParser`** (finds the models) and
**`running_as_notebook`** (gates interactive behavior). That's 90% of why it's imported.