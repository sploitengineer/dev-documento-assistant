# Dev-Documento: RAG-Powered Developer Assistant

Dev-Documento is a VS Code extension that functions as an AI developer assistant, leveraging a local-first Retrieval-Augmented Generation (RAG) architecture. It generates highly context-aware documentation and performs preliminary code reviews against custom standards, all while running entirely on your local machine to ensure 100% code privacy.

## Overview

This tool is designed to tackle two persistent challenges in software development: stale, misleading documentation and inconsistent, bottlenecked code reviews. By grounding a local Large Language Model (LLM) with the context of your entire codebase and a custom knowledge base of best practices, Dev-Documento acts as an intelligent teammate that helps you write better code, faster.

## Key Features

-   **Context-Aware Documentation**: Generates accurate and insightful docstrings for functions and classes by understanding how they are used throughout your project.
-   **Customizable Code Review**: Checks your code against a knowledge base of coding standards (e.g., PEP 8, Google Style Guides) or your own organization's best practices, providing actionable feedback.
-   **Local-First and Secure**: All processing, from code analysis to AI inference, happens on your local machine. No code is ever sent to a third-party API, guaranteeing the security and confidentiality of your intellectual property.
-   **Language Agnostic by Design**: While the prototype is configured for Python, the architecture is built to be easily extended to other programming languages.

## Technology Stack

-   **Backend**: Python, Flask, LangChain, ChromaDB, Ollama
-   **AI Model**: phi3 (or any other model supported by Ollama)
-   **Frontend**: TypeScript, Visual Studio Code Extension API

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Visual Studio Code**: The code editor itself.
-   **Node.js and npm**: Required for building the VS Code extension.
-   **Python**: Version 3.9 or newer.
-   **Ollama**: To run the LLM locally. Make sure you have pulled a model by running `ollama pull phi3`.

## Installation and Setup Guide

Follow these steps to get Dev-Documento up and running.

### Step 1: Backend Setup

This part configures the Python server that performs all the AI logic.

1.  **Navigate to the Backend**:
    Open a terminal and `cd` into the `backend` directory of the project.

2.  **Create and Activate a Virtual Environment**:
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (Windows)
    .\venv\Scripts\activate

    # Activate it (macOS/Linux)
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    Install all the required Python libraries.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up the Knowledge Base**:
    The AI needs coding standards to perform reviews.
    * In the `backend` folder, create a new folder named `knowledge_base`.
    * Inside `knowledge_base`, create another folder named `python`.
    * Download a coding standard document (e.g., save the Google Python Style Guide as a PDF) and place it inside the `backend/knowledge_base/python/` folder.

5.  **Run the Ingestion Script**:
    This script reads your code and the knowledge base and indexes them in a local vector database.
    ```bash
    python ingest.py
    ```

### Step 2: Frontend (VS Code Extension) Setup

This part packages the extension so you can install it in VS Code.

1.  **Navigate to the Frontend**:
    Open a new terminal and `cd` into the `DevDocumento` directory (the one containing `package.json`).

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Install the Packager**:
    If you don't have it already, install the official VS Code extension packaging tool.
    ```bash
    npm install -g @vscode/vsce
    ```

4.  **Package the Extension**:
    This command bundles the extension into a single installable file.
    ```bash
    vsce package
    ```
    This will create a `DevDocumento-0.0.1.vsix` file in your directory.

5.  **Install the Extension in VS Code**:
    * Open VS Code.
    * Go to the Extensions view.
    * Click the three-dots (...) menu at the top-right.
    * Select "Install from VSIX..." and choose the `.vsix` file you just created.
    * Reload VS Code when prompted.

## How to Use

1.  **Start the Backend Server**:
    In your terminal for the backend (with the virtual environment active), start the Flask server. This server must be running in the background for the extension to work.
    ```bash
    python server.py
    ```

2.  **Use the Extension**:
    * Open any Python project in VS Code.
    * Select a function or class.
    * Right-click on the selection.
    * Choose **"Dev-Doc: Generate Smart Documentation"** to insert a docstring.
    * Choose **"Dev-Doc: Run Pre-Review"** to get code review feedback in a new tab.

## Architecture Diagram

```mermaid
graph LR

%% ================================
%% A. VS Code Frontend
%% ================================
subgraph A["A. VS Code Frontend (Developer's Editor)"]
direction LR
    A1[User Action] --> A2{Extension Logic}
    A2 -- "Step 1: Send Selected Code" --> B1
    B1 -- "Step 5: Return Result" --> A2
    A2 -- "Step 6: Display to User" --> A3[Formatted Docstring / Review Panel]
end

%% ================================
%% B. Local Python Backend
%% ================================
subgraph B["B. Local Python Backend (Flask Server)"]
direction LR
    B1[API Endpoints] --> B2{RAG Logic}
end

%% ================================
%% C. AI & Data Components
%% ================================
subgraph C["C. AI & Data Components (Local)"]
direction TB
    C1[Code Vector Store]
    C2[Practices Vector Store]
    C3[Ollama LLM - Phi-3]
end

%% ================================
%% Connections Between B and C
%% ================================
B2 -- "Step 2: Query for Context" --> C1
B2 -- "Step 3: Query for Best Practices" --> C2
C1 -- "Context" --> B2
C2 -- "Best Practices" --> B2
B2 -- "Step 4: Augment Prompt & Query LLM" --> C3

%% ================================
%% Styling
%% ================================
style A fill:#cde4ff,stroke:#4682b4,stroke-width:2px,rounded
style B fill:#d5f0d5,stroke:#2e8b57,stroke-width:2px,rounded
style C fill:#ffe4c4,stroke:#cd853f,stroke-width:2px,rounded
