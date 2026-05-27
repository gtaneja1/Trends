# strategy_synthesizer_v2.py
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_elite_strategy(scraped_data):
    """
    Phase 1: Draft Strategy using CoT (Chain of Thought)
    """
    draft_prompt = f"""
    You are an elite business strategist. Analyze this live data:
    {json.dumps(scraped_data)}
    
    Think step-by-step (Chain of Thought):
    1. Identify the core market gap based on social sentiment.
    2. Assess the competitor ticker weakness.
    3. Formulate 3 ruthless, non-generic tactical steps.
    
    Output the raw strategy draft.
    """
    
    draft_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": draft_prompt}],
        temperature=0.4
    )
    draft_strategy = draft_response.choices[0].message.content

    """
    Phase 2: The Critic (Self-Correction)
    """
    critic_prompt = f"""
    You are a skeptical hedge fund manager. Review this strategy draft:
    {draft_strategy}
    
    Remove all marketing fluff, corporate jargon, and generic advice.
    Reformat it into a strict JSON payload containing:
    "summary", "proof_metrics", and "tactical_steps" (array of title, description, and execution_asset).
    """

    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": critic_prompt}],
        response_format={ "type": "json_object" },
        temperature=0.2 # Low temperature for strict, analytical formatting
    )
    
    return json.loads(final_response.choices[0].message.content)