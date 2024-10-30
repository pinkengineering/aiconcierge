```mermaid
graph TD
    %% Top to Bottom Layout
    subgraph User Interaction
        direction TB
        style User Interaction fill:##8dd4ea,stroke:#4a90e2,stroke-width:2px,color:#000000
        User[User]
    end
    
    subgraph User Devices
        direction TB
        style User Devices fill:#8dd4ea,stroke:#4a90e2,stroke-width:2px,color:#000000
        Mobile[Mobile Browser]
        Desktop[Desktop Browser]
    end
    
    subgraph User Interface
        direction TB
        style User Interface fill:#8dd4ea,stroke:#4a90e2,stroke-width:2px,color:#000000
        ST[Streamlit App]
    end
    
    subgraph AWS
        direction TB
        style AWS fill:#f9f9c4,stroke:#d3d3d3,stroke-width:2px,color:#000000
        A[Bedrock AI Agent]
        S3[Amazon S3 - Stores Documents & Images]
        KB[Knowledge Base]
        PC[Pinecone Vector DB]
        GR[Guard Rails]
        SES[Email Service]
    end
    
    subgraph Sources
        direction TB
        style Sources fill:#f9f9c4,stroke:#d3d3d3,stroke-width:2px,color:#000000
        Docs[Documents]
        Images[Images]
    end

    %% Connections
    User -->|Access| Mobile
    User -->|Access| Desktop
    Mobile -->|Access| ST
    Desktop -->|Access| ST
    ST -->|User Query| A
    A -->|Fetch Data| S3
    A -->|Query| KB
    A -->|Search| PC
    A -->|Fetch| GR
    A -->|Send Data| SES

    Docs -->|Upload| S3
    Images -->|Upload| S3
    A -->|Response| ST
    ST -->|Display| Mobile
    ST -->|Display| Desktop
```