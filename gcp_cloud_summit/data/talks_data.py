"""
Conference Data Module for Google Cloud Technical Summit 2026
Contains event metadata, talk details, speaker profiles, and schedule breakdown.
"""

EVENT_INFO = {
    "name": "Google Cloud Tech Summit 2026",
    "theme": "Innovating with Generative AI, Cloud Native Infrastructure, and Modern Data Pipelines",
    "date": "October 15, 2026",
    "location": "Moscone Center West, San Francisco, CA & Online Live Stream",
    "timezone": "PST (UTC-7)",
    "lunch_break": {
        "title": "Networking & Keynote Lunch Break",
        "duration_minutes": 60,
        "time": "12:15 PM - 1:15 PM",
        "location": "Main Dining Hall & Terrace",
        "description": "Complimentary lunch, interactive Google Cloud sandbox demos, and peer networking."
    }
}

CATEGORIES = [
    "AI & Machine Learning",
    "Cloud Infrastructure & Security",
    "Data Analytics & Databases",
    "Serverless & DevOps"
]

TALKS = [
    {
        "id": 1,
        "title": "Architecting Enterprise AI Agents with Vertex AI & Gemini 1.5 Pro",
        "category": "AI & Machine Learning",
        "time": "09:00 AM - 09:45 AM",
        "start_time": "09:00",
        "end_time": "09:45",
        "description": "Learn how to construct resilient, production-ready AI agents using Google Vertex AI Agent Builder. We will cover tool calling, memory management, groundings with Google Search, and enterprise security guardrails.",
        "room": "Track A - Main Auditorium",
        "speakers": [
            {
                "first_name": "Elena",
                "last_name": "Rostova",
                "role": "Principal AI Architect",
                "company": "Google Cloud",
                "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/elena-rostova-ai"
            },
            {
                "first_name": "Marcus",
                "last_name": "Chen",
                "role": "Lead ML Engineer",
                "company": "Anthropic Partner Solutions",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/marcus-chen-ml"
            }
        ]
    },
    {
        "id": 2,
        "title": "Zero-Trust Security & Workload Identity Federation on GKE Enterprise",
        "category": "Cloud Infrastructure & Security",
        "time": "09:50 AM - 10:35 AM",
        "start_time": "09:50",
        "end_time": "10:35",
        "description": "Deep dive into hardening Google Kubernetes Engine (GKE) clusters using Service Mesh, Anthos Config Management, and passwordless authentication with AWS/Azure using Workload Identity Federation.",
        "room": "Track B - Hall 102",
        "speakers": [
            {
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "role": "Staff Security Engineer",
                "company": "Datadog Cloud",
                "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/sarah-jenkins-sec"
            }
        ]
    },
    {
        "id": 3,
        "title": "Scaling Real-Time Analytics with BigQuery vector search & Dataproc Serverless",
        "category": "Data Analytics & Databases",
        "time": "10:40 AM - 11:25 AM",
        "start_time": "10:40",
        "end_time": "11:25",
        "description": "Explore high-speed streaming data ingestion into BigQuery, integrating PySpark jobs with Dataproc Serverless, and leveraging BigQuery Vector Indexing for RAG pipelines at petabyte scale.",
        "room": "Track A - Main Auditorium",
        "speakers": [
            {
                "first_name": "Devon",
                "last_name": "Vance",
                "role": "VP of Data Engineering",
                "company": "Snowflake & GCP Solutions",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/devon-vance-data"
            },
            {
                "first_name": "Priya",
                "last_name": "Sharma",
                "role": "Staff Developer Advocate",
                "company": "Google Cloud",
                "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/priya-sharma-gcp"
            }
        ]
    },
    {
        "id": 4,
        "title": "Next-Gen Serverless Architectures: Cloud Run, Eventarc & Firestore",
        "category": "Serverless & DevOps",
        "time": "11:30 AM - 12:15 PM",
        "start_time": "11:30",
        "end_time": "12:15",
        "description": "Building event-driven microservices without infrastructure management. Covers automatic GPU scaling in Cloud Run, asynchronous event orchestration with Eventarc, and transactional consistency in Cloud Firestore.",
        "room": "Track B - Hall 102",
        "speakers": [
            {
                "first_name": "Alex",
                "last_name": "Rivera",
                "role": "Cloud Architect Lead",
                "company": "HashiCorp Tech",
                "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/alex-rivera-serverless"
            }
        ]
    },
    {
        "id": 5,
        "title": "Fine-Tuning & Deploying Open Models (Llama 3 & Gemma) on Cloud GPUs",
        "category": "AI & Machine Learning",
        "time": "01:15 PM - 02:00 PM",
        "start_time": "13:15",
        "end_time": "14:00",
        "description": "Step-by-step tutorial on distributed LoRA fine-tuning of Gemma 2 models using Google Cloud TPU v5e slices and Nvidia H100 GPU clusters managed via Google Kubernetes Engine.",
        "room": "Track A - Main Auditorium",
        "speakers": [
            {
                "first_name": "Kenji",
                "last_name": "Takahashi",
                "role": "Senior AI Researcher",
                "company": "Google DeepMind",
                "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/kenji-takahashi-ai"
            },
            {
                "first_name": "Aria",
                "last_name": "Montgomery",
                "role": "Principal MLops Engineer",
                "company": "Weights & Biases",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/aria-montgomery-mlops"
            }
        ]
    },
    {
        "id": 6,
        "title": "Multi-Region High Availability with Cloud Spanner & AlloyDB",
        "category": "Data Analytics & Databases",
        "time": "02:05 PM - 02:50 PM",
        "start_time": "14:05",
        "end_time": "14:50",
        "description": "How top-tier financial platforms achieve 99.999% availability with zero RPO using Cloud Spanner's TrueTime technology and AlloyDB for PostgreSQL dynamic query acceleration.",
        "room": "Track B - Hall 102",
        "speakers": [
            {
                "first_name": "David",
                "last_name": "Kowalski",
                "role": "Distinguished Systems Engineer",
                "company": "Stripe Infrastructure",
                "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/david-kowalski-db"
            }
        ]
    },
    {
        "id": 7,
        "title": "GitOps Pipelines with Cloud Build, Terraform & ArgoCD",
        "category": "Serverless & DevOps",
        "time": "02:55 PM - 03:40 PM",
        "start_time": "14:55",
        "end_time": "15:40",
        "description": "Automating multi-cloud deployment pipelines using declarative GitOps practices. Demonstrating canary releases, automated rollback on Cloud Monitoring alerts, and Infrastructure as Code.",
        "room": "Track B - Hall 102",
        "speakers": [
            {
                "first_name": "Rachel",
                "last_name": "Kim",
                "role": "DevOps Tech Lead",
                "company": "GitLab Cloud Solutions",
                "avatar": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/rachel-kim-devops"
            },
            {
                "first_name": "Carlos",
                "last_name": "Mendoza",
                "role": "Cloud Solutions Specialist",
                "company": "Google Cloud",
                "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/carlos-mendoza-gcp"
            }
        ]
    },
    {
        "id": 8,
        "title": "Cloud FinOps & Cost Optimization at Scale using BigQuery Analytics",
        "category": "Cloud Infrastructure & Security",
        "time": "03:45 PM - 04:30 PM",
        "start_time": "15:45",
        "end_time": "16:30",
        "description": "Actionable strategies for monitoring, analyzing, and reducing enterprise cloud spend on Google Cloud. Learn to leverage Committed Use Discounts, spot VMs, and custom billing dashboards.",
        "room": "Track A - Main Auditorium",
        "speakers": [
            {
                "first_name": "Hannah",
                "last_name": "Abbott",
                "role": "Head of Cloud FinOps",
                "company": "Spotify Engineering",
                "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80",
                "linkedin": "https://www.linkedin.com/in/hannah-abbott-finops"
            }
        ]
    }
]
