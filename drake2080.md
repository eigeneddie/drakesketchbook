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