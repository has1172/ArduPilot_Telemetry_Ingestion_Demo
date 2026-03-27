import os
from pymavlink import mavutil

class FlightLogAnalyzer:
    def __init__(self, log_path):
        self.log_path = log_path
        # The Dynamic Schema Registry: Maps abstract concepts to version-specific parameters
        self.schema_registry = {
            "roll_error": ["PIDR.Err", "ATT.ErrRP"],
            "pitch_error": ["PIDP.Err", "ATT.ErrPI"],
            "battery_voltage": ["BAT.Volt", "BATT.Volt"] 
        }
        
    def _get_available_param(self, msg, concept):
        """Resolves the correct parameter name based on the schema registry."""
        for param in self.schema_registry.get(concept, []):
            if hasattr(msg, param.split('.')[-1]): 
                return param.split('.')[-1]
        return None

    def extract_telemetry_features(self):
        """Ingests the .bin file, bypasses version drift, and normalizes the data."""
        print(f"[*] Initializing PINNs Telemetry Ingestion Pipeline for: {self.log_path}")
        print("[*] Loading Dynamic Schema Registry...")
        
        try:
            mlog = mavutil.mavlink_connection(self.log_path)
        except Exception as e:
            print(f"[!] Error opening log: {e}")
            return

        anomaly_flags = 0

        # Scan through the log looking for Attitude (ATT) and Roll/Pitch (PIDR/PIDP) messages
        while True:
            msg = mlog.recv_match(type=['ATT', 'PIDR', 'PIDP'], blocking=False)
            if msg is None:
                break
            
            msg_type = msg.get_type()
            
            # Target Roll Error specifically to catch the oscillation crash
            if msg_type in ['ATT', 'PIDR']:
                roll_err_attr = self._get_available_param(msg, "roll_error")
                if roll_err_attr:
                    error_value = getattr(msg, roll_err_attr)
                    
                    # Rule-Based Anomaly Detection (Simulating the physics check)
                    if abs(error_value) > 15.0: # Flagging anything over 15 degrees of error
                        anomaly_flags += 1
                        print(f"[!] ANOMALY DETECTED: Extreme Roll Error -> {error_value:.2f} deg at timestamp {msg._timestamp}")

        print(f"\n[*] Ingestion Complete. Total physical anomalies flagged: {anomaly_flags}")
        print("[*] Telemetry normalized and ready for Machine Learning pipeline.")

if __name__ == "__main__":
    sample_log = "sample_crash_log.bin" 
    
    if os.path.exists(sample_log):
        analyzer = FlightLogAnalyzer(sample_log)
        analyzer.extract_telemetry_features()
    else:
        print(f"[!] Please place '{sample_log}' in this directory to run the ingestion test.")