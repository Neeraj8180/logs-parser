import os
import json
import argparse
import re
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key) if groq_api_key else None

OUTPUT_FILE = "metrics_output.json"

def call_groq(prompt, model="llama3-70b-8192"):
    if not client:
        print("❌ GROQ client not initialized - skipping API call")
        return ""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error during Groq API call: {e}")
        return ""

def extract_metrics_from_log(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    with open(file_path, 'r') as file:
        content = file.read()

    prompt = f"""
Extract BBDEV throughput metrics from the following log content and format them into the exact JSON structure shown below.

REQUIRED OUTPUT FORMAT:
{{
  "resultsInfo": [
    {{
      "run": 1,
      "statistics": [
        {{
          "Stress-BBDEV-Throughput": [
            {{
              "Encode": [
                {{ "metricsName": "encode_queues", "metricsValue": <int> }},
                {{ "metricsName": "decode_queues", "metricsValue": <int> }},
                {{ "metricsName": "dequeue_threads", "metricsValue": <int> }},
                {{ "metricsName": "iter", "metricsValue": <int> }},
                {{ "metricsName": "time_out", "metricsValue": <int> }},
                {{ "metricsName": "burst_size", "metricsValue": <int> }},
                {{ "metricsName": "nb_ops", "metricsValue": <int> }},
                {{ "metricsName": "Encode Throughput In (Gbps)", "metricsValue": <float> }},
                {{ "metricsName": "Encode Throughput Out (Gbps)", "metricsValue": <float> }}
              ],
              "Decode": [
                {{ "metricsName": "encode_queues", "metricsValue": <int> }},
                {{ "metricsName": "decode_queues", "metricsValue": <int> }},
                {{ "metricsName": "dequeue_threads", "metricsValue": <int> }},
                {{ "metricsName": "iter", "metricsValue": <int> }},
                {{ "metricsName": "time_out", "metricsValue": <int> }},
                {{ "metricsName": "burst_size", "metricsValue": <int> }},
                {{ "metricsName": "nb_ops", "metricsValue": <int> }},
                {{ "metricsName": "Decode Throughput In (Gbps)", "metricsValue": <float> }},
                {{ "metricsName": "Decode Throughput Out (Gbps)", "metricsValue": <float> }}
              ],
              "status": "OK"
            }}
          ],
          "status": "OK"
        }}
      ],
      "summary": "Results for Run 1"
    }}
  ]
}}

RULES:
1. Extract ALL metrics from both Encode and Decode sections
2. If any metric is missing, use 0 as the default value
3. Maintain the exact JSON structure shown above
4. Return ONLY the JSON output - no additional text or explanations
5. All throughput values should be in Gbps (convert if necessary)
6. Set both status fields to "OK" unless there are errors in the log

Now process this log content:
{content}
"""

    return call_groq(prompt)

def save_result_to_file(result_text):
    try:
        # Clean the response to extract just the JSON
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        json_text = result_text[json_start:json_end]
        
        # Parse and validate the structure
        parsed = json.loads(json_text)
        
        # Validate required structure
        if not all(key in parsed for key in ["resultsInfo"]):
            raise ValueError("Missing required top-level keys")
            
        with open(OUTPUT_FILE, "w") as f:
            json.dump(parsed, f, indent=2)
        print(f"✅ Metrics saved to: {OUTPUT_FILE}")
        return True
    except json.JSONDecodeError:
        print("❌ Failed to parse response as valid JSON")
    except ValueError as ve:
        print(f"❌ Invalid structure in response: {ve}")
    except Exception as e:
        print(f"❌ Unexpected error saving results: {e}")
    
    print("Raw response was:")
    print(result_text)
    return False

def main():
    parser = argparse.ArgumentParser(description="Extract BBDEV throughput metrics from log using Groq API")
    parser.add_argument("-f", "--file", required=True, help="Path to the log file")
    args = parser.parse_args()

    print(f"🔍 Processing log file: {args.file}")
    result_text = extract_metrics_from_log(args.file)
    
    if result_text:
        save_result_to_file(result_text)

if __name__ == "__main__":
    main()