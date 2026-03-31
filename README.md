# ArduPilot_Telemetry_Ingestion_Demo
This repository serves as a proof-of-concept for handling real-world, noisy ArduPilot `.bin` DataFlash flight logs. It is designed as the foundational data ingestion and preprocessing layer for the **GSoC 2026: AI-Assisted Log Diagnosis & Root-Cause Detection** project.

A common pitfall in training Machine Learning (ML) models for log diagnosis is the over-reliance on clean, simulated (SITL) data. When naive machine learning models are deployed against real-world forum crash logs, they frequently fail due to two critical bottlenecks:

1. **Parameter Version Drift:** ArduPilot is constantly evolving. Older logs rely on legacy parameter naming conventions (e.g., `PIDR.Err`), while newer logs use updated structures (e.g., `ATT.ErrRP`). Hardcoded ML pipelines break when fed historical data.
2. **Sensor Noise & ML Hallucinations:** Violent physical crashes create massive magnetic, inertial, and vibrational noise. Naive ML models often misinterpret this secondary noise, hallucinating sensor errors when the raw telemetry clearly indicates a primary mechanical failure.

This project solves these issues by implementing dynamic parameter resolution and a strict deterministic physics-filtering layer *before* the data ever reaches a machine learning classifier.


![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyMAVLink](https://img.shields.io/badge/PyMAVLink-Supported-success)
![GSoC 2026](https://img.shields.io/badge/GSoC-2026_Candidate-orange)


## 🧠 The Problem: ML Hallucinations vs. Physics-Informed Neural Networks (PINNs)

Traditional machine learning models (like Random Forests or standard LSTMs) operate as "black boxes" that learn purely from statistical data correlations. 

**The Compass Hallucination Example:**
Imagine a quadcopter experiences an ESC desync mid-flight. The drone loses thrust on one arm and violently tumbles out of the sky. As it spins uncontrollably, the magnetometer (compass) readings spike erratically due to the rapid rotation. If you feed this raw telemetry to a traditional ML model, it notices the massive compass variance right before the crash and incorrectly learns: *Compass spikes cause crashes.* When deployed, the AI will confidently misdiagnose the mechanical failure as a "Compass Error."

## The PINN Solution:

**Why Physics-Informed Neural Networks (PINNs)?**
Traditional machine learning models are "black boxes" that learn purely from data correlations. If you feed a traditional ML model a dataset of drone crashes, it might notice that the compass always spikes right before the crash. The model will incorrectly learn: *Compass spikes cause crashes.* In reality, the drone suffered a mechanical motor failure, started tumbling out of the sky, and the violent tumbling *caused* the compass spike. 

**What is a PINN?**
A Physics-Informed Neural Network (PINN) is an AI architecture where the laws of physics (kinematics, aerodynamics, thermodynamics) are hardcoded into the model's loss function or feature extraction layer. The model is penalized if it makes a prediction that violates real-world physics.

**Benefits for ArduPilot Diagnosis:**
* **Eliminates Hallucinations:** By looking at Motor PWM (`RCOU`) and Altitude (`CTUN`), the physics layer recognizes the drone is experiencing Thrust Loss. It overrides the ML model, preventing it from incorrectly blaming the compass.
* **Requires Less Training Data:** Because the model already "knows" basic kinematics, it doesn't need millions of SITL runs to figure out that drones cannot fly without thrust.
* **High Interpretability:** Instead of a black-box guess, the diagnosis can be traced directly back to specific physical telemetry timestamps.

---
By running the telemetry through the `physics_check.py` engine first, the system looks at the physical truth:
* **Motor PWM (`RCOU`):** Are the motors commanded to maximum output (>1900)?
* **Altitude (`CTUN.CRt`):** Is the climb rate deeply negative (the drone is falling)?

If motors are maxed but the drone is falling, the engine definitively flags a **Mechanical Thrust Loss**. It overrides the ML model, suppressing the compass noise and preventing the hallucination. This results in high interpretability—the diagnosis can be traced directly back to specific physical constraints, not a black-box guess.

## 🛠️ Core Pipeline Architecture

This pipeline handles the extraction, normalization, and physical verification of the `.bin` telemetry.

### 1. Dynamic Schema Registry (`analyzer.py`)
Instead of hardcoding parameter lookups that break across ArduCopter/ArduPlane firmware versions, this ingestion engine utilizes `pymavlink` to dynamically resolve telemetry.
* Maps abstract engineering concepts (e.g., "Roll Error") to a fallback dictionary.
* Scans incoming messages (`ATT`, `BATT`, `PIDR`) and dynamically resolves attribute names based on the highest-priority available field in the schema.
* Allows the tool to seamlessly ingest logs from ArduPilot 3.x and 4.x without requiring manual user configuration files.

### 2. Mechanical Physics Filtering (`physics_check.py`)
Executes rule-based physical constraints to isolate hardware failures from sensor noise. 
* Evaluates actuator outputs (`RCOU`) against expected vehicle kinematics (`CTUN`, `IMU`).
* Flags critical, undeniable physical anomalies (e.g., Thrust Loss, uncommanded extreme attitude variance) to serve as a ground-truth override for the downstream ML classifier.

### 3. AI-Ready Feature Matrix
Converts the variable parameter states into a standardized, physically-verified, time-series matrix. This prepares the data for sequential ML models without carrying over the noise of the crash dynamics.

## 🚀 Usage & Proof of Concept

You can test the physics-filtering logic directly in your browser without any local setup, or run it locally via CLI.

### Option 1: Live Browser Demo
Test the physics engine against an ArduPilot `.bin` log directly in Google Colab. This interactive environment handles the `pymavlink` dependencies and extracts the telemetry in the cloud.

[**Run the Interactive Diagnostics Colab Notebook Here**](https://colab.research.google.com/drive/1073K9Z8Er4FPNH9qkAkWG6XG5z1UK5go?usp=sharing)

### Option 2: Local CLI Execution
To run the ingestion and physics engine locally on your own machine:

1. Clone this repository.
2. Ensure you have Python 3.8+ and install the required dependencies:
   ```bash
   pip install pymavlink

(Note: The script currently expects a .bin file named sample_crash_log.bin in the root directory. You can swap this with your own flight logs to test the mechanical failure detection thresholds).

##👨‍💻 About the Author
Harsh Shah
Computer Science Engineering specializing in AI | Parul University

This architectural approach is heavily informed by my background in both physical drone hardware and large-scale data processing. I previously engineered "PARTH," a morphing quadcopter utilizing a Pixhawk flight controller, which required deep familiarity with raw telemetry, PID tuning, and ArduPilot C++ kinematics. Furthermore, the physics-informed anomaly detection approach utilized here is scaled down from Divya Dhrishti, a prior project where I successfully processed a dataset of over 3 million real-world Boeing 737 flight logs to isolate mechanical signatures from sensor noise.
