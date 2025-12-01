

# 🌀 **Unified Reality Agent (URA)**

### Multi-Agent System for Context-Aware Automation

*Powered by Python · Config-Driven · Offline + Real Mode Support*

---

## 📌 Overview

**Unified Reality Agent (URA)** is a modular, multi-agent AI system that unifies real-world context (weather, schedules, routines, reminders) with digital automation.
Instead of managing multiple apps, URA synchronizes your environment using specialized agents — all coordinated by a central Orchestrator.

This project is structured with clean architecture principles:

* Config-driven behavior
* Modular agents
* Pluggable tools
* Hot-reload configuration
* Offline (demo) and real modes
* Full logging and error handling

---

## 🚀 Features

### ✔ Multi-Agent Architecture

* **Weather Agent** – fetches real or mock weather
* **Planner Agent** – converts intent → task plan
* **Executor Agent** – executes planned steps
* **Orchestrator** – central controller coordinating everything

### ✔ Real + Demo Mode Support

* **Demo Mode:** Uses local `mock_data/` JSON
* **Real Mode:** Uses *Open-Meteo API* (free, no key required)

### ✔ Configuration Hot Reload

* Update `config/settings.json` while the app is running
* Watchdog automatically reloads and updates agents

### ✔ Clean, Professional Output

Formatted weather reports in terminal (black & white).

### ✔ Robust Engineering

* BOM-safe JSON loading
* Retry logic for network calls
* Input validation with Pydantic
* Full logging to console + file

---

## 📁 Project Structure

```
Capstone-URA/
│── agent/
│   ├── weather_agent.py
│   ├── planner_agent.py
│   ├── executor_agent.py
│   ├── orchestrator.py
│
│── tools/
│   └── mcp_weather_tool.py
│
│── utils/
│   ├── config_manager.py
│   ├── network_utils.py
│   ├── file_utils.py
│   └── logger.py
│
│── data/
│   └── mock_data/
│        └── weather.json
│
│── config/
│   └── settings.json
│
│── logs/
│── tests/
│── main.py
│── requirements.txt
│── README.md
│── .gitignore
```

---

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Capstone-URA.git
cd Capstone-URA
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

**Windows:**

```bash
venv\Scripts\Activate.ps1
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

The main configuration file is:

```
config/settings.json
```

It supports both real mode and demo mode.

### **Real Mode: Open-Meteo**

```json
"weather": {
  "geocoding_endpoint": "https://geocoding-api.open-meteo.com/v1/search",
  "forecast_endpoint": "https://api.open-meteo.com/v1/forecast",
  "timezone": "Asia/Kolkata",
  "units": "metric",
  "demo_data_path": "data/mock_data/weather.json",
  "timeout_seconds": 8,
  "max_retries": 2
}
```

### **Demo Mode**

Uses:

```
data/mock_data/weather.json
```

---

## ▶️ Running the System

### **Run in Demo Mode**

```bash
python main.py --mode demo --location "Rajkot"
```

### **Run in Real Mode**

```bash
python main.py --mode real --location "London"
```

---

## 🖥 Example Output (Real Mode)

```
-----------------------------------------
           WEATHER REPORT (REAL MODE)
-----------------------------------------
Location     : London, United Kingdom
Timestamp    : 2025-12-01T14:00

Temperature  : 11.2 °C
Humidity     : 72 %
Wind Speed   : 18.4 km/h
Summary      : Partly cloudy

-----------------------------------------
Source       : REAL
-----------------------------------------
```

---

## 🏗 Architecture Summary

### ✔ **Orchestrator**

Central system manager:

* Applies mode (demo/real)
* Initializes agents
* Loads + hot-reloads config
* Handles weather queries

### ✔ **Weather Agent**

* Calls MCP Weather Tool
* Normalizes output
* Supports demo + real mode

### ✔ **MCP Weather Tool**

* Open-Meteo integration
* Geocoding + weather
* Retry logic
* Timeout handling

### ✔ **Planner Agent**

Converts user intent to actionable tasks (simple stub for now).

### ✔ **Executor Agent**

Executes planned tasks (stub, can be extended to calendars, reminders, smart-home, etc.)

---

## 🔮 Roadmap

* Add Reminder Agent
* Add Calendar Agent
* Add Smart-Home Agent
* Add Conversation / LLM Agent
* Add FastAPI backend
* Add Web Dashboard
* Add SQLite or MongoDB persistent store
* Implement Planner → Executor → Tools real automation loop

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss what you’d like to add.

