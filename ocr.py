import re
import easyocr
from typing import List

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Generate filenames dynamically
PATH = "./Pictures/0{i}.png"
filenames = [PATH.format(i=i) for i in range(5)]


def get_text_ocr(filename: str) -> str:
    """
    Extracts text from an image using EasyOCR and processes the content
    to extract relevant information.
    """
    text_content = ""
    try:
        data = reader.readtext(filename)
        start, end = 0, len(data)

        # Determine start position
        for k, (_, text, _) in enumerate(data):
            if text == 'ACTION':
                start = k + 1
                break

        # Determine end position
        for k, (_, text, _) in enumerate(reversed(data)):
            if text == 'Select':
                end = len(data) - k
                break

        # Extract relevant text
        text_content = "\n".join(i[1] for i in data[start:end])

    except Exception as e:
        print(f"Error processing file {filename}: {e}")

    return text_content


def split_by_description(text: str) -> List[List[str]]:
    """
    Splits the extracted text into structured groups based on description.
    """
    delimiter = "If description"
    split_pattern = r"I?f?\s*?description"

    groups = re.split(split_pattern, text, flags=re.I)
    groups = [group.strip().split("\n") for group in groups if group.strip()]

    # Ensure first two groups merge if the first is incomplete
    if len(groups) > 1 and len(groups[0]) < 3:
        groups = [[*groups[0], *groups[1]]] + groups[2:]

    structured_groups = []
    for i, group in enumerate(groups):
        if i == 0:
            structured_groups.append(group[:-1])
        else:
            structured_groups.append([groups[i - 1][-1], *group[:-1]])

    # Post-processing: Remove unwanted actions
    actions_to_remove = ['Select']
    cleaned_groups = []
    for group in structured_groups:
        cleaned_group = [line for line in group if line not in actions_to_remove]
        cleaned_group[1] = delimiter + cleaned_group[1]  # Add delimiter to second element
        cleaned_groups.append(cleaned_group)

    # Post-processing: Merge "Rename" actions properly
    processed_groups = []
    for group in cleaned_groups:
        new_group = group[:]
        for i, line in enumerate(group):
            if line.startswith("Rename"):
                if len(group[i:]) > 2:
                    new_group = group[:i] + [" ".join(group[i:-1])] + [group[-1]]
        processed_groups.append(new_group)

    # Further processing for "If" statements
    final_groups = []
    for group in processed_groups:
        new_group = group[:]
        for i, line in enumerate(group):
            if line.startswith("If "):
                sub = new_group[:i]
                for k, v in enumerate(sub):
                    if v.startswith("If "):
                        new_group = [' '.join(sub[:k])] + [' '.join(sub[k:])] + new_group[i:]
                        break
        final_groups.append(new_group)

    return final_groups


# Example usage
for file in filenames:
    extracted_text = get_text_ocr(file)
    structured_data = split_by_description(extracted_text)
    print("\nProcessed Data:", structured_data)
