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
