<!-- # Deep Learning-Based Earthquake Early Warning System (EEWS)

This repository contains the source code and architecture referenced in the research paper:

**Comparative Analysis of Technologies in Deep Learning Based Earthquake Early Warning System**  
Authors: Adi Wibowo, Arjuna Wahyu Kusuma, Satriawan Rasyid Purnama, Liem Roy Marcelino  
Affiliation: Department of Computer Science, Universitas Diponegoro

📄 [Link to Paper](https://doi.org/...) *(update this with actual link if available)*

---

# Table of Contents

- [Deep Learning-Based Earthquake Early Warning System (EEWS)](#deep-learning-based-earthquake-early-warning-system-eews)
  - [Table of Contents](#table-of-contents)
  - [Overview](#🧭-overview)
  - [Key Findings](#🧪-key-findings)
  - [Technologies Used](#🛠️-technologies-used)
  - [Repository Structure](#📁-repository-structure)
  - [Getting Started](#🚀-getting-started)
  - [Performance Evaluation](#📊-performance-evaluation)
  - [Code Availability](#🔗-code-availability)
  - [Citation](#📜-citation)
  - [Acknowledgments](#🙏-acknowledgments)
  - [Contact](#📬-contact)

## 🧭 Overview

This project presents a comparative analysis and optimization of distributed computing technologies for Earthquake Early Warning Systems (EEWS). It evaluates and integrates:

- **Multiprocessing** for data ingestion
- **Kafka & NGINX** for scalable message handling
- **Multi-container execution** for load-distributed components
- **Express.js** for real-time alert broadcasting via WebSocket

An optimized EEWS architecture is proposed, demonstrating a balance of speed, scalability, and resource efficiency.

---

## 🧪 Key Findings

| Module                    | Best Method             | Delay (s) | CPU (%) | Memory (MB) |
|--------------------------|-------------------------|-----------|---------|-------------|
| Data Ingestion           | Multiprocessing         | 2.955     | 44.50   | 476         |
| WebSocket Broadcasting   | Express.js (5 clients)  | 0.001452  | 13.38   | 96.05       |
| Message Broker           | Kafka (no NGINX)        | 0.006329  | -       | Higher      |

---

## 🛠️ Technologies Used

- **Languages**: Python, JavaScript (Node.js)
- **Frameworks**: TensorFlow, PyTorch, FastAPI, Express.js
- **Message Broker**: Apache Kafka
- **Load Balancer**: NGINX
- **Database**: MongoDB
- **Tools**: ObsPy, Docker, SeedLink

---

## 📁 Repository Structure

```
realtime_earthquake_detection/
├── data_provider/            # Data ingestion (ObsPy + SeedLink)
├── p_wave_detector/          # P-wave detection (TensorFlow model)
├── message_broker/           # Kafka + NGINX setup
├── archiver/                 # Data storage to MongoDB
├── location_detector/        # Hypocenter & magnitude estimation
├── websocket/                # Real-time WebSocket using Express.js
├── frontend/                 # Real-time visualization dashboard (optional)
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### Requirements

- Python 3.7+
- TensorFlow (GPU support)
- PyTorch 1.12.1
- CUDA Toolkit 11.3
- Docker & Docker Compose
- MongoDB

### Installation

```bash
git clone https://github.com/bowoadi/realtime_earthquake_detection.git
cd realtime_earthquake_detection
pip install -r requirements.txt
```

### Run with Docker

```bash
docker-compose up --build
```

---

## 📊 Performance Evaluation

Performance metrics were measured across:
- **Parallel data processing (Data Provider)**
- **Load balancing (Kafka with/without NGINX)**
- **Real-time communication (Express.js vs FastAPI)**
- **Scalability (Multi-container setup)**

All experimental data and results are detailed in the full paper.

---

## 🔗 Code Availability

- Repository: [https://github.com/bowoadi/realtime_earthquake_detection](https://github.com/bowoadi/realtime_earthquake_detection)
- Program Size: ~11.4 MB
- Programming Language: Python
- Contact: bowo.adi@live.undip.ac.id | +62 812-8804-6166

---

## 📜 Citation

```bibtex
@article{wibowo2025eews,
  title={Comparative Analysis of Technologies in Deep Learning Based Earthquake Early Warning System},
  author={Wibowo, Adi and Kusuma, Arjuna Wahyu and Purnama, Satriawan Rasyid and Marcelino, Liem Roy},
  journal={Computers & Geosciences},
  year={2025}
}
```

---

## 🙏 Acknowledgments

This project was supported by:

- **BMKG Indonesia** – for seismic data access
- **Dikti AI Centre & NVIDIA DGX A100** – for computational resources
- **Riset Kolaborasi Indonesia (RKI) – Universitas Diponegoro** – Grant No. 391-04/UN7.D2/PP/V/2023

---

## 📬 Contact

For further information or collaboration:

- Adi Wibowo – [bowo.adi@live.undip.ac.id](mailto:bowo.adi@live.undip.ac.id)
- Arjuna Wahyu Kusuma – [LinkedIn](https://www.linkedin.com/in/arjunawahyuks/) *(optional)* -->


# EEWS-Distributed

- [EEWS-Distributed](#eews-distributed)
  - [Introduction](#introduction)
  - [How to Run](#how-to-run)
  - [License](#license)
  - [Step-by-Step Procedure](#step-by-step-procedure)

## Introduction

This project is a deep learning-based Earthquake Early Warning System (EEWS) built on distributed computing principles. It is inspired by QuakeFlow and optimized for performance, low latency, and modularity. Key features include:

- Parallel data processing using **multiprocessing**
- Scalable messaging via **Kafka** and **NGINX**
- Real-time alert delivery via **Express.js WebSocket**
- Containerized modules using **Docker**

This repository evaluates and integrates several technologies to achieve efficient earthquake detection and alerting suitable for cloud or hybrid environments.

## How to Run

### Requirements

- Python >= 3.7
- Docker & Docker Compose
- TensorFlow-GPU
- MongoDB
- CUDA Toolkit 11.3

### Running the System

Clone and start the services:

```bash
git clone https://github.com/yourusername/eews-distributed.git
cd eews-distributed
docker-compose up --build
```

Alternatively, run each container individually if needed (e.g., for debugging or scaling).

## License

MIT License. See [`LICENSE`](./LICENSE) file for more information.

## Step-by-Step Procedure

**1. Data Flow Architecture**

- `data_provider_generator/`: Reads real-time seismic data (via ObsPy + SeedLink) and publishes to Kafka.
- `p_wave_detector/`: Detects P-wave onsets using TensorFlow models exposed via FastAPI.
- `loc_mag_detector/`: Estimates hypocenter and magnitude based on pick data.
- `data_saver/`: Archives waveform and result data to MongoDB.
- `api_server/` + `websocket/`: Broadcasts detection results to front-end in real-time using WebSocket (Express.js).

**2. Kafka & Load Balancing**

- `load_balancer/`: Configures NGINX as a reverse proxy and load balancer for Kafka partitions and FastAPI workers.

**3. Containerized Services**

Each component is modular and containerized, allowing independent scaling and updates:
- Kafka, MongoDB, and NGINX are deployed as services via `docker-compose.yml`.
- Modules communicate using Kafka topics (e.g., `trace_topic`, `p_wave_topic`, `result_topic`).

**4. Performance Summary (from Paper)**

| Component           | Optimal Method           | Delay    | CPU Usage | Memory Usage |
|--------------------|--------------------------|----------|-----------|---------------|
| Data Provider       | Multiprocessing           | 2.955 s  | 44.5%     | 476 MB        |
| WebSocket Broadcast | Express.js (5 clients)    | ~1.4 ms  | 13.38%    | 96 MB         |
| Kafka Load Balancer| Kafka-only vs NGINX trade-off | ~6 ms | varies     | lower memory with NGINX |

**5. Real-Time Testing**

Simulated data can be pushed to `trace_topic` and monitored via:
- Web-based dashboard (see `seismic_app/` or build your own)
- Kafka logs and MongoDB queries for validation

## Contact

If you use or extend this work, please cite the paper:

> Wibowo, A., Kusuma, A. W., Purnama, S. R., & Marcelino, L. R. (2025). Comparative Analysis of Technologies in Deep Learning Based Earthquake Early Warning System. *Computers & Geosciences*.
