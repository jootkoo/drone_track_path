
import time
import msvcrt  # Windows keyboard input

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# Crazyflie connection
URI = "radio://0/80/2M/E7E7E7E7E7"

# Flight settings
FLIGHT_HEIGHT = 0.35   # 35 cm
MOVE_DISTANCE = 0.10   # 10 cm per keypress
MOVE_SPEED = 0.10      # 0.1 meters/second
TURN_ANGLE = 15        # 15 degrees per keypress
LAND_SPEED = 0.10
MAX_FLIGHT_SECONDS = 30


def main():
    cflib.crtp.init_drivers()
    print("Connecting to Crazyflie...")
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache")) as scf:
        # Verify Flow Deck before flight
        flow = scf.cf.param.get_value("deck.bcFlow2")

        if flow is None or int(flow) != 1:
            raise RuntimeError("Flow Deck V2 not detected.")

        print("Connected! Flow Deck detected.")

        mc = MotionCommander(scf, default_height=FLIGHT_HEIGHT)

        flying = False
        takeoff_time = 0

        print("""
        ===== CRAZYFLIE CONTROLS =====

        T       Take off
        L       Land

        W       Forward
        S       Backward
        A       Left
        D       Right

        Q       Rotate left
        E       Rotate right

        H       Hover / stop movement
        X       Land and exit

        ==============================
        """)

        try:
            while True:
                # Automatic landing after 30 seconds
                if flying:
                    elapsed = time.monotonic() - takeoff_time

                    if elapsed >= MAX_FLIGHT_SECONDS:
                        print("Flight time limit reached.")
                        break

                # Wait for keyboard input
                if not msvcrt.kbhit():
                    time.sleep(0.05)
                    continue

                key = msvcrt.getwch().lower()

                if key == "t" and not flying:
                    print("Taking off...")

                    scf.cf.supervisor.send_arming_request(True)
                    time.sleep(0.5)

                    flying = True
                    mc.take_off(velocity=0.15)
                    takeoff_time = time.monotonic()

                    print("Hovering at 35 cm.")

                elif key == "l" and flying:
                    print("Landing...")
                    mc.land(velocity=LAND_SPEED)
                    flying = False

                elif key == "x":
                    print("Exiting...")
                    break

                elif not flying:
                    print("Press T to take off first.")

                elif key == "w":
                    print("Forward")
                    mc.forward(MOVE_DISTANCE, velocity=MOVE_SPEED)

                elif key == "s":
                    print("Backward")
                    mc.back(MOVE_DISTANCE, velocity=MOVE_SPEED)

                elif key == "a":
                    print("Left")
                    mc.left(MOVE_DISTANCE, velocity=MOVE_SPEED)

                elif key == "d":
                    print("Right")
                    mc.right(MOVE_DISTANCE, velocity=MOVE_SPEED)

                elif key == "q":
                    print("Rotate left")
                    mc.turn_left(TURN_ANGLE, rate=30)

                elif key == "e":
                    print("Rotate right")
                    mc.turn_right(TURN_ANGLE, rate=30)

                elif key == "h":
                    print("Hover")
                    mc.stop()

        finally:
            if flying:
                print("Landing before disconnect...")
                mc.stop()
                mc.land(velocity=LAND_SPEED)

        print("Disconnected safely.")


if __name__ == "__main__":
    main()
