import os
import re
import json
import argparse
import time
from dotenv import load_dotenv
from groq import Groq
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load .env file and API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)

OUTPUT_FILE = "throughput_metrics.json"
groq_response_times = []
parsing_times = []

def call_groq(prompt, model="llama3-70b-8192"):
    try:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        groq_response_times.append(time.time() - start)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during GROQ API call: {e}")
        return json.dumps({
            "error": str(e),
            "metrics": {
                "Burst size": 0,
                "No_ops": 0,
                "threads": 0,
                "Throughput": 0
            }
        })

def extract_preamble_metrics(content):
    prompt = (
        "Extract the following system information from the DPDK test log preamble and return as JSON:\n"
        "1. RTE Version (e.g., '23.11.0')\n"
        "2. Platform (e.g., 'Intel(R) Xeon(R) Platinum 8480+')\n"
        "3. BBDEV PMD version (e.g., 'v1.0.3')\n"
        "4. Any other relevant system configuration details\n\n"
        "Return a JSON object with these keys: 'rte_version', 'platform', 'pmd_version', 'other_config'\n"
        "Ensure all values are strings. If any information is missing, use 'unknown'.\n\n"
        "Log content:\n" + content
    )
    return call_groq(prompt)

def extract_test_metrics(content):
    prompt = (
        "Analyze this DPDK BBDEV test log and extract all metrics in JSON format with this exact structure:\n\n"
        "1. First determine if this is an ENCODE or DECODE test from the log content\n"
        "2. Extract these parameters from the test name/configuration:\n"
        "   - K_prime_minus_L (block size as integer)\n"
        "   - E (codeword size as integer)\n"
        "   - BG (base graph number as integer)\n"
        "   - Q_m (modulation order as integer)\n"
        "   - For decode: SNR value as string with 2 decimal places (e.g., '40.00')\n"
        "   - For encode: 'RM_on_CRC_24B' flag as boolean\n"
        "   - LLR_width if mentioned (as integer)\n\n"
        "3. Extract these operational metrics:\n"
        "   - Burst size (as integer, typically 512)\n"
        "   - No_ops (number of operations as integer, typically 1024)\n"
        "   - threads (number of threads as integer, typically 16)\n"
        "   - Throughput (as float with exactly 4 decimal places)\n\n"
        "Return a JSON object with this exact structure:\n"
        "{\n"
        "  \"test_type\": \"encode|decode\",\n"
        "  \"test_parameters\": {\n"
        "    \"K_prime_minus_L\": int,\n"
        "    \"E\": int,\n"
        "    \"BG\": int,\n"
        "    \"Q_m\": int,\n"
        "    \"SNR\": string (only for decode),\n"
        "    \"RM_on_CRC_24B\": bool (only for encode),\n"
        "    \"LLR_width\": int (if present)\n"
        "  },\n"
        "  \"metrics\": {\n"
        "    \"Burst size\": int,\n"
        "    \"No_ops\": int,\n"
        "    \"threads\": int,\n"
        "    \"Throughput\": float\n"
        "  }\n"
        "}\n\n"
        "Important:\n"
        "- Use the exact same field names as shown\n"
        "- Maintain consistent data types\n"
        "- For decode tests, always include SNR even if not in log (use '40.00' as default)\n"
        "- For encode tests, include RM_on_CRC_24B as true unless specified otherwise\n\n"
        "Log content:\n" + content
    )
    return call_groq(prompt)

def update_metrics_file(new_data):
    # Initialize empty structure if file doesn't exist
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = {
            "system_info": {},
            "resultsInfo": []
        }

    # Handle preamble data (system information)
    if "preamble" in new_data:
        try:
            system_info = json.loads(new_data["preamble"][0])
            existing_data["system_info"] = system_info
        except json.JSONDecodeError:
            print("Warning: Failed to parse system info JSON")

    # Handle test results
    for test_name, test_results in new_data.items():
        if test_name != "preamble":
            try:
                test_data = json.loads(test_results[0])
                
                # Skip if we got an error response
                if "error" in test_data:
                    print(f"Warning: Error in test data for {test_name}")
                    continue

                # Find or create the test run entry
                run_entry = None
                for entry in existing_data["resultsInfo"]:
                    if entry.get("run") == 1:  # Assuming single run for now
                        run_entry = entry
                        break
                
                if not run_entry:
                    run_entry = {
                        "run": 1,
                        "statistics": [{
                            "DPDK-Test-BBDEV-Throughput": [],
                            "status": "OK"
                        }],
                        "summary": "Results for Run 1"
                    }
                    existing_data["resultsInfo"].append(run_entry)
                
                # Build the test case identifier string
                test_identifier = build_test_identifier(test_data)
                
                # Create the test case entry
                throughput_key = f"{test_data['test_type'].capitalize()} Throughput"
                test_case = {
                    test_identifier: [
                        {"metricsName": "Burst size", "metricsValue": test_data["metrics"]["Burst size"]},
                        {"metricsName": "No_ops", "metricsValue": test_data["metrics"]["No_ops"]},
                        {"metricsName": "threads", "metricsValue": test_data["metrics"]["threads"]},
                        {"metricsName": throughput_key, "metricsValue": test_data["metrics"]["Throughput"]}
                    ]
                }
                
                # Add to the statistics
                run_entry["statistics"][0]["DPDK-Test-BBDEV-Throughput"].append(test_case)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to process test {test_name}: {str(e)}")

    # Write the updated data back to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(existing_data, f, indent=2)

def build_test_identifier(test_data):
    params = test_data["test_parameters"]
    identifier_parts = [
        f"ldpc_{test_data['test_type']}",
        f"LD{params['K_prime_minus_L']}",
        f"K_prime_minus_L_{params['K_prime_minus_L']}",
        f"E_{params['E']}",
        f"BG_{params['BG']}",
        f"Q_m_{params['Q_m']}"
    ]

    if test_data["test_type"] == "decode":
        identifier_parts.append(f"SNR_{params.get('SNR', '40.00')}")
        if "LLR_width" in params:
            identifier_parts.append(f"LLR_width_{params['LLR_width']}")
    else:
        identifier_parts.append("RM_on_CRC_24B")

    return "_".join(identifier_parts)

def process_log_block(content, is_preamble=False):
    start_time = time.time()
    if is_preamble:
        result = {"preamble": [extract_preamble_metrics(content)]}
    else:
        raw = extract_test_metrics(content)
        result = {get_file_id(content): [raw]}
    parsing_times.append(time.time() - start_time)
    return result

def get_file_id(content):
    # Try to extract meaningful identifier from test vector path
    match = re.search(r'Test *vector *file *= *examples/.*/(encode|decode)/([a-zA-Z0-9_.=+-]+)', content)
    if match:
        block_type, name = match.groups()
        return f"{block_type}_{re.sub(r'[^a-zA-Z0-9_]', '_', name)}"
    
    # Fallback to hash if no path found
    return f"unknown_{hash(content) % 10000}"

def split_log_file(input_log_path):
    preamble = ""
    block_lines = []
    blocks = []
    started = False

    with open(input_log_path, "r") as f:
        for line in f:
            if "Starting Test Suite : BBdev" in line:
                if not started:
                    started = True
                else:
                    blocks.append("\n".join(block_lines))
                    block_lines = []
                block_lines = [line.strip()]
            elif "Test Case :" in line:
                if block_lines:  # If we have previous content, save it
                    blocks.append("\n".join(block_lines))
                    block_lines = []
                block_lines = [line.strip()]
            else:
                if not started:
                    preamble += line
                else:
                    block_lines.append(line.strip())

    if block_lines:
        blocks.append("\n".join(block_lines))

    return preamble.strip(), blocks

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="Path to log file")
    args = parser.parse_args()

    print(f"Processing log file: {args.file}")
    preamble_text, test_blocks = split_log_file(args.file)

    print("Processing preamble...")
    preamble_result = process_log_block(preamble_text, is_preamble=True)
    update_metrics_file(preamble_result)

    print(f"Processing {len(test_blocks)} test blocks...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_log_block, content): content for content in test_blocks}
        for future in as_completed(futures):
            content = futures[future]
            block_id = get_file_id(content)
            try:
                result = future.result()
                print(f"✓ Processed: {block_id}")
                update_metrics_file(result)
            except Exception as e:
                print(f"✗ Failed to process block {block_id}: {e}")

    total_exec_time = time.time() - start_time
    avg_groq_time = sum(groq_response_times) / len(groq_response_times) if groq_response_times else 0
    avg_parse_time = sum(parsing_times) / len(parsing_times) if parsing_times else 0

    print("\nProcessing complete!")
    print(f"• Total execution time: {total_exec_time:.2f} seconds")
    print(f"• Average GROQ API response time: {avg_groq_time:.2f} seconds")
    print(f"• Average parsing time per block: {avg_parse_time:.2f} seconds")
    print(f"• Results saved to: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()