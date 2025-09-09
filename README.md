

# Welcome to the SDLC_core Repo

<details>
  <summary><strong>Table of Contents</strong></summary>

- [Installing and running Windows Terminal](#installing-and-running-windows-terminal)
- [Module Roadmap](#SDLC_core-roadmap)
- [SDLC_core Overview](#sdlc_core-overview)
- [Resources](#resources)
- [FAQ](#faq)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Communicating with the Team](#communicating-with-the-team)
- [Developer Guidance](#developer-guidance)
- [Code of Conduct](#code-of-conduct)

</details>

<br />

This repository contains the source code for the SDLC_core project, a Python-based framework for building AI-powered software development life cycle tools.

Related repositories include:

* [SDLC_core Documentation](https://github.com/SoftwareDevLabs) (Placeholder)

## SDLC_core Roadmap

The plan for the SDLC_core [is described here](./doc/roadmap-20xx.md) and
will be updated as the project proceeds.

## Installing and running Windows Terminal

> [!NOTE]
> This section is a placeholder and may not be relevant to this project.

## SDLC_core Overview

SDLC_core is a Python-based Software Development Life Cycle core project that provides AI/ML capabilities for software development workflows. The repository contains modules for LLM clients, intelligent agents, memory management, prompt engineering, document retrieval, skill execution, and various utilities. It combines a Python core with TypeScript for Azure DevOps pipeline configurations.

## Resources

> [!NOTE]
> This section is a placeholder. Please add relevant links.

* [Link 1](add link)
* [Link 2](add link)

## FAQ

> [!NOTE]
> This section is a placeholder. Please add frequently asked questions.

### Q1
### Q2

## Documentation

All project documentation is located at [softwaremodule-docs](./doc/). If you would like
to contribute to the documentation, please submit a pull request on the [SDLC_core
Documentation](https://github.com/SoftwareDevLabs) repository.

---

## 🔧 Key Components

```

📁 config/ → YAML config for models, prompts, logging
📁 data/ → Prompts, embeddings, and other dynamic content
📁 examples/ → Minimal scripts to test key features
📁 notebooks/ → Quick experiments and prototyping
📁 tests/ → Unit, integration, and end-to-end tests
📁 src/ → The core engine — all logic lives here (./src/README.md)

```
---

## ⚡ Best Practices

- Track prompt versions and results  
- Separate configs using YAML files
- Maintain separation between model clients
- Structure code by clear module boundaries  
- Cache responses to reduce latency and cost  
- Handle errors with custom exceptions  
- Use notebooks for rapid testing and iteration  
- Monitor API usage and set rate limits  
- Keep code and docs in sync  

---

## 🧭 Getting Started

1.  **Clone the repository.**
2.  **Set up your Python environment.** A Python version between 3.10 and 3.12 is recommended.
3.  **Install dependencies.** The project's dependencies are split into several files. For general development, you will need `requirements-dev.txt`.
    ```bash
    pip install -r requirements-dev.txt
    ```
4.  **Set up your environment variables.** Copy the `.env.template` file to `.env` and fill in the required API keys for the LLM providers you want to use.
5.  **Explore the examples.** The `examples/` directory contains scripts that demonstrate the key features of the project.
6.  **Experiment in notebooks.** The `notebooks/` directory is a great place to start experimenting with the codebase.

---

## 💡 Development Tips

- Use modular structure  
- Test components early  
- Track with version control  
- Keep datasets fresh  
- Keep documentation updated
- Monitor API usage and limits 

---

## 📁 Core Files

- `requirements.txt` – Core package dependencies for the project.
- `requirements-dev.txt` - Dependencies for development and testing.
- `requirements-docs.txt` - Dependencies for generating documentation.
- `AGENTS.md` - Instructions for AI agents working with this repository.
- `README.md` – Project overview and usage.
- `Dockerfile` – Container build instructions.

## Running tests

We provide a small helper script that creates an isolated virtualenv and runs the test suite.

Run the full test suite locally:

```bash
./scripts/run-tests.sh
```

Or run just the deepagent tests (fast):

```bash
./scripts/run-tests.sh test/unit -k deepagent
```

You can also use the Makefile targets:

```bash
make test
make lint
```

---

## Contributing

We are excited to work with the community to build and enhance this project.

***BEFORE you start work on a feature/fix***, please read & follow our [Contributor's Guide](./CONTRIBUTING.md) to
help avoid any wasted or duplicate effort.

## Communicating with the Team

The easiest way to communicate with the team is via GitHub issues.

Please file new issues, feature requests and suggestions, but **DO search for similar open/closed preexisting issues before creating a new issue.**

If you would like to ask a question that you feel doesn't warrant an issue (yet), please reach out to us via email: [info@softwaredevlabs.com][conduct-email]

## Developer Guidance

Please review these brief docs below about our coding practices.

> 👉 If you find something missing from these docs, feel free to contribute to
> any of our documentation files anywhere in the repository (or write some new
> ones!)

This is a work in progress as we learn what we'll need to provide people in
order to be effective contributors to our project.

 - [Coding Style](./doc/STYLE.md)
 - [Code Organization](./doc/ORGANIZATION.md)
 - [Exceptions in our legacy codebase](./doc/EXCEPTIONS.md)

---

## Code of Conduct

This project has adopted the [Code of Conduct][conduct-code]. For more information see the [Code of Conduct][conduct-code] or contact [info@softwaredevlabs.com][conduct-email] with any additional questions or comments.

[conduct-code](./CODE_OF_CONDUCT.md)

[conduct-email]: mailto:info@softwaredevlabs.com
[conduct-code]: ./CODE_OF_CONDUCT.md
[conduct-email]: mailto:info@softwaredevlabs.com
