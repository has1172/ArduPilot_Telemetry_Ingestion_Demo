import os
from pymavlink import mavutil

class PhysicsInformedDiagnostics:
    def __init__(self, log_path):
        self.log_path = log_path
        self.pwm_max_threshold = 1900  # Motors commanded to near absolute maximum
        self.climb_rate_threshold = -1.0 # Negative climb rate (drone is falling)

    def analyze_thrust_loss(self):
        print(f"[*] Initializing Physics-Based Diagnostic Engine for: {self.log_path}")
        print("[*] Scanning for Mechanical Thrust Loss signatures...")
        
        try:
            mlog = mavutil.mavlink_connection(self.log_path)
        except Exception as e:
            print(f"[!] Error opening log: {e}")
            return

        thrust_loss_flags = 0

        while True:
            # We need RCOU (Motor Outputs) and CTUN (Control Tuning / Altitude)
            msg = mlog.recv_match(type=['RCOU', 'CTUN'], blocking=False)
            if msg is None:
                break
            
            msg_type = msg.get_type()
            
            # Check Motor PWM Outputs
            if msg_type == 'RCOU':
                # Checking primary quadcopter/plane motor channels (C1 to C4)
                # Note: Depending on the specific vehicle frame, C1-C4 might be different, 
                # but this covers standard quadcopters and basic planes.
                motors = [msg.C1, msg.C2, msg.C3, msg.C4]
                
                if any(pwm > self.pwm_max_threshold for pwm in motors):
                    # Motor is maxed out. Now we check if the drone is actually climbing.
                    
                    # Look ahead for the nearest CTUN message to check climb rate
                    ctun_msg = mlog.recv_match(type='CTUN', blocking=False)
                    if ctun_msg and hasattr(ctun_msg, 'CRt'):
                        climb_rate = ctun_msg.CRt
                        
                        # PHYSICS CHECK: Motors maxed, but drone is falling
                        if climb_rate < self.climb_rate_threshold:
                            thrust_loss_flags += 1
                            print(f"[!] CRITICAL PHYSICAL ANOMALY: Thrust Loss Detected at timestamp {msg._timestamp}")
                            print(f"    -> Evidence: Motors maxed at {max(motors)} PWM, but climb rate is {climb_rate} m/s.")

        if thrust_loss_flags > 0:
            print(f"\n[X] DIAGNOSIS: Mechanical Failure / Thrust Loss. (Flags: {thrust_loss_flags})")
            print("[X] ACTION: Suppress ML sensor hallucinations (e.g., Compass Error). Physical failure overrides.")
        else:
            print("\n[*] No thrust loss signatures detected in this specific log section.")

if __name__ == "__main__":
    sample_log = r"C:\Users\HARSH\Desktop\AdruPilot GSoC 2026\sample_crash_log.bin" 
    
    if os.path.exists(sample_log):
        diagnostic = PhysicsInformedDiagnostics(sample_log)
        diagnostic.analyze_thrust_loss()
    else:
        print(f"[!] Please place '{sample_log}' in this directory to run the test.")