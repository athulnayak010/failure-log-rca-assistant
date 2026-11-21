import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Root Cause Analysis assistant for software test failures.
You will be given a list of parsed failed test log entries.

Your job:
1. Group the failures into clusters based on similar symptoms (same error type, similar error message patterns).
2. Identify the TOP 3 most probable root causes across all failures, ranked by how many logs they likely explain.
3. For each root cause, give a confidence note (High/Medium/Low) and WHY.
4. Suggest 1-2 concrete next debugging steps per root cause.

Respond ONLY in valid JSON, no preamble, no markdown formatting, in this exact structure:
{
  "symptom_groups": [
    {"group_name": "string", "count": number, "example_tests": ["string"]}
  ],
  "root_causes": [
    {
      "rank": 1,
      "cause": "string",
      "confidence": "High/Medium/Low",
      "reasoning": "string",
      "affected_tests_count": number,
      "next_debugging_steps": ["string", "string"]
    }
  ]
}
"""

def analyze_logs(parsed_logs):
    """
    Sends parsed log data to the AI model and returns structured 
    symptom groups + ranked root causes.
    """
    log_summary = "\n".join([
    f"- Test: {log['test_name']}, Error: {log['error_type']}, Message: {log['error_message']}"
    if log['error_type'] != 'UNPARSED'
    else f"- Unparsed line: {log['raw_line']}"
    for log in parsed_logs
])

    user_prompt = f"Here are {len(parsed_logs)} failed test log entries:\n\n{log_summary}\n\nAnalyze these per your instructions."

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()

    # Clean up in case model wraps output in markdown fences
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json", "", 1).strip()

    try:
        result = json.loads(raw_output)
        return result
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response as JSON", "raw_output": raw_output}


# Quick manual test
if __name__ == "__main__":
    from log_parser import parse_log_file
    logs = parse_log_file("sample_logs.txt")
    result = analyze_logs(logs)
    print(json.dumps(result, indent=2))






















    