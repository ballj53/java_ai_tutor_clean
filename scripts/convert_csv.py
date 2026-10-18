import os
import re
import sys
import pandas as pd

# Default or command-line specified roster file
input_file = sys.argv[1] if len(sys.argv) > 1 else "section2-221-Spring26.csv"
section = None

# If section explicitly provided via command line: python convert_csv.py roster.csv 2
if len(sys.argv) > 2:
    try:
        section = int(sys.argv[2])
    except ValueError:
        section = sys.argv[2]
else:
    # Auto-detect section number from filename (e.g. section2-221-Spring26.csv -> 2)
    match = re.search(r"section\s*(\d+)", input_file, re.IGNORECASE)
    if match:
        section = int(match.group(1))

if os.path.exists(input_file):
    df = pd.read_csv(input_file)
    df_new = pd.DataFrame()

    email_col = next((c for c in ["Email", "email", "EMAIL"] if c in df.columns), None)
    if email_col:
        df_new["email"] = df[email_col]
    else:
        raise KeyError(f"Could not find an email column in {input_file}. Columns found: {list(df.columns)}")

    if "condition" in df.columns:
        df_new["condition"] = df["condition"]
    elif "Condition" in df.columns:
        df_new["condition"] = df["Condition"]
    else:
        df_new["condition"] = (df.index % 2) + 1

    # Extract section from column if present, or assign detected section number
    if "Section" in df.columns:
        df_new["section"] = df["Section"]
    elif "section" in df.columns:
        df_new["section"] = df["section"]
    elif section is not None:
        df_new["section"] = section

    input_dir = os.path.dirname(input_file)
    default_out_name = f"section{section}_cleaned.csv" if section else "cleaned_students.csv"
    output_file = sys.argv[3] if len(sys.argv) > 3 else (os.path.join(input_dir, default_out_name) if input_dir else default_out_name)
    df_new.to_csv(output_file, index=False)
    print(f"✅ Converted {input_file} -> {output_file} ({len(df_new)} rows, Section: {section})")
else:
    print(f"ℹ️ Input file {input_file} not found. Ready to process when roster CSV is provided.")

