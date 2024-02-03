# GSD (GPU Swarm for Datasets) 🕸️🌐💻🔥

## Join the Swarm

```shell
docker run -it --rm --shm-size=2g --gpus all gardner/gsd:latest --server https://q.llm.nz
```

## Introduction 📖

GSD (GPU Swarm for Datasets) is a FOSS initiative designed to democratize the improvement of datasets for broader R&D. This project brings together volunteers who contribute their GPU time to enhance text datasets, making them more useful for the community at large. Inspired by the paper "Rephrasing the Web: A Recipe for Compute and Data-Efficient Language Modeling" by Maini et al. (January 29, 2024) [arxive](https://arxiv.org/abs/2401.16380), GSD is a community approach to processing and refining data efficiently and at scale.

GSD is similar to a decentralized version of Facebook's [cc_net](https://github.com/facebookresearch/cc_net).

## How It Works 🚀

Participants (You!) contribute by running a Docker container, which connects to a work queue to fetch work packets, processes the text locally using [vLLM](https://github.com/vllm-project/vllm), and submits the results. The output is collated and batched before being published to HuggingFace.

## Getting Started 🌟

### Prerequisites

- Docker 🐳
- A stable internet connection 🌐
- A GPU that can run Mistral 7B (~12GB of VRAM) We are accepting pull requests for CPU workers!
- A commitment to Getting Shit Done ✅

### Join the Swarm

To join the swarm, simply run the docker container:
```shell
docker run -it --rm --gpus all gardner/gsd:latest --server https://q.llm.nz
```

### Contributing

1. **Clone the Repository**:

```bash
git clone https://github.com/gardner/gsd.git
```

2. **Run the Docker Container**: In the repository's directory, execute:

```bash
docker-compose up --build
```

## Acknowledgements 🙏

A huge thank you to every volunteer and to the pioneers who inspired GSD, especially the authors of the influential work by Maini et al. Your contributions drive this project forward.

## License 📄

GSD is under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
