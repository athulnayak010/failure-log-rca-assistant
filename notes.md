## Day 1 - Step 1: Setup (final)
- Using Groq API (free tier)
- Model: openai/gpt-oss-120b (Groq's recommended replacement 
  for llama-3.3-70b-versatile, which was decommissioned Aug 16, 2026)
- Verified API key + model access with a test call before building main logic

## Day 1 - Step 2: Sample Data
- Created 25 synthetic failed test logs
- Designed 5 distinct failure categories: UI timeouts, 
  DB constraint violations, null/JS errors, connection 
  failures, assertion mismatches
- Purpose: give the AI grouping real signal to work with, 
  not random noise

  ## Day 1 - Step 3: Log Parser
- Built regex-based parser extracting: timestamp, test_name, 
  error_type, error_message from each log line
- Handles malformed/unexpected lines gracefully by tagging 
  them as "UNPARSED" instead of crashing
- Verified: successfully parsed all 25/25 sample log lines

## Day 1 - Step 4: RCA Engine (AI Integration)
- Model: openai/gpt-oss-120b via Groq API
- Single AI call per analysis - takes all parsed logs, returns 
  structured JSON: symptom_groups (grouped by pattern) + 
  root_causes (top 3, ranked, with confidence + reasoning + 
  next debugging steps)
- Prompt designed to force strict JSON output (no markdown, 
  no preamble) so it's directly renderable in UI
- Added JSON parsing safety: strips markdown fences if model 
  wraps output in ```json blocks
- Verified: successfully analyzed 25 logs -> produced grouped 
  symptoms + 3 ranked root causes with actionable debugging steps

  ## Day 2 - Step 5: Streamlit UI (app.py)
- Built a single-page Streamlit web app that wraps the parser + RCA engine
- Two input methods provided: file upload (.txt) or direct paste — 
  gives flexibility for demo and for testing different log sources
- Flow: user provides logs -> click "Analyze Logs" -> app parses 
  logs (log_parser.py) -> sends to AI (rca_engine.py) -> renders 
  results in two sections:
  1. Grouped Symptom Summary (expandable cards per symptom group, 
     showing count + example affected test names)
  2. Top 3 Probable Root Causes (ranked, color-coded by confidence: 
     green=High, yellow=Medium, red=Low, with reasoning + 
     suggested debugging steps per cause)
- Added basic input validation (warns if no log data provided 
  before analyze is clicked)
- Added error handling: if AI response isn't valid JSON, shows 
  a clear error + raw output instead of crashing silently
- Verified: pasted full sample_logs.txt (25 lines) into the app -> 
  successfully produced 4 symptom groups + 3 ranked root causes, 
  matching the brief's exact expected output format