import re

# Regular expressions to capture the necessary text between delimiters
focus_pattern = re.compile(r'Study Focus:(.*?)- Health Benefits:', re.DOTALL)
benefits_pattern = re.compile(r'Health Benefits:(.*?)- Population:', re.DOTALL)
population_pattern = re.compile(r'Population:(.*)', re.DOTALL)


def parse_string_to_list(input_string):
    # Normalize by stripping brackets
    cleaned_string = input_string.strip("[]")

    # Split on commas that are outside of single quotes
    items = re.split(r",\s*(?=(?:[^']*'[^']*')*[^']*$)", cleaned_string)

    # Strip extra spaces and surrounding quotes
    cleaned_items = [item.strip().strip("'") for item in items]

    return cleaned_items


def structure_output(text):
    df_rows = []
    # Extract data from each entry
    if text == None:
        return None

    if '[Insert category number (1-7)]' in text:
        text = text.replace('[Insert category number (1-7)]', '')

    # Search for patterns and extract the necessary part
    focus_match = focus_pattern.search(text)
    benefits_match = benefits_pattern.search(text)
    population_match = population_pattern.search(text)

    focus = focus_match.group(1).strip()
    focus = re.search(r'\d+', focus).group()
    benefits = benefits_match.group(1).strip()
    benefits = benefits.replace("[List or 'None']", '')

    if 'None' in benefits:
        benefits = None
    else:
        benefits = parse_string_to_list(benefits)

    pop = population_match.group(1).strip()
    pop = pop.replace("[List or 'None']", '')
    if pop == '[None]' or pop == "['None']" or pop.startswith('None') or pop.startswith("[None]") or pop.startswith(
            "'None'") or pop.startswith("['None']") or pop.startswith(
            '["None"]') or '- Population: None' in pop or '- None' in pop:
        pop = None
    else:
        pop = parse_string_to_list(pop)

    row = [focus, benefits, pop]
    df_rows.append(row)

    return df_rows