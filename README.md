# MDLBEEWS: Modular Deep Learning Based Earthquake Early Warning System

## Description

MDLBEEWS is a modular deep learning-based earthquake early warning system designed to provide real-time alerts and information about seismic activities. It leverages advanced machine learning techniques to analyze seismic data and predict potential earthquakes, enabling timely responses to mitigate risks and enhance safety.

### Developer

- Adi Wibowo – [bowo.adi@live.undip.ac.id](mailto:bowo.adi@live.undip.ac.id)
- Arjuna Wahyu Kusuma – [arjuna.kusuma@bmkg.go.id](mailto:arjuna.kusuma@bmkg.go.id)

### Table of Contents
- [Installation](#installation)
- [How To Run](#how-to-run)
- [Our Test](#our-test)
- [License](#license)
- [Citation](#citation)

## Installation
To install MDLBEEWS, follow these steps:
1. Install Docker
    - For Windows, follow the [Docker Desktop for Windows installation guide](https://docs.docker.com/desktop/windows/install/).
    - For Linux, follow the [Docker Engine installation guide](https://docs.docker.com/engine/install/).
    - For macOS, follow the [Docker Desktop for Mac installation guide](https://docs.docker.com/desktop/mac/install/).

2. Install Docker Compose
    - For Windows and macOS, Docker Compose is included with Docker Desktop.
    - For Linux, follow the [Docker Compose installation guide](https://docs.docker.com/compose/install/).

3. Clone the repository:
   ```bash
   git clone https://github.com/ArjunaWahyu/paper-eews.git
   cd paper-eews
   ```

## How To Run
1. You can run the system using Docker Compose with the following command:
    ```bash
    docker-compose up -d
    ```

2. This is generally used to run the system in detached mode, allowing it to run in the background. If you want to specify a configuration file, you can use:
    ```bash
    docker-compose -f <configuration file> up -d
    ```
    You can test the system using different Docker Compose configuration files. Replace `<configuration file>` with the desired file name. For example:

    ```bash
    docker-compose -f docker-compose-1-1.yml up -d
    ```

    The following table lists the available test cases and their corresponding configuration files. Each test case is designed to evaluate different aspects of the system, such as data processing methods, load balancing, multi-container setups, and WebSocket implementations.

    ### Test Cases of Parallel Data Processing on Data Provider

    Test cases for parallel data processing on the data provider are designed to evaluate the system's ability to handle multiple data processing techniques simultaneously. Each configuration file represents a different approach to data processing, allowing for comprehensive testing and comparison.

    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-1-1.yml`    | Single-threaded data provider                      |
    | `docker-compose-1-2.yml`    | Multi-process data provider                        |
    | `docker-compose-1-3.yml`    | Multi-threaded data provider                       |
    | `docker-compose-1-4.yml`    | Hybrid (multi-threading and multi-processing)      |

    ### Test Cases of NGINX as a Load Balancer for Kafka Broker

    Test cases for NGINX as a load balancer for Kafka brokers are designed to evaluate the system's ability to distribute incoming traffic across multiple Kafka broker instances. Each configuration file represents a different approach to load balancing, allowing for comprehensive testing and comparison.

    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-2-1.yml`    | Kafka as broker and load balancer                  |
    | `docker-compose-2-2.yml`    | Kafka with NGINX load balancer                     |

    ### Test Cases of Multi-Container Execution in Data Archiving and Seismic Detection

    Test cases for multi-container execution in data archiving and seismic detection are designed to evaluate the system's ability to run multiple instances of data archivers and P wave detectors. Each configuration file represents a different number of instances, allowing for comprehensive testing and comparison.

    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-3-1.yml`    | 1 Data Archiver                                    |
    | `docker-compose-3-2.yml`    | 2 Data Archivers                                   |
    | `docker-compose-3-3.yml`    | 3 Data Archivers                                   |
    | `docker-compose-3-4.yml`    | 4 Data Archivers                                   |
    | `docker-compose-3-5.yml`    | 5 Data Archivers                                   |
    | `docker-compose-3-6.yml`    | 2 P Wave Detectors                                 |
    | `docker-compose-3-7.yml`    | 3 P Wave Detectors                                 |
    | `docker-compose-3-8.yml`    | 4 P Wave Detectors                                 |
    | `docker-compose-3-9.yml`    | 5 P Wave Detectors                                 |

    ### Test Cases of WebSocket Implementation Using Express.js and FastAPI

    Test cases for WebSocket implementation using Express.js and FastAPI are designed to evaluate the system's ability to handle real-time communication between clients and servers. Each configuration file represents a different number of clients, allowing for comprehensive testing and comparison.
    
    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-4-1.yml`    | 1 Express.js client and 1 FastAPI client           |
    | `docker-compose-4-2.yml`    | 5 Express.js clients and 5 FastAPI clients         |

## Our Test

### Performance Analysis of Parallel Data Processing on Data Provider

Based on the test results, the Multiprocessing model delivered the best performance with the lowest latency (2.955 seconds), CPU usage of 44.50%, and memory usage of 476 MB, remaining stable throughout the testing. In contrast, the Sequential and Multithreading models experienced crashes due to limitations in handling parallel execution and resource contention.

| Scenario                         | Data Delay (seconds) | CPU Usage (%) | Memory Usage (MB) | Notes                                    |
|----------------------------------|----------------------|---------------|-------------------|------------------------------------------|
| Sequential                       | None                 | None          | None              | 40 minutes delay start, crash occurs     |
| Multithreading                   | 3.150                | 31.24         | 112               | Crash occurs when there are many threads |
| Multiprocessing                  | **2.955**            | **44.50**     | 476               | **Stable**                               |
| Multiprocessing + Multithreading | 4.768                | 62.50         | 600               | **Stable**                               |

### Performance Analysis of NGINX as a Load Balancer for Kafka Broker

### Performance Analysis of Multi-Container Execution in Data Archiving and Seismic Detection

### Performance Analysis of WebSocket Implementation Using Express.js and FastAPI


## LICENSE
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation
