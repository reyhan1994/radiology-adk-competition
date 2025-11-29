# AI Radiologist Assistant Agent (ADK-based)

A conceptual multi-agent AI system for radiology image analysis, report generation, and automatic coding — implemented as part of the ADK Agents Intensive Course.

## ⭐ Overview
- Multi-agent architecture using `SequentialAgent`  
- Supports Function Tools, Agent Tools, Long-Running Operations (LRO), LLM-as-tool, Agent-to-Agent communication, and memory consolidation  
- Workflow: patient history → image analysis → report generation → pathology coding → memory storage  

## 🧰 Quick Start 
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run inference (replace PATH_TO_IMAGES with your data folder)
python src/master_agent.py --input PATH_TO_IMAGES --output submission.csv```


## 📁 Repository Structure
root/
│
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── agents/
    │   ├── patient_context_agent.py
    │   ├── image_analysis_agent.py
    │   ├── report_generation_agent.py
    │   ├── pathology_coding_agent.py
    │   └── memory_consolidation_agent.py
    └── master_agent.py




