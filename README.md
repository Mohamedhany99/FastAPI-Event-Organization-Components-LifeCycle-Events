# ⚡ Energy Operations Technical Challenge 

## Context
The Energy Operations Challenge is a **FastAPI-based application** for managing utility contracts.
In this challenge, you will build a system that can handle events for different contract components and track their timelines.


## Contract Structure
The contract structure is minimal and contains a contract number, list of components and a creation date.
In addition, each contract is made up of multiple components, which allow for a flexible and more personalized configuration.
```json
{
  "contract_number": "1234",
  "created_at": "2024-01-01T00:00:00",
  "components": ["energy_supply", "battery_optimization", "heatpump_optimization"]
}
```

## Component Structure
Each component represents a functional module of a contract with a start and end period that can be tracked via events.
Components have the following rules:
* Each component has a start and end date, set via events.
* A component cannot end before it starts.
* A component cannot be restarted once terminated, meaning no new start/end period allowed after termination.
* Only the following components are supported:
  * * `energy_supply`
  * * `battery_optimization`
  * * `heatpump_optimization`


---

## Event Structure

Events represent actions on components and are used to build their timelines.
Events have the following rules:
* Events are processed in order based on `created_at`.
* Events for not existing contracts, should be rejected.
* Start event: If already exists, overwrites the existing start date.
* Start event that comes after the end event should be rejected.
* End event: If already exists, overwrites the existing the end date.
* End event without a start event should be rejected.
* Supported events:
  * * `supply_energy_start`
  * * `supply_energy_end`
  * * `battery_optimization_start`
  * * `battery_optimization_end`
  * * `heatpump_optimization_start`
  * * `heatpump_optimization_end`


```json
{
  "type": "module_action",
  "created_at": "2024-02-01T00:00:00",
  "create_at": "YYYY-MM-DD"
}
```

## Example Events

```json
[
    {"type": "supply_energy_start", "contract_number": "1234", "date": "2024-12-01"},
    {"type": "supply_energy_end", "contract_number": "1234", "date": "2024-12-31"},
    {"type": "battery_optimization_start", "contract_number": "1234", "date": "2024-03-03"},
    {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-04-04"},
    {"type": "heatpump_optimization_start", "contract_number": "1234", "date": "2025-03-03"},
    {"type": "heatpump_optimization_end", "contract_number": "1234", "date": "2025-04-04"},
    {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-02-01"},
    {"type": "supply_energy_start", "contract_number": "1234", "date": "2024-12-01"},
    {"type": "supply_energy_start", "contract_number": "9999", "date": "2024-12-01"},
    {"type": "battery_optimization_start", "contract_number": "1234", "date": "2024-03-15"},
    {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-04-15"},
    {"type": "heatpump_optimization_end", "contract_number": "1234", "date": "2024-04-01"}
]
```

---
## API Endpoints

Note: endpoints for contract handling (POST, GET, DELETE) are already implemented and can be used when working with events.


### 📌 `POST /event`
Imports a single event into the system.

#### Input JSON Example
```json
{
  "type": "battery_optimization_start",
  "contract_number": "1234",
  "date": "2024-03-03",
  "created_at": "2024-03-03T10:00:00"
}
```

#### ✅ Successful Response
```json
{
  "status": "accepted",
  "message": "Event processed successfully."
}
```

#### ❌ Error Response Example
```json
{
  "status": "rejected",
  "message": "End event cannot occur before start event."
}
```

### 📌 `GET /{contract_number}/contract_timeline`
Retrieves the timeline of all components for a contract.

#### ✅ Successful Response Example
```json
{
  "contract_number": "1234",
  "components": {
    "energy_supply": { "start": "2024-12-01", "end": "2024-12-31" },
    "battery_optimization": { "start": "2024-03-03", "end": null }
  }
}
```

#### ❌ Error Response Example
```json
{
  "status": "error",
  "message": "Contract 9999 not found."
}
```


---

## Acceptance criteria

1. **Successful execution**
   * The project should run successfully on a local machine.
   * Start/end periods for each component must be tracked correctly.
   * Invalid or unsupported scenarios should be detected and rejected with a meaningful error response.
   * The database may be adapted or extended to support the feature requirements.

2. **Expose API endpoints:**
   * See specifications above, in `API Endpoints` section.

3. **Model Contract**
    * A `Contract` entity must be created and persisted in the database.
    * Must support component lifecycle tracking.

4. **Extend unit tests:**
   * Extend unit tests to cover the new features.
   * Include tests for valid, invalid and edge-case scenarios.
   * Implementation of unit tests for already provided contract endpoints is optional.


---


## 🚀 Project Setup

### Project Information

* Python 3.12
* FastAPI
* Poetry
* SQLite
* Pytest


### 1️⃣ Install & Configure Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.in-project true
```

### 2️⃣ Install Dependencies
```bash
poetry install
```

### 3️⃣ Run the Application
- **Terminal**:
```bash
poetry run uvicorn app.main:app --reload
```

### 5️⃣ Access API Docs
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
