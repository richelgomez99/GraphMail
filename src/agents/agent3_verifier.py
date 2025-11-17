"""Agent 3: Verification & Graph Builder
Verifies extracted facts and builds knowledge graph.

Security: Integrated rate limiting (Article VIII: Security by Default)
"""

import json
import networkx as nx
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import structlog

# Import security modules
from src.sanitization.rate_limiter import rate_limited_llm_call
from src.config import get_settings

logger = structlog.get_logger(__name__)


def get_llm():
    """Get LLM instance."""
    settings = get_settings()

    if settings.openai_api_key:
        # Using configured model from settings
        return ChatOpenAI(model=settings.agent3_model, temperature=0)
    elif settings.anthropic_api_key:
        return ChatAnthropic(model=settings.agent3_model, temperature=0)
    else:
        raise ValueError("No API key found")


class GraphBuilder:
    """Builds and verifies knowledge graph from extracted intelligence."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.rejected_facts = []
        self.llm = get_llm()
    
    def verify_and_add_project(
        self,
        project_data: Dict,
        source_emails: List[Dict]
    ) -> Optional[str]:
        """Verify project data and add to graph.
        
        Args:
            project_data: Extracted project intelligence
            source_emails: Original cleaned emails for verification
            
        Returns:
            project_id if successful, None if rejected
        """
        project_id = project_data['project_id']
        
        # Verify project name
        name_valid = self.verify_fact(
            claim=f"Project named '{project_data['project_name']}'",
            evidence_ids=project_data.get('evidence', []),
            source_emails=source_emails
        )
        
        if not name_valid:
            self.rejected_facts.append({
                'claim': f"Project: {project_data['project_name']}",
                'reason': 'Cannot verify project name from evidence',
                'evidence_ids': project_data.get('evidence', [])
            })
            return None
        
        # Add project node
        self.graph.add_node(
            project_id,
            node_type='Project',
            name=project_data['project_name'],
            project_type=project_data.get('project_type', 'Other'),
            timeline=project_data.get('timeline', {}),
            scope=project_data.get('scope', {}).get('description', ''),
            phase=project_data.get('phase', 'Unknown'),
            phase_reasoning=project_data.get('phase_reasoning', ''),
            evidence=project_data.get('evidence', [])
        )
        
        logger.info("agent3.project_added",
                   project_id=project_id,
                   project_name=project_data['project_name'],
                   project_type=project_data.get('project_type', 'Other'))
        
        # Add topics
        for topic in project_data.get('topics', []):
            self._add_topic(project_id, topic, source_emails)
        
        # Add challenges
        for challenge in project_data.get('challenges', []):
            self._add_challenge(project_id, challenge, source_emails)
        
        # Add resolutions
        for resolution in project_data.get('resolutions', []):
            self._add_resolution(project_id, resolution, source_emails)
        
        return project_id
    
    def _add_topic(self, project_id: str, topic: Dict, source_emails: List[Dict]):
        """Add topic node and edge."""
        topic_name = topic.get('topic', '')
        topic_id = f"topic_{topic_name.lower().replace(' ', '_').replace('/', '_')}"
        
        # Verify topic
        valid = self.verify_fact(
            claim=f"Project discusses topic: {topic_name}",
            evidence_ids=topic.get('evidence', []),
            source_emails=source_emails
        )
        
        if valid:
            self.graph.add_node(
                topic_id,
                node_type='Topic',
                name=topic_name,
                evidence=topic.get('evidence', [])
            )
            
            self.graph.add_edge(
                project_id,
                topic_id,
                edge_type='HAS_TOPIC',
                evidence=topic.get('evidence', [])
            )
        else:
            self.rejected_facts.append({
                'claim': f"Topic: {topic_name}",
                'reason': 'Cannot verify from evidence'
            })
    
    def _add_challenge(self, project_id: str, challenge: Dict, source_emails: List[Dict]):
        """Add challenge node and edge."""
        challenge_id = f"{project_id}_{challenge.get('id', 'ch_unknown')}"
        
        # Verify challenge
        valid = self.verify_fact(
            claim=f"Challenge: {challenge.get('description', '')}",
            evidence_ids=challenge.get('evidence', []),
            source_emails=source_emails
        )
        
        if valid:
            self.graph.add_node(
                challenge_id,
                node_type='Challenge',
                description=challenge.get('description', ''),
                category=challenge.get('category', 'Other'),
                raised_date=challenge.get('raised_date', ''),
                evidence=challenge.get('evidence', [])
            )
            
            self.graph.add_edge(
                project_id,
                challenge_id,
                edge_type='FACED_CHALLENGE',
                evidence=challenge.get('evidence', [])
            )
        else:
            self.rejected_facts.append({
                'claim': f"Challenge: {challenge.get('description', '')}",
                'reason': 'Cannot verify from evidence'
            })
    
    def _add_resolution(self, project_id: str, resolution: Dict, source_emails: List[Dict]):
        """Add resolution node and edge."""
        resolution_id = f"{project_id}_{resolution.get('id', 'res_unknown')}"
        challenge_id = f"{project_id}_{resolution.get('resolves', '')}"
        
        # Verify resolution
        valid = self.verify_fact(
            claim=f"Resolution: {resolution.get('description', '')}",
            evidence_ids=resolution.get('evidence', []),
            source_emails=source_emails
        )
        
        if valid:
            self.graph.add_node(
                resolution_id,
                node_type='Resolution',
                description=resolution.get('description', ''),
                resolved_date=resolution.get('resolved_date', ''),
                methodology=resolution.get('methodology', ''),
                evidence=resolution.get('evidence', [])
            )
            
            # Link to challenge if it exists
            if self.graph.has_node(challenge_id):
                self.graph.add_edge(
                    challenge_id,
                    resolution_id,
                    edge_type='RESOLVED_BY',
                    evidence=resolution.get('evidence', [])
                )
            else:
                # Link to project if challenge not found
                self.graph.add_edge(
                    project_id,
                    resolution_id,
                    edge_type='HAS_RESOLUTION',
                    evidence=resolution.get('evidence', [])
                )
        else:
            self.rejected_facts.append({
                'claim': f"Resolution: {resolution.get('description', '')}",
                'reason': 'Cannot verify from evidence'
            })
    
    def verify_fact(
        self,
        claim: str,
        evidence_ids: List[str],
        source_emails: List[Dict]
    ) -> bool:
        """Verify if evidence actually supports claim.
        
        Args:
            claim: The fact being claimed
            evidence_ids: Message IDs cited as evidence
            source_emails: All source emails
            
        Returns:
            True if verified, False otherwise
        """
        # Get evidence emails
        evidence_emails = [
            e for e in source_emails
            if e['message_id'] in evidence_ids
        ]
        
        if not evidence_emails:
            return False
        
        # Format evidence for verification
        evidence_text = "\n\n".join([
            f"Email {e['message_id']}:\n"
            f"Subject: {e['subject']}\n"
            f"Body: {e['body_clean'][:600]}"
            for e in evidence_emails
        ])
        
        # Use LLM to verify
        prompt = f"""Verify if the evidence supports the claim.

Claim: {claim}

Evidence emails:
{evidence_text}

Answer YES only if the claim is directly stated or strongly implied in the evidence.
Answer NO if the claim requires assumptions or is not supported.

Output JSON: {{"supported": true/false, "reasoning": "brief explanation"}}

Output ONLY the JSON, no additional text.
"""
        
        try:
            # SECURITY: Invoke LLM with rate limiting
            response = rate_limited_llm_call(self.llm.invoke, prompt)
            content = response.content
            
            # Parse JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            result = json.loads(content)
            return result.get('supported', False)
        except Exception as e:
            logger.error("agent3.verification_error", error=str(e), claim=claim[:100])
            # Conservative: reject if verification fails
            return False
    
    def export_graph(self, format: str = 'json') -> Dict:
        """Export graph in specified format.
        
        Args:
            format: 'json' or 'graphml'
            
        Returns:
            Graph data in requested format
        """
        if format == 'json':
            return nx.node_link_data(self.graph)
        elif format == 'graphml':
            # Write to file
            nx.write_graphml(self.graph, '/tmp/knowledge_graph.graphml')
            return {'file': '/tmp/knowledge_graph.graphml'}
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def get_graph_stats(self) -> Dict:
        """Get graph statistics."""
        node_types = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('node_type', 'Unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        edge_types = {}
        for u, v in self.graph.edges():
            edge_type = self.graph[u][v].get('edge_type', 'Unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': node_types,
            'edge_types': edge_types
        }


def agent_3_verifier(state: Dict) -> Dict:
    """Agent 3: Verify facts and build graph.
    
    Args:
        state: ProjectGraphState dict
        
    Returns:
        Updated state with verified_graph, graph_json
    """
    logger.info("agent3.verification_started",
                project_count=len(state.get('project_intelligence', [])))
    
    builder = GraphBuilder()
    
    # Process each project
    for project_intel in state['project_intelligence']:
        builder.verify_and_add_project(
            project_data=project_intel,
            source_emails=state['cleaned_emails']
        )
    
    # Export graph
    graph_json = builder.export_graph(format='json')
    
    # Get stats
    stats = builder.get_graph_stats()
    logger.info("agent3.verification_complete",
                nodes=stats['nodes'],
                edges=stats['edges'],
                projects=stats.get('projects', 0),
                rejected_facts=len(builder.rejected_facts))
    
    return {
        "verified_graph": builder.graph,
        "rejected_facts": builder.rejected_facts,
        "graph_json": graph_json
    }
