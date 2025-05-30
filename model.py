import os
import json
import argparse
import re
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
from concurrent.futures import ThreadPoolExecutor, as_completed
from Schemas import SCHEMA_MAP
import dotenv
import tiktoken

dotenv.load_dotenv()
os.environ["OPEN_AI_API_KEY"] = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = "output_dir"
TOKEN_LIMIT = 100000  # GPT-4o supports up to ~128k tokens


def normalize_log_type(log_type: str) -> str:
    return re.sub(r'\W+', '', log_type.lower())


def read_log_file(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Log file not found: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_token_count(text: str, model_name: str = "gpt-4o") -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))


def chunk_text_by_tokens(text: str, max_tokens: int, model_name: str = "gpt-4o") -> list[str]:
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk = encoding.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)

    return chunks


def summarize_chunk(chunk: str, model: ChatOpenAI) -> str:
    prompt = f"""
You are a helpful assistant. Summarize the following log chunk for metric extraction:

Log:
{chunk}

Only summarize what's relevant for extracting metrics like latency, throughput, performance, etc.
"""
    response = model.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def extract_metrics_from_summary(summaries: str, schema_cls: type[BaseModel], model: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=schema_cls)
    prompt = f"""
Extract metrics from the summarized logs below using the following JSON schema:

{json.dumps(schema_cls.model_json_schema(), indent=2)}

Summarized Logs:
{summaries}

Rules:
- Respond only with JSON.
- If a metric is not mentioned, do not include it in the response.
"""
    response = model.invoke([HumanMessage(content=prompt)])
    return parser.parse(response.content)


def process_log_file(filepath: str, schema_cls: type[BaseModel]):
    log_content = read_log_file(filepath)
    model = ChatOpenAI(model_name="gpt-4o", temperature=0)

    if get_token_count(log_content) < TOKEN_LIMIT:
        return [extract_metrics_from_summary(log_content, schema_cls, model)]
    else:
        # Step 1: Chunk and summarize
        log_chunks = chunk_text_by_tokens(log_content, max_tokens=4000)
        summaries = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(summarize_chunk, chunk, model) for chunk in log_chunks]
            for future in as_completed(futures):
                try:
                    summaries.append(future.result())
                except Exception as e:
                    print(f"Error summarizing chunk: {e}")

        combined_summary = "\n".join(summaries)

        # Step 2: Extract metrics from combined summaries
        return [extract_metrics_from_summary(combined_summary, schema_cls, model)]


def save_output(output_data: dict, original_filename: str, log_type: str):
    output_folder = os.path.join(OUTPUT_DIR, log_type)
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.splitext(original_filename)[0] + ".json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Saved output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract metrics from benchmark logs using LangChain and OpenAI.")
    parser.add_argument("-f", "--file", required=True, help="Path to a log file or a folder of log files.")
    parser.add_argument("-b", "--benchmark", required=True, help="Benchmark/log type name (e.g., FFMPEG, DGEMM, etc.)")
    args = parser.parse_args()

    user_input = args.file
    raw_log_type = args.benchmark
    log_type = normalize_log_type(raw_log_type)

    if log_type not in SCHEMA_MAP:
        print(f"Unsupported log type: {log_type}")
        print(f"Available types: {', '.join(SCHEMA_MAP.keys())}")
        return

    schema_cls = SCHEMA_MAP[log_type]

    if os.path.isdir(user_input):
        for filename in os.listdir(user_input):
            file_path = os.path.join(user_input, filename)
            if os.path.isfile(file_path):
                try:
                    result = process_log_file(file_path, schema_cls)
                    filtered_result = [r.model_dump(exclude_unset=True) for r in result]
                    save_output(filtered_result, filename, log_type)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    elif os.path.isfile(user_input):
        try:
            result = process_log_file(user_input, schema_cls)
            filtered_result = [r.model_dump(exclude_unset=True) for r in result]
            print("\nParsed Output:")
            print(json.dumps(filtered_result, indent=2))
            save_output(filtered_result, os.path.basename(user_input), log_type)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid file or folder path.")


if __name__ == "__main__":
    main()
