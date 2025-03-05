import openai

client = openai.OpenAI(
    api_key="your_api_key",
    base_url="https://ai-research-proxy.azurewebsites.net",
)


def get_completion(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # model to send to the proxy
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    return response.choices[0].message.content


def get_prompt(compound_name, title, abstract):
    base_prompt = f"""
    Analyze the clinical trial and classify the study focus based on the involvement of {compound_name} or its derivatives.
    1. Classify the study focus:
       - (1) {compound_name} as a Single Compound
       - (2) {compound_name} in Combination Therapy (f.e. with other compounds)
       - (3) A derivative of {compound_name}
       - (4) Comparative Analysis ({compound_name} or its derivatives  vs. Other Compounds or treatments)
       - (5) {compound_name} as Biomarker/Measurement (it is used to assess or track biological effects, not as a treatment)
       - (6) No Involvement ({compound_name} is not studied)
       - (7) Other Focus

    2. Extract any health benefits attributed to {compound_name} (or its derivatives) in the study, excluding adverse events, unrelated findings, or effects from other compounds. If none, return 'None'. Only return keywords.

    3. Extract any terms related to the study population/genotype (f.e. Obese, asian, women, rats, APOE ε4, etc.)

    The output should be structured as:
    - Study Focus: [Insert category number (1-7)]
    - Health Benefits: [List or 'None']
    - Population: [List or 'None']

    No explanation is needed.

    Clinical trial: Title: {title} Abstract: {abstract}
    """
    return base_prompt


def get_prompt_alt(compound_name, title, abstract):
    prompt = f'''Using the information provided in the abstract below, answer the following questions about the clinical trial involving the compound "{compound_name}" (please do not include any explanations or additional text):

        Title: {title} - Abstract: {abstract}

        Questions:
        1. Is the compound "{compound_name}" researched as a treatment in this clinical trial?
        2. If yes, did the compound show positive effects in treating the condition?
        3. What were the conditions it aimed to treat?

        Please provide answers in a structured format as follows:
        1. Compound researched: [Yes/No/Unsure]
        2. Positive effects: [Yes/No/Not Applicable]
        3. Conditions aimed to treat: [Condition Names/Not Applicable]'''
    return prompt