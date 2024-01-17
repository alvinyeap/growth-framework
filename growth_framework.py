import streamlit as st
import pandas as pd
import openai
import json

st.title("Growth Framework")

if 'employee_name' not in st.session_state:
    st.session_state['employee_name'] = "Employees"
if 'num_levels' not in st.session_state:
    st.session_state['num_levels'] = "6"
if 'num_attrs' not in st.session_state:
    st.session_state["num_attrs"] = "3"
if 'levels' not in st.session_state:
    st.session_state["levels"] = [f"L{l+1}" for l in range(6)]
if 'attributes' not in st.session_state:
    st.session_state["attributes"] = [
        {"name": "", "description": ""} for _ in range(3)
    ]

c1, c2, c3 = st.columns(3)
with c1:
    if employee_name := st.text_input("What do you call employees?", placeholder="Employees"):
        st.session_state['employee_name'] = employee_name
with c2:
    if num_levels := st.text_input("Number of seniority levels", placeholder="6"):
        st.session_state['num_levels'] = num_levels
        st.session_state["levels"] = [
            f"L{l+1}" for l in range(int(num_levels))]
with c3:
    if num_attrs := st.text_input("Number of attributes", placeholder="3"):
        st.session_state['num_attrs'] = num_attrs
        st.session_state["attributes"] = [
            {"name": "", "description": ""} for _ in range(int(num_attrs))
        ]


with st.expander("Seniority Levels"):
    num_levels = int(st.session_state['num_levels'])
    levels = [f"L{l+1}" for l in range(num_levels)]
    for l in range(num_levels):
        levels[l] = st.text_input(f"Level {l+1}", placeholder=f"L{l+1}")
        if levels[l]:
            st.session_state['levels'][l] = levels[l]
    # st.markdown(st.session_state["levels"])


with st.expander("Attributes"):
    num_attrs = int(st.session_state['num_attrs'])
    attributes = [{"name": "", "description": ""} for _ in range(num_attrs)]
    c1, c2 = st.columns([30, 70])
    for a in range(num_attrs):
        with c1:
            attributes[a]["name"] = st.text_input(f"Attribute {a+1} Name")
            if attributes[a]["name"] != "":
                st.session_state["attributes"][a]["name"] = attributes[a]["name"]
        with c2:
            attributes[a]["description"] = st.text_input(
                f"Attribute {a+1} Description"
            )
            if attributes[a]["description"] != "":
                st.session_state["attributes"][a]["description"] = attributes[a]["description"]
    # st.markdown(st.session_state["attributes"])


# attributes = {
#     "Communication": "The ability to effectively communicate, both in writing and verbally, is crucial. This includes being able to explain ideas clearly, listen to others, and engage in constructive discussions.",
#     "Teamwork": "Working well in a team setting and collaborating with others is essential in most workplaces. This involves being able to work alongside others, contribute to group efforts, and support team members.",
#     "Problem-Solving Abilities": "The capacity to identify problems, think critically, and come up with viable solutions is highly valued. This skill is important for navigating challenges and finding effective ways to overcome them.",
#     "Adaptability": "The business world is constantly changing, so being able to adapt to new situations and be flexible in the face of change is important. This includes being open to new ideas, willing to learn, and capable of adjusting to shifting priorities or tasks.",
#     "Professionalism": "Displaying a strong sense of professionalism and a solid work ethic is crucial. This encompasses being reliable, punctual, responsible, and showing dedication to one’s job and the company’s values and goals."
# }

attributes_str = "\n".join(
    [
        f"{d['name']}: {d['description']}"
        for d in st.session_state["attributes"]
    ]
)

PROMPT = (
    f"""
    Write a growth framework for a fictional company.
    The collective noun for employees at this company is {employee_name}.
    The company has {num_levels} seniority levels: {levels}.
    In our company we have professional functions: HR, Finance, Legal, Sales, Marketing, Engineering, Design, Product, Operations, Customer Support, Customer Onboarding, Customer Retention, IT and Analytics
    The company has the following values or key attributes:
    {attributes_str}\n
    """
    f"""
    Provide your response as a JSON object with the following structure:
    {{
        "growth_framework": [
            {{
                seniority_level: one of {st.session_state['levels']}.
                attributes: [
                    {{
                        attribute_name: the name of the attribute,
                        attribute_competencies: a list of 3-5 competencies that should be demonstrated at this seniority level. These should be generalized across all the mentioned professional functions.
                    }}
                ]
            }},
            ...
        ]
    }}
    """
)


if st.button("Build"):
    messages = [{'role': 'user', 'content': PROMPT}]
    response = openai.chat.completions.create(
        model='gpt-4-1106-preview',
        temperature=0.7,
        messages=messages,
        response_format={"type": "json_object"}
    )

    message = response.choices[0].message.content
    growth_framework = json.loads(message)['growth_framework']

    records = []
    for entry in growth_framework:
        seniority_level = entry["seniority_level"]
        for attribute in entry["attributes"]:
            competencies = [
                f"{i}. {c}"
                for i, c
                in enumerate(attribute["attribute_competencies"])
            ]
            records.append({
                "seniority_level": seniority_level,
                "attribute_name": attribute["attribute_name"],
                "attribute_competencies": '\n'.join(competencies)
            })

    df = pd.DataFrame.from_records(records)
    df = df.pivot(index='attribute_name', columns='seniority_level',
                  values='attribute_competencies')

    st.table(df)
    # st.dataframe(df)
