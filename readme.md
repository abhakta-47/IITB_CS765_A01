# Assignment 1: Simulation of a P2P Cryptocurrency Network

## Course: CS765
## Submitted By
### Santanu Sahoo (23M0777)
### Arnab Bhakta (23M0835)

Here's a concise `README.md` for your blockchain simulation project using discrete event simulation:

---

# Blockchain Simulation using Discrete Event Simulation

This project implements a **discrete-event simulator** to study the dynamics of a **P2P cryptocurrency network**. It models key components such as transaction generation, network topology, message latency, mining, and blockchain maintenance to analyze performance and behavior under different network conditions.

## 🚩 Problem Statement

We aim to simulate a blockchain-based cryptocurrency system where nodes (peers) differ in processing and network speeds. The simulator helps answer:

* How do mining rate and network delay affect fork rate and chain quality?
* How do slow peers and low-CPU peers contribute to the blockchain?
* What is the impact of varying block generation time (Tk) and transaction inter-arrival time (Ttx)?

## 🧠 High-Level Design

At a high level, the system is a **discrete-event simulator** that progresses based on a priority queue of events (e.g., transaction creation, block mining, block propagation).

* Each peer runs independently and may be designated as slow/fast and high/low CPU.
* Events are timestamped and processed in chronological order.
* The simulation collects statistics on fork rate, block acceptance, longest chain growth, and peer contribution.

## 🧩 Low-Level Design

Below is a breakdown of key files and their responsibilities:

### Simulation & Core Logic

* `DiscreteEventSim.py` – The main discrete event simulation engine.
* `simulation.py` – Sets up the simulation with parameters and runs scenarios.
* `config.py` / `config.json` – Contains simulation parameters (e.g., number of peers, Tk, Ttx).
* `logger.py` – Logging utility to trace simulation progress.

### Blockchain & Network Modeling

* `Block.py` – Defines the structure of a block.
* `Transaction.py` – Defines transactions.
* `BlockChainBase.py`, `BlockChainHonest.py`, `BlockChainSecret.py` – Different blockchain strategies (honest mining, secret attack, etc.).
* `network.py` – Simulates the P2P network with link speeds and message delays.
* `Link.py` – Models individual network links between peers.
* `Peer.py` – Represents a node (peer) in the network.
* `cases.py` – Defines experimental setups (e.g., different Tk/Ttx configurations).

### Output & Visualization

* `graphs.ipynb`, `playbook.ipynb` – Jupyter notebooks for visualizing results.
* `visualisation.py`, `visuallizationor` – Plots forks, longest chain, peer contribution.
* `results.json`, `results_filtered.json`, `summary.json`, `summaries.csv` – Simulation outputs and statistics.

## 📊 Example Scenarios

The project simulates multiple scenarios by varying:

* Block mining time `Tk`
* Transaction inter-arrival time `Ttx`
* Network delay vs block propagation time

### Observed Insights:

* When `Tk >> delay`, forks are rare.
* When `Tk ≈ delay`, forks increase.
* When `Tk < delay`, the chain quality deteriorates significantly.

## 📁 Folder Structure

```
.
├── simulation.py               # Main driver
├── DiscreteEventSim.py        # Event queue engine
├── BlockChain*.py             # Different blockchain policies
├── network.py / Link.py       # Network simulation
├── Peer.py, Block.py, Transaction.py
├── results.json / summary.json / summaries.csv
├── graphs/frames/plots        # Visual outputs
├── config.json / config.py
├── logger.py / logs
├── playbook.ipynb             # Analysis notebook
├── Report-01.pdf              # Full report with analysis
└── readme.md
```

## 🛠 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

## 🧪 Running the Simulation

```bash
python simulation.py --config config.json
```

Adjust simulation parameters in `config.json`.

## 📚 Report
* Course lectures and discrete event system references listed in `Report-01.pdf`.
