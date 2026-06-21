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


if __name__ == "__main__":
    meshcat = StartMeshcat()
    print(f"Open Meshcat at: {get_meshcat_url()}")
    input("Press Enter when the browser is open...")
    cartpole_demo(meshcat)

# 1. build plant + scene_graph
# 2. load cart-pole URDF via Parser
# 3. set upright, FixValue(0), Linearize -> A,B
# 4. LQR(Q,R) -> controller
# 5. wire diagram: plant->controller->plant
# 6. simulate from upright + noise
