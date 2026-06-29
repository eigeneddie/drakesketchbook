# This is my local machine version of the deepnote
# notes from MIT course 6.832 

import subprocess
import numpy as np
from pydrake.all import(
   AddMultibodyPlantSceneGraph,
   ControllabilityMatrix,
   DiagramBuilder,
   Linearize,
   LinearQuadraticRegulator,
   MeshcatVisualizer,
   Parser,
   Simulator,
   StartMeshcat,
)

from underactuated import ConfigureParser
from underactuated.meshcat_utils import MeshcatSliders



def get_meshcat_url(port=7000):
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode().split()[0]
        return f"http://{ip}:{port}"
    except Exception:
        return f"http://localhost:{port}"


def cartpole_demo(meshcat):
    # STEP 1 [note 1]: Build the plant and scene graph (the physics world)
    builder = DiagramBuilder()
    plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=0.0)

    # STEP 2 [note 2]: Load the cart-pole URDF model into the plant
    parser = Parser(plant)
    ConfigureParser(parser)
    parser.AddModelsFromUrl("package://underactuated/models/cartpole.urdf")
    plant.Finalize()

    # STEP 3: Set up Meshcat visualization in 2D side view
    meshcat.Delete()
    meshcat.Set2dRenderMode(xmin=-2.5, xmax=2.5, ymin=-1.0, ymax=2.5)
    MeshcatVisualizer.AddToBuilder(builder, scene_graph, meshcat)

    # STEP 4 [note 5]: Wire up slider input — use arrow keys or drag in Meshcat controls
    print("Use the slider in the MeshCat controls (or arrow keys) to apply force to the cart.")
    meshcat.AddSlider(
        "u",
        min=-5,
        max=5,
        step=0.1,
        value=0.0,
        decrement_keycode="ArrowLeft",
        increment_keycode="ArrowRight",
    )
    force_system = builder.AddSystem(MeshcatSliders(meshcat, ["u"]))
    builder.Connect(
        force_system.get_output_port(), plant.get_actuation_input_port()
    )

    # STEP 5: Finalize the diagram (locks the wiring)
    diagram = builder.Build()

    # STEP 6 [note 6]: Create simulator and set initial state (x, theta, xdot, thetadot)
    simulator = Simulator(diagram)
    context = simulator.get_mutable_context()
    context.SetContinuousState([0, 1, 0, 0])

    # STEP 7 [note 6]: Run the simulation until the user clicks Stop in Meshcat
    simulator.set_target_realtime_rate(1.0)
    print("Press 'Stop Simulation' in MeshCat to continue.")
    meshcat.AddButton("Stop Simulation", "Escape")
    while meshcat.GetButtonClicks("Stop Simulation") < 1:
        simulator.AdvanceTo(simulator.get_context().get_time() + 1.0)

    meshcat.DeleteAddedControls()

def cartpole_balancing_example(meshcat):
    def UprightState():
        state = (0, np.pi, 0, 0)
        return state

    # STEP 3 [note 3]: Linearize around the upright and check controllability
    def Controllability(plant):
        context = plant.CreateDefaultContext()
        plant.get_actuation_input_port().FixValue(context, [0])
        plant.SetPositionsAndVelocities(context, UprightState())

        linearized_plant = Linearize(
            plant,
            context,
            input_port_index=plant.get_actuation_input_port().get_index(),
            output_port_index=plant.get_state_output_port().get_index(),
        )
        print(linearized_plant.A())
        print(linearized_plant.B())
        print(
            f"The singular values of the controllability matrix are: {np.linalg.svd(ControllabilityMatrix(linearized_plant), compute_uv=False)}"
        )

    # STEP 4 [note 4]: Design LQR controller around the upright
    def BalancingLQR(plant):
        context = plant.CreateDefaultContext()
        plant.get_actuation_input_port().FixValue(context, [0])
        plant.SetPositionsAndVelocities(context, UprightState())

        Q = np.diag((10.0, 10.0, 1.0, 1.0))
        R = np.array([1])

        # MultibodyPlant has many (optional) input ports, so we must pass the
        # input_port_index to LQR.
        return LinearQuadraticRegulator(
            plant,
            context,
            Q,
            R,
            input_port_index=plant.get_actuation_input_port().get_index(),
        )

    # STEP 1 [note 1]: Build plant and scene graph
    builder = DiagramBuilder()
    plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=0)

    # STEP 2 [note 2]: Load cart-pole URDF
    parser = Parser(plant)
    ConfigureParser(parser)
    parser.AddModelsFromUrl("package://underactuated/models/cartpole.urdf")
    plant.Finalize()

    Controllability(plant)

    # STEP 5 [note 5]: Wire diagram: plant -> LQR controller -> plant
    controller = builder.AddSystem(BalancingLQR(plant))
    builder.Connect(plant.get_state_output_port(), controller.get_input_port(0))
    builder.Connect(controller.get_output_port(0), plant.get_actuation_input_port())

    # Setup visualization
    meshcat.Delete()
    meshcat.Set2dRenderMode(xmin=-2.5, xmax=2.5, ymin=-1.0, ymax=2.5)
    MeshcatVisualizer.AddToBuilder(builder, scene_graph, meshcat)

    diagram = builder.Build()

    # STEP 6 [note 6]: Simulate from upright + noise, 5 random trials
    simulator = Simulator(diagram)
    context = simulator.get_mutable_context()
    plant_context = plant.GetMyMutableContextFromRoot(context)

    simulator.set_target_realtime_rate(1.0)
    for i in range(5):
        context.SetTime(0.0)
        plant.SetPositionsAndVelocities(
            plant_context,
            UprightState() + 0.1 * np.random.randn(4,),
        )
        simulator.Initialize()
        simulator.AdvanceTo(5.0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cartpole", action="store_true", help="Manual teleop with slider")
    group.add_argument("--controlled", action="store_true", help="LQR auto-balancing")
    args = parser.parse_args()

    np.set_printoptions(formatter={"float": lambda x: "{0:0.4f}".format(x)})
    meshcat = StartMeshcat()
    print(f"Open Meshcat at: {get_meshcat_url()}")
    input("Press Enter when the browser is open...")

    if args.cartpole:
        cartpole_demo(meshcat)
    elif args.controlled:
        cartpole_balancing_example(meshcat)

# 1. build plant + scene_graph
# 2. load cart-pole URDF via Parser
# 3. set upright, FixValue(0), Linearize -> A,B
# 4. LQR(Q,R) -> controller
# 5. wire diagram: plant->controller->plant
# 6. simulate from upright + noise
