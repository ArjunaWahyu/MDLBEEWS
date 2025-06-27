# MDLBEEWS: Modular Deep Learning Based Earthquake Early Warning System

## Description

MDLBEEWS is a modular deep learning-based earthquake early warning system designed to provide real-time alerts and information about seismic activities. It leverages advanced machine learning techniques to analyze seismic data and predict potential earthquakes, enabling timely responses to mitigate risks and enhance safety. This software is designed to accelerate real-time seismic data processing to support earthquake early warning systems. Featuring a modular interface and containerization support, the system is easily deployable by geophysics researchers, disaster management agencies, and technology developers.

The software significantly enhances research and operational efficiency within earthquake early warning systems. By automating previously manual workflows, it enables real-time seismic data analysis within minutes. In addition to accelerating processes, the software also opens new opportunities for exploring machine learning-based topics that were previously inaccessible due to computational limitations.

MDLBEEWS is built on a foundation of modern technologies to deliver scalable, reliable, and high-performance earthquake early warning capabilities. The system leverages Docker for containerization, ensuring consistent deployment and simplified dependency management across platforms. Apache Kafka serves as the core message broker, enabling real-time, fault-tolerant streaming of seismic data between modules. NGINX is integrated as a load balancer to efficiently distribute traffic and optimize resource utilization. For real-time, bidirectional communication, the system employs WebSocket protocols implemented with Express.js and FastAPI, supporting low-latency delivery of alerts and updates. Currently, MDLBEEWS operates as a single-station system, processing seismic data from one sensor location at a time and does not yet support multi-station or networked deployments. 

### Contributors

- Adi Wibowo – [bowo.adi@live.undip.ac.id](mailto:bowo.adi@live.undip.ac.id)
- Arjuna Wahyu Kusuma – [arjunawahyukusuma@alumni.undip.ac.id](mailto:arjunawahyukusuma@alumni.undip.ac.id) (corresponding author)
- Satriawan Rasyid Purnama – [satriawanrasyid@live.undip.ac.id](mailto:satriawanrasyid@live.undip.ac.id)
- Liem, Roy Marcelino – [liemroym@alumni.undip.ac.id](mailto:liemroym@alumni.undip.ac.id)

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
   git clone https://github.com/ArjunaWahyu/MDLBEEWS.git
   cd MDLBEEWS
   ```

## Requirement 

<!-- add all requirement version from file requirement.txt in every folder -->


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

3. The table below outlines the available test cases along with their respective configuration files. Each test case includes detailed information and is intended to assess specific components of the system, such as data processing techniques, load balancing strategies, multi-container configurations, and WebSocket-based communication approaches.

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
    | `docker-compose-3-10.yml`   | 2 P Wave Detectors with Load Balancer              |
    | `docker-compose-3-11.yml`   | 3 P Wave Detectors with Load Balancer              |
    | `docker-compose-3-12.yml`   | 4 P Wave Detectors with Load Balancer              |
    | `docker-compose-3-13.yml`   | 5 P Wave Detectors with Load Balancer              |

    ### Test Cases of WebSocket Implementation Using Express.js and FastAPI

    Test cases for WebSocket implementation using Express.js and FastAPI are designed to evaluate the system's ability to handle real-time communication between clients and servers. Each configuration file represents a different number of clients, allowing for comprehensive testing and comparison.
    
    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-4-1.yml`    | Express.js                                         |
    | `docker-compose-4-2.yml`    | FastAPI                                            |

## Our Test

The experimental setup leverages high-performance hardware to ensure optimal computational efficiency and reliability. It features an Intel® Core™ i9-13900K processor, renowned for its exceptional processing capabilities, paired with 128 GB of memory to accommodate large-scale seismic datasets and intensive real-time computations. The system also integrates an NVIDIA GeForce RTX 4090 GPU, which provides advanced graphics rendering and robust support for machine learning algorithms. Furthermore, a 4 TB solid-state drive (SSD) is utilized to facilitate rapid data access and storage of extensive seismic records, enabling seamless execution of automated workflows and real-time analysis.

The MDLBEEWS system is developed using a set of well-established libraries and tools to ensure reliability, scalability, and high performance. It requires Python (version 3.7 or higher) as the core programming language. Containerization and orchestration are managed using Docker (version 28.2.2) and Docker Compose (version 2.37.1). For real-time data streaming and message brokering, the system uses `kafka-python>=2.0.2`. Deep learning functionalities are powered by `tensorflow>=2.10.0`, while `fastapi>=0.68.0` is used for building high-performance APIs. Seismic data processing is handled by `obspy>=1.2.2`, and real-time, bidirectional communication is supported by `websockets>=10.3`. The system also utilizes `numpy>=1.21.0` for efficient numerical computations.

To ensure the reliability and consistency of the results, the evaluation was conducted using a dataset comprising 100 individual samples. The final performance metrics were derived by calculating the average across all samples, thereby minimizing the impact of outliers and random fluctuations. This approach provides a robust representation of the system’s capabilities under typical operating conditions and enhances the statistical validity of the findings.

1. Performance Analysis of Parallel Data Processing on Data Provider

    Based on the test results, the Multiprocessing model delivered the best performance with the lowest latency (2.955 seconds), CPU usage of 44.50%, and memory usage of 476 MB, remaining stable throughout the testing. In contrast, the Sequential and Multithreading models experienced crashes due to limitations in handling parallel execution and resource contention.

    | Scenario                         | Data Delay (seconds) | CPU Usage (%) | Memory Usage (MB) | Notes                                    |
    |----------------------------------|----------------------|---------------|-------------------|------------------------------------------|
    | Sequential                       | None                 | None          | None              | 40 minutes delay start, crash occurs     |
    | Multithreading                   | 3.150                | 31.24         | 112               | Crash occurs when there are many threads |
    | Multiprocessing                  | **2.955**            | **44.50**     | 476               | **Stable**                               |
    | Multiprocessing + Multithreading | 4.768                | 62.50         | 600               | **Stable**                               |

2. Performance Analysis of NGINX as a Load Balancer for Kafka Broker

    Testing shows that using Kafka as both broker and load balancer results in the lowest data delay (0.0063 seconds) but with higher memory consumption (3,108 MB). Meanwhile, integrating NGINX as a load balancer reduces memory usage to 2,591 MB, but increases data delay to 0.0159 seconds. The choice of configuration depends on whether lower latency or memory efficiency is the priority.

    | Scenario                          | Data Delay (seconds) | CPU Usage (%) | Memory Usage (MB) |
    |-----------------------------------|----------------------|---------------|-------------------|
    | Kafka as Broker and Load Balancer | **0.006329**         | 27.24         | 3,108             |
    | Kafka with NGINX Load Balancer    | 0.015902             | **25.68**     | **2,591**         |

3. Performance Analysis of Multi-Container Execution in Data Archiving and Seismic Detection

    Performance evaluation of the Data Archiver system shows that increasing the number of containers from one to five results in a consistent reduction in data delay, from 0.019274 to 0.015763 seconds. However, this improvement in latency comes with a substantial rise in resource consumption, as CPU usage increases from 150.37% to 197.90% and memory usage from 151.34 MB to 518.59 MB. These findings highlight a trade-off between processing speed and system resource demands.

    | Num of Container | Data Delay (seconds) | CPU Usage (%) | Memory Usage (MB) |
    |------------------|----------------------|---------------|-------------------|
    | 1 Data Archiver  | 0.019274             | 150.37        | 151.34            |
    | 2 Data Archiver  | 0.018164             | 160.55        | 242.68            |
    | 3 Data Archiver  | 0.017323             | 173.48        | 321.34            |
    | 4 Data Archiver  | 0.015903             | 185.81        | 418.59            |
    | 5 Data Archiver  | 0.015763             | 197.90        | 518.59            |

    The evaluation reveals that increasing the number of P wave detectors leads to reduced data delay, indicating improved responsiveness. However, this comes at the cost of higher CPU usage. When NGINX is integrated into the system, data delay slightly increases, but CPU usage is significantly reduced, suggesting a trade-off between processing speed and computational efficiency.

    | Scenario                             | Data Delay (seconds) | CPU Usage (%) |
    |--------------------------------------|----------------------|---------------|
    | 2 P wave Detector                    | 0.034936             | 195.73        |
    | 3 P wave Detector                    | 0.034010             | 228.17        |
    | 4 P wave Detector                    | 0.033197             | 257.94        |
    | 5 P wave Detector                    | 0.032647             | 280.00        |
    | 2 P wave Detector with Load Blanacer | 0.035951             | 157.21        |
    | 3 P wave Detector with Load Blanacer | 0.035214             | 162.55        |
    | 4 P wave Detector with Load Blanacer | 0.034843             | 177.18        |
    | 5 P wave Detector with Load Blanacer | 0.033676             | 192.14        |

4. Performance Analysis of WebSocket Implementation Using Express.js and FastAPI

    The performance comparison between Express.js and FastAPI under varying client loads reveals distinct resource utilization patterns. While Express.js demonstrates lower CPU usage with a single client, it consumes more memory than FastAPI. As the number of clients increases to five, FastAPI exhibits a sharper rise in CPU usage but maintains relatively stable memory consumption, indicating a trade-off between processing efficiency and memory management.

    | Scenario            | Data Delay (seconds) | CPU Usage (%) | Memory Usage (MB) |
    |---------------------|----------------------|---------------|-------------------|
    | Express.js 1 Client | 0.001324             | 12.02         | 95.49             |
    | Express.js 5 Client | 0.001452             | 13.38         | 96.05             |
    | FastAPI 1 Client    | 0.001356             | 17.71         | 72.67             |
    | FastAPI 5 Client    | 0.001578             | 39.05         | 72.97             |

## LICENSE
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation
