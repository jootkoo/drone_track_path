
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

URI = "radio://0/80/2M/E7E7E7E7E7"

cflib.crtp.init_drivers()

with SyncCrazyflie(
    URI, cf=Crazyflie(rw_cache="./cache")
) as scf:

    # Verify that the Flow Deck V2 is detected
    flow = scf.cf.param.get_value("deck.bcFlow2")

    if flow is None or int(flow) != 1:
        raise RuntimeError(
            "Flow Deck V2 not detected. Flight cancelled."
        )

    print("Flow Deck detected.")

    # Arm the drone
    scf.cf.supervisor.send_arming_request(True)
    time.sleep(1)

    try:
        # Automatically take off to 0.3 meters
        with MotionCommander(scf, default_height=0.3) as mc:
            print("Taking off...")
            time.sleep(10)
            print("Landing...")

        print("Flight complete.")

    finally:
        scf.cf.supervisor.send_arming_request(False)
