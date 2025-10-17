import google.generativeai as genai
from config1 import API_KEY
import json
import os

# Configure Gemini
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_prompt(jd_text, cv_text):
    return (
        f"Compare this Job Description with this Candidate CV and provide a JSON result.\n"
        f"Job Description:\n{jd_text}\n\nCandidate CV:\n{cv_text}\n\n"
        f"Provide a JSON with HR focus including: match_score (0-100), summary, strengths (list), "
        f"missing_requirements (list), and verdict (strong match | possible match | not a match)."
    )

def evaluate_cv(jd_text, cv_text):
    prompt = generate_prompt(jd_text, cv_text)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.3}
    )
    return response.text

def generate_report(cv_json, cv_index):
    summary = f"# CV{cv_index} Matching Report\n\n"
    summary += f"**Match Score:** {cv_json.get('match_score')}\n\n"
    summary += f"**Summary:** {cv_json.get('summary')}\n\n"
    summary += "**Strengths:**\n"
    for s in cv_json.get('strengths', []):
        summary += f"- {s}\n"
    summary += "\n**Missing Requirements:**\n"
    for m in cv_json.get('missing_requirements', []):
        summary += f"- {m}\n"
    summary += f"\n**Verdict:** {cv_json.get('verdict')}\n"
    return summary

def clean_json_response(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Remove the first line if it starts with ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove the last line if it starts with ```
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text

if __name__ == "__main__":
    jd_path = r"C:\Users\krumk\Documents\VSCode_prog_datorium\llm_api_project\cv\sample_inputs\jd.txt"
    cv_paths = [r"C:\Users\krumk\Documents\VSCode_prog_datorium\llm_api_project\cv\sample_inputs\cv1.txt", r"C:\Users\krumk\Documents\VSCode_prog_datorium\llm_api_project\cv\sample_inputs\cv2.txt", r"C:\Users\krumk\Documents\VSCode_prog_datorium\llm_api_project\cv\sample_inputs\cv3.txt"]

    jd_text = read_file(jd_path)

    os.makedirs("outputs", exist_ok=True)

    for i, cv_path in enumerate(cv_paths, start=1):
        cv_text = read_file(cv_path)

        # Get Gemini model evaluation (JSON string assumed)
        result_text = evaluate_cv(jd_text, cv_text)
        cleaned_text = clean_json_response(result_text)
        
        # Parse JSON response from model output
        try:
            cv_result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for CV{i}. Output was:\n{result_text}")
            continue

        # Save JSON result
        json_path = f"outputs/cv{i}.json"
        write_file(json_path, json.dumps(cv_result, indent=2, ensure_ascii=False))

        # Generate and save Markdown report
        report_md = generate_report(cv_result, i)
        report_path = f"outputs/cv{i}_report.md"
        write_file(report_path, report_md)

        print(f"Processed CV{i}: JSON and report saved.")
