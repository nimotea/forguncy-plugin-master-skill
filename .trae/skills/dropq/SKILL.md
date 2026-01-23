---
name: dropQ
description: "Persists user feedback, bug reports, and suggestions for skills in a structured, AI-readable log format. Use when the user provides structured feedback (e.g., \"[wellog-viz 技能优化建议]\") or generic suggestions for skill improvements."
---

# Feedback Collector (dropQ)

## Overview

This skill standardizes and persists user feedback for skills engineering. It parses structured user input and logs it to a JSONL file (`feedback_logs.jsonl`) in the workspace root, ensuring the data is AI-readable and easy to integrate with downstream analysis tools.

## Architecture & Mechanism

The dropQ skill functions as a bridge between unstructured user feedback and structured data analysis.

1.  **Parsing**: The skill (Trae) first parses the natural language input, extracting key information based on predefined markers (like `[问题/建议类型]`, `[场景还原]`).
2.  **Structuring**: This information is converted into a standard JSON object.
3.  **Persistence Layer**: The JSON object is passed to a Python script (`log_feedback.py`).
4.  **Storage**: The script appends the JSON object as a new line in the `feedback_logs.jsonl` file located in the workspace root. This file acts as an append-only log.

This mechanism ensures:
- **Decoupling**: The storage logic is isolated in the script.
- **Reliability**: JSONL format prevents data corruption and is easy to stream-process.
- **Traceability**: Each entry is automatically timestamped by the script.

## Configuration

The skill behavior can be configured primarily through the `log_feedback.py` script arguments.

### Output File Location
Logs are written to `feedback_logs.jsonl` in the workspace root.
**The filename is fixed and cannot be changed.**

**IMPORTANT:** You MUST always explicitly provide the current project root directory using the `--project-root` argument. This ensures logs are saved in the correct location regardless of where the script is executed from.

```bash
python <script_path> '<json_string>' --project-root <absolute_project_root>
```

### JSON Schema
While the skill suggests a standard schema (title, type, scenario, etc.), the underlying mechanism supports any valid JSON object.
- **Standard Fields**: `title`, `type`, `scenario`, `pain_point`, `suggestion`.
- **Custom Fields**: You can extract and include additional fields (e.g., `priority`, `author`) in the JSON object if the user provides them.

## Workflow

1.  **Analyze Input**: Check if the user input follows the standard feedback format (e.g., `[问题/建议类型]`, `[场景还原]`, etc.).
2.  **Extract Data**: Parse the input into a JSON object.
3.  **Identify Paths**:
    - Determine the absolute path of the current project root.
    - Locate the `log_feedback.py` script. It is typically found in the `scripts/` directory of this skill.
4.  **Persist**: Run the `log_feedback.py` script with the `--project-root` argument.
5.  **Confirm**: Notify the user that the feedback has been recorded.

## Usage

### 1. Extracting Feedback

When the user provides feedback, extract the following fields into a JSON object.
**Important:**
1. Do NOT summarize or truncate the content. Preserve the original details, including error stacks and code snippets.
2. Ignore any internal thinking process, `<think>` tags, or system artifacts. Only extract the explicit user-provided content.

- `title`: The title of the feedback (e.g., "wellog-viz 技能优化建议").
- `type`: The type of issue (e.g., "易用性改进 / 缺陷修复").
- `scenario`: The "[场景还原]" section (Keep full details).
- `pain_point`: The "[现状痛点]" section (Keep full details).
- `suggestion`: The "[改进建议]" section (Keep full details).
- `raw_content`: The full raw text of the user's input (optional, if context is complex).

**Example JSON:**

```json
{
  "title": "wellog-viz 技能优化建议",
  "type": "易用性改进",
  "scenario": "1. 初始化流程...",
  "pain_point": "1. 生命周期脆弱...",
  "suggestion": "1. 增加状态守卫..."
}
```

### 2. Logging Feedback

Execute the logging script with the JSON string and the project root.

**Recommendation for Complex Content:**
For complex JSON content (containing spaces, newlines, or quotes) or Windows environments, **it is strongly recommended to write the JSON to a temporary file first**, and then pass the file path to the script.

**Option A: Passing JSON directly (Simple cases)**
```bash
python skills/dropQ/scripts/log_feedback.py '{"title": "Simple Test"}' --project-root <absolute_project_root>
```

**Option B: Using a temporary file (Recommended for stability)**
1. Write the JSON content to a temporary file (e.g., `temp_feedback.json`) in the project root.
2. Run the script with the file path:
```bash
python skills/dropQ/scripts/log_feedback.py <absolute_path_to_temp_file> --project-root <absolute_project_root>
```
3. Delete the temporary file.

### 3. Confirmation

After the script runs successfully, confirm to the user:
"Feedback has been successfully logged to `feedback_logs.jsonl`."

## Resources

### scripts/

- `log_feedback.py`: Appends the JSON feedback entry to `feedback_logs.jsonl` with a timestamp.