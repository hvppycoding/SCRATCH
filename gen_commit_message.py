#!/usr/bin/env python3

import subprocess
import sys
import openai

def get_staged_diff():
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout

def main():
    # ⚠️ Replace with your actual API key
    openai.api_key = "YOUR_OPENAI_API_KEY_HERE"

    diff_output = get_staged_diff()
    if not diff_output.strip():
        print("⚠️  No staged changes detected. Aborting.")
        sys.exit(1)

    diff_limited = "\n".join(diff_output.strip().splitlines()[:100])

    messages = [
        {"role": "system", "content": "You are an AI assistant that helps generate git commit messages based on code changes."},
        {"role": "user", "content": f"Suggest an informative commit message by summarizing code changes from the shared command output. The commit message should follow the conventional commit format and provide meaningful context for future readers.\n\nChanges:\n{diff_limited}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=100
        )
    except Exception as e:
        print(f"🚫 OpenAI API request failed: {e}")
        sys.exit(1)

    commit_message = response.choices[0].message["content"].strip() if response.choices else ""

    if not commit_message:
        print("🚫 Failed to generate a commit message from OpenAI.")
        sys.exit(1)

    print("🤖 Suggested commit message:")
    print(commit_message)
    choice = input("Do you want to use this message? (y/n) ").strip().lower()

    if choice != "y":
        print("🛑 Commit aborted by the user.")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("✅ Dry run: Commit message generated, but no commit was made.")
        sys.exit(0)

    commit_result = subprocess.run(["git", "commit", "-m", commit_message])
    if commit_result.returncode != 0:
        print("❌ Commit failed. Aborting.")
        sys.exit(1)

    print(f"✅ Committed with message: {commit_message}")

if __name__ == "__main__":
    main()
