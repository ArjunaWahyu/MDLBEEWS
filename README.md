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
- [Contact](#contact)

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

    | Test Case    | Example Configuration File    | Description                             |
    |--------------|------------------------------|-----------------------------------------|
    | Test Case 1  | `docker-compose-1-<code>.yml` | Tests different data processing methods in the data provider |
    | Test Case 2  | `docker-compose-2-<code>.yml` | Tests Kafka and NGINX load balancing    |
    | Test Case 3  | `docker-compose-3-<code>.yml` | Tests multi-container setups for data archiving and detection |
    | Test Case 4  | `docker-compose-4-<code>.yml` | Tests WebSocket implementations with Express.js and FastAPI |

    The following table lists the available configuration files and their descriptions:

    | Configuration File          | Description                                        |
    |-----------------------------|----------------------------------------------------|
    | `docker-compose-1-1.yml`    | Single-threaded data provider                      |
    | `docker-compose-1-2.yml`    | Multi-process data provider                        |
    | `docker-compose-1-3.yml`    | Multi-threaded data provider                       |
    | `docker-compose-1-4.yml`    | Hybrid (multi-threading and multi-processing)      |
    | `docker-compose-2-1.yml`    | Kafka as broker and load balancer                  |
    | `docker-compose-2-2.yml`    | Kafka with NGINX load balancer                     |
    | `docker-compose-3-1.yml`    | 1 Data Archiver                                    |
    | `docker-compose-3-2.yml`    | 2 Data Archivers                                   |
    | `docker-compose-3-3.yml`    | 3 Data Archivers                                   |
    | `docker-compose-3-4.yml`    | 4 Data Archivers                                   |
    | `docker-compose-3-5.yml`    | 5 Data Archivers                                   |
    | `docker-compose-3-6.yml`    | 2 P Wave Detectors                                 |
    | `docker-compose-3-7.yml`    | 3 P Wave Detectors                                 |
    | `docker-compose-3-8.yml`    | 4 P Wave Detectors                                 |
    | `docker-compose-3-9.yml`    | 5 P Wave Detectors                                 |
    | `docker-compose-4-1.yml`    | 1 Express.js client and 1 FastAPI client           |
    | `docker-compose-4-2.yml`    | 5 Express.js clients and 5 FastAPI clients         |

## Our Test

## LICENSE
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries or contributions, please contact the developers:
- Adi Wibowo – [LinkedIn](https://www.linkedin.com/in/adiwibowo)
- Arjuna Wahyu Kusuma – [LinkedIn](https://www.linkedin.com/in/arjunawahyu)