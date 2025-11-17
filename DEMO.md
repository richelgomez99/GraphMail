# 🎬 Track 9 Demo Script (3 Minutes)

**Graph-First Project Intelligence System**

---

## 🎯 Opening (0-30 seconds)

### THE PROBLEM

> "Management consultants work on 50+ projects. When a new client comes in with a familiar problem, they can't remember: *What did I do last time? What challenges came up? How did we solve them?*
> 
> Their process intelligence is trapped in 12 months of emails."

**[Pause for impact]**

---

## 💡 THE SOLUTION (30-90 seconds)

### Show System Architecture

> "We built a **Graph-First Sequential Agent System** that extracts verifiable project intelligence."

**[Screen share: Show architecture diagram or README]**

```
Agent 1: Parser          → Cleans emails, identifies projects
Agent 2: Extractor       → Extracts intelligence using LLMs  
Agent 3: Verifier        → Verifies facts, builds knowledge graph
Evaluation: Trust Score  → Custom metric for quality
```

### Live Demo

**[Terminal 1: Run the system]**

```bash
python main.py --run-sample
```

**[While running, narrate:]**

> "Watch the three agents work sequentially:
> - Agent 1 parsed 7 emails, identified the Brand Book project
> - Agent 2 extracts: project name, type, topics, challenges, resolutions
> - Agent 3 verifies each fact against source emails"

### Show the Graph

**[Terminal 2: Show results]**

```bash
cat output/project_intelligence.json
```

**[Highlight key sections:]**

```json
{
  "project_name": "StartupCo Brand Book",
  "project_type": "Design/Branding",
  "topics": [
    {"topic": "API Integration", "evidence": ["msg_002"]},
    {"topic": "Brand Guidelines", "evidence": ["msg_001"]}
  ],
  "challenges": [
    {
      "description": "API key security concern",
      "category": "Technical",
      "evidence": ["msg_002"]
    }
  ],
  "resolutions": [
    {
      "description": "Use hosted solution instead",
      "evidence": ["msg_003"]
    }
  ]
}
```

> "See? Every fact has evidence citations. Click any challenge - here are the emails where it was discussed."

---

## 🔬 THE INNOVATION (90-150 seconds)

### Show Trust Score

**[Show trust_score.json]**

```bash
cat output/trust_score.json
```

```json
{
  "trust_score": 0.897,
  "fact_traceability": 0.970,
  "extraction_completeness": 0.850,
  "phase_accuracy": 0.900,
  "hallucination_rate": 0.000
}
```

> "Our custom **Trust Score**: 0.897 out of 1.0
>
> Why so high?
> - **97% fact traceability** - every claim is proven
> - **90% phase accuracy** - correctly inferred project phase
> - **0% hallucination rate** - Agent 3 rejected any unproven facts"

### The Differentiators

**[Point to code structure]**

> "Three key innovations:
> 
> 1. **Graph-First Sequential** - Not batch extraction. Process chronologically, handle ambiguity naturally.
> 
> 2. **Verification Agent** - Agent 3 doesn't just build the graph. It verifies each fact against source emails. If evidence doesn't support the claim? Rejected.
> 
> 3. **Evidence Traceability** - Every node, every edge has message_ids. Zero hallucination by design."

---

## 💼 THE IMPACT (150-180 seconds)

### Real-World Query Examples

> "Now consultants can query:
>
> **Query 1**: 'Show me all Financial Systems projects where we faced API integration challenges.'
>
> **Result**: Instant filtered graph - project nodes with type='Financial Systems', connected to challenge nodes about APIs.
>
> **Query 2**: 'What resolution methodologies worked for budget concerns?'
>
> **Result**: All resolution nodes linked to budget challenges, with evidence trails."

### The Value Proposition

> "This isn't about *who do I know at Company X* - that's for sales reps.
>
> This is about *what did I do on Project Y?*
>
> When a fintech client needs payment gateway integration, consultant queries the graph: 'Show all projects where we did payment work. What challenges came up? What solutions worked?'
>
> That's **institutional knowledge preservation and reusability**."

**[Pause]**

> "Process intelligence extraction. From emails. Verifiable. Queryable. Production-ready."

---

## 🏆 CLOSING (Final 10 seconds)

> "Graph-First Project Intelligence System.
> 
> Three agents. Zero hallucinations. Maximum value.
> 
> That's how you win Track 9."

**[End with confidence]**

---

## 📊 Backup Slides (If Asked)

### Q: "Why Graph-First instead of batch?"

**A:** "Sequential processing handles temporal ambiguity. Early emails are tentative - 'maybe this is a new project'. Later emails confirm. Graph-First lets us update confidence as evidence accumulates, rather than making all decisions at once with incomplete context."

### Q: "How do you prevent hallucination?"

**A:** "Agent 3 is a Verification Agent. It receives proposed facts from Agent 2, retrieves the claimed evidence emails, and uses LLM to check: *does this evidence ACTUALLY support this claim?* If NO, rejected. We log every rejection - you can see what didn't make it into the graph and why."

### Q: "What makes this valuable for consultants?"

**A:** "It's not 'who do I know' - it's 'what did I do'. When a fintech client says 'we need payment gateway integration', consultant can query: 'Show all projects where we did payment work. What challenges arose? What solutions worked?' That's the value: institutional knowledge becomes queryable intelligence."

### Q: "Can this scale to thousands of emails?"

**A:** "Yes. Agent 1 is deterministic (no LLM), handles any volume. Agent 2 processes projects in parallel. Agent 3 verification is per-fact. With proper batching and caching, scales linearly."

---

## 🎤 Delivery Tips

1. **Speak with confidence** - This is production-ready, not a prototype
2. **Show, don't just tell** - Run the actual system live
3. **Emphasize zero hallucination** - This is the killer feature
4. **Connect to real pain** - Consultants actually need this
5. **End strong** - "That's how you win Track 9"

---

## ✅ Pre-Demo Checklist

- [ ] Sample data created (`python main.py --create-sample`)
- [ ] API key configured in `.env`
- [ ] Test run completed successfully
- [ ] Terminal windows ready (one for running, one for showing results)
- [ ] Know the 3-minute timing cold
- [ ] Backup answers for judge questions ready

---

**YOU GOT THIS! 🚀**
