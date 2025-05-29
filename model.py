import os
import json
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
import dotenv
dotenv.load_dotenv()

from Schemas import SCHEMA_MAP


os.environ["OPEN_AI_API_KEY"] = os.getenv("OPENAI_API_KEY")



def read_log_file(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Log file not found: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def process_log_file(filepath: str, schema_cls: BaseModel):
    log_content = read_log_file(filepath)
    parser = PydanticOutputParser(pydantic_object=schema_cls)
    model = ChatOpenAI(model_name="gpt-4o", temperature=0)

    prompt = f"""
Extract the metrics from the following log file and output a JSON matching this Pydantic schema:

{json.dumps(schema_cls.model_json_schema(), indent=2)}

Log:
{log_content}

Respond only with JSON.
"""
    response = model([HumanMessage(content=prompt)])
    return parser.parse(response.content)

OUTPUT_DIR = "output_dir"  

def save_output(output_data: dict, original_filename: str, log_type: str):
    # Create the output path: output_dir/log_type/
    output_folder = os.path.join(OUTPUT_DIR, log_type)
    os.makedirs(output_folder, exist_ok=True)

    # Save the output with .json extension
    output_path = os.path.join(output_folder, os.path.splitext(original_filename)[0] + ".json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)


def main():
    user_input = input("Enter a file or folder path: ").strip()
    log_type = input(
        "Enter the log file type (nginx, FIO, Netperf, Redis, MySQL_TPC_C, MySQL_TPC_H, Stream, DGEMM, Iperf, Mariadb_TPC_C, Mariadb_TPC_H, Oracle_TPC_C, Oracle_TPC_H, TCP_RR): "
    ).strip()

    if log_type not in SCHEMA_MAP:
        print(f"Unsupported log type: {log_type}")
        return

    schema_cls = SCHEMA_MAP[log_type]

    if os.path.isdir(user_input):
        # Process all files in the folder
        for filename in os.listdir(user_input):
            file_path = os.path.join(user_input, filename)
            if os.path.isfile(file_path):
                try:
                    result = process_log_file(file_path, schema_cls)
                    filtered_result = result.model_dump(exclude_unset=True)

                    # Save to output directory
                    save_output(filtered_result, filename, log_type)

                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    elif os.path.isfile(user_input):
        try:
            result = process_log_file(user_input, schema_cls)
            filtered_result = result.model_dump(exclude_unset=True)
            print("\nParsed Output:")
            print(json.dumps(filtered_result, indent=2))

            # Save to output directory
            save_output(filtered_result, os.path.basename(user_input), log_type)

        except Exception as e:
            print(f"Error: {e}")

    else:
        print("Invalid file or folder path.")



if __name__ == "__main__":
    main()
