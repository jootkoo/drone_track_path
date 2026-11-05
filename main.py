
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

# Radio connection from your Crazyflie Client
URI = "radio://0/80/2M/E7E7E7E7E7"


def main():
    # Initialize the Crazyradio communication drivers
    cflib.crtp.init_drivers()

    print("Connecting to Crazyflie...")

    # Establish a connection to the drone
    with SyncCrazyflie(
        URI, cf=Crazyflie(rw_cache="./cache")
    ) as scf:

        print("Successfully connected!")

        # Configure battery voltage logging
        log_config = LogConfig(
            name="Battery",
            period_in_ms=500
        )

        log_config.add_variable("pm.vbat", "float")

        # Receive 10 battery measurements
        with SyncLogger(scf, log_config) as logger:
            for count, entry in enumerate(logger):
                timestamp, data, logconf = entry

                voltage = data["pm.vbat"]

                print(f"Battery: {voltage:.2f} V")

                if count >= 9:
                    break

    print("Disconnected safely.")


if __name__ == "__main__":
    main()
