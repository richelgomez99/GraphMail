# ⚡ Quick Start Guide

Get the Graph-First Project Intelligence System running in 5 minutes.

---

## 🚀 Setup (2 minutes)

### 1. Install Dependencies

```bash
cd GRAPHMAIL
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-key-here
```

Or use Anthropic:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## ✅ Test Installation (1 minute)

Run the test suite (no API key needed):

```bash
python test_system.py
```

You should see:
```
✅ ALL TESTS PASSED
```

---

## 🎯 Run on Sample Data (2 minutes)

### Create Sample Dataset

```bash
python main.py --create-sample
```

Output:
```
✅ Sample dataset created in ./data/
   - sample_emails.json (7 emails)
   - sample_calendar.json (2 events)
   - ground_truth.json
```

### Run Pipeline

```bash
python main.py --run-sample
```

Output:
```
============================================================
GRAPH-FIRST PROJECT INTELLIGENCE SYSTEM
============================================================

[Agent 1] Starting email parsing and project identification...
[Agent 1] Parsed 7 emails
[Agent 1] Identified 1 projects
[Agent 1] Complete

[Agent 2] Starting project intelligence extraction...
[Agent 2] Extracted: StartupCo Brand Book
[Agent 2] Complete

[Agent 3] Starting fact verification and graph building...
[Agent 3] Added project node: StartupCo Brand Book
[Agent 3] Complete

[Evaluation] Calculating Trust Score...

============================================================
PROJECT INTELLIGENCE TRUST SCORE REPORT
============================================================

🏆 TRUST SCORE: 0.XXX

============================================================
PIPELINE COMPLETE
============================================================

✅ Results saved to ./output/
```

---

## 📊 View Results

Results are saved in `./output/`:

- `knowledge_graph.json` - Graph in JSON format
- `knowledge_graph.graphml` - Graph for visualization tools
- `project_intelligence.json` - Extracted project data
- `rejected_facts.json` - Facts that failed verification
- `trust_score.json` - Evaluation metrics

### Visualize Graph

Use tools like:
- **Gephi** - Open `knowledge_graph.graphml`
- **Cytoscape** - Import GraphML
- **NetworkX** - Load JSON in Python

---

## 🔧 Run on Your Data

### 1. Prepare Your Data

Create `your_emails.json`:

```json
[
  {
    "message_id": "msg_001",
    "from": "sender@company.com",
    "to": ["recipient@company.com"],
    "subject": "Project Discussion",
    "date": "2024-01-15",
    "body_text": "Email content here..."
  }
]
```

### 2. Run Pipeline

```bash
python main.py --emails your_emails.json --output ./my_results
```

### 3. Check Results

```bash
ls -lh ./my_results/
```

---

## 🎬 For Hackathon Demo

### Quick Demo Flow

```bash
# 1. Show system structure
tree -L 2 src/

# 2. Show sample data
cat data/sample_emails.json | head -30

# 3. Run pipeline
python main.py --run-sample

# 4. Show results
cat output/trust_score.json
cat output/project_intelligence.json | head -50
```

### What to Highlight

1. **Three-Agent Architecture** - Parser → Extractor → Verifier
2. **Evidence-Based Extraction** - Every fact has message_id citations
3. **Zero Hallucination** - Verification agent rejects unproven facts
4. **Trust Score Metric** - Custom evaluation with 4 weighted components
5. **Production Ready** - Complete error handling, logging, evaluation

---

## ❓ Troubleshooting

### "No API key found"

Make sure `.env` file exists with:
```
OPENAI_API_KEY=your_key_here
```

### "Module not found"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "No such file: data/sample_emails.json"

Create sample data:
```bash
python main.py --create-sample
```

---

## 📚 Next Steps

- Read full [README.md](README.md)
- Review code in `src/`
- Customize for your use case
- Add ground truth for evaluation

---

## 🏆 Track 9 Checklist

✅ Agent-based orchestration (LangGraph)  
✅ Three distinct agents  
✅ Custom evaluation metric (Trust Score)  
✅ Verifiable/traceable (evidence citations)  
✅ Machine-readable output (JSON/GraphML)  
✅ Production-ready implementation  
✅ Real-world value proposition  

---

**Ready to win Track 9! 🚀**
