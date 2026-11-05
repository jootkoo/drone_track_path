
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# Crazyflie radio address
URI = "radio://0/80/2M/E7E7E7E7E7"

# Flight settings
FLIGHT_HEIGHT = 0.4    # Meters
MOVE_DISTANCE = 0.15   # Meters
MOVE_SPEED = 0.10      # Meters per second
LAND_SPEED = 0.10      # Meters per second

# Start with movement disabled to test landing first
ENABLE_MOVEMENT = True

flow_detected = Event()


def flow_callback(name, value):
    if int(value) == 1:
        flow_detected.set()


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(
        URI, cf=Crazyflie(rw_cache="./cache")
    ) as scf:

        print("Connected to Crazyflie!")

        # Check Flow Deck
        scf.cf.param.add_update_callback(
            group="deck",
            name="bcFlow2",
            cb=flow_callback
        )

        if not flow_detected.wait(timeout=5):
            raise RuntimeError("Flow Deck not detected!")

        print("Flow Deck detected.")

        # Arm the drone
        scf.cf.supervisor.send_arming_request(True)
        time.sleep(1)

        mc = MotionCommander(
            scf,
            default_height=FLIGHT_HEIGHT
        )

        try:
            # Take off
            print("Taking off...")
            mc.take_off(velocity=0.15)
            time.sleep(2)

            if ENABLE_MOVEMENT:
                # Move forward
                print("Moving forward...")
                mc.forward(
                    MOVE_DISTANCE,
                    velocity=MOVE_SPEED
                )
                mc.stop()
                time.sleep(1)

                # Move backward
                print("Moving backward...")
                mc.back(
                    MOVE_DISTANCE,
                    velocity=MOVE_SPEED
                )
                mc.stop()
                time.sleep(1)

            print("Hovering...")
            mc.stop()
            time.sleep(2)

        finally:
            print("Landing...")
            try:
                mc.land(velocity=LAND_SPEED)
            finally:
                scf.cf.supervisor.send_arming_request(False)

    print("Flight sequence finished.")


if __name__ == "__main__":
    main()
