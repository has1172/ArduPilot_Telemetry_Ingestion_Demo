# ArduPilot_Telemetry_Ingestion_Demo
Dynamic schema registry utilizing PyMAVLink to normalize version-drift in ArduPilot .bin logs. Prepares messy, real-world telemetry data for Physics-Informed Neural Networks (PINNs). GSoC 2026 Proof-of-Concept.


![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyMAVLink](https://img.shields.io/badge/PyMAVLink-Supported-success)
![GSoC 2026](https://img.shields.io/badge/GSoC-2026_Candidate-orange)

## 📌 Project Overview
This repository serves as a proof-of-concept for handling real-world, noisy ArduPilot `.bin` flight logs. It is designed as the foundational data ingestion layer for the **GSoC 2026: AI-Assisted Log Diagnosis & Root-Cause Detection** project.

A common pitfall in training AI models for log diagnosis is the over-reliance on clean, simulated (SITL) data. When these models face real-world forum crash logs, they often fail due to sensor noise and **version drift** (e.g., older logs using `PIDR.Err` while newer logs use `ATT.ErrRP`). 

This project solves that bottleneck by implementing a **Dynamic Schema Registry** that standardizes telemetry ingestion before it ever reaches the machine learning model.

## 🏗️ Architecture: The Dynamic Schema Registry
Instead of hardcoding parameter lookups that break across ArduPilot firmware versions, this ingestion engine maps abstract engineering concepts to a fallback dictionary of version-specific parameters.

### The Pipeline:
1. **Ingestion:** Parses raw `.bin` logs using `PyMAVLink`.
2. **Dynamic Mapping:** Scans messages (ATT, BATT, PIDR) and dynamically resolves attribute names based on the highest-priority available field in the schema.
3. **Normalization:** Converts variable parameter states into a standardized, time-series feature matrix.
4. **AI-Ready Output:** Outputs clean, normalized data ready for sequential ML models (like LSTMs or Physics-Informed Neural Networks).

## 🚀 Usage
To run the schema registry test locally:

1. Clone this repository.
2. Ensure you have `pymavlink` installed:
   ```bash
   pip install pymavlink
