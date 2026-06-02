import io
from contextlib import redirect_stdout

import autogen
import streamlit as st
from dotenv import load_dotenv
from openai import APIConnectionError, RateLimitError


def load_llm_config():
    load_dotenv()
    config_list = autogen.config_list_from_dotenv()

    if not config_list:
        st.error("No model config found. Check OPENAI_API_KEY and OAI_CONFIG_LIST in .env.")
        st.stop()

    return {"config_list": config_list}


def create_agents(llm_config):
    financial_assistant = autogen.AssistantAgent(
        name="Financial_assistant",
        llm_config=llm_config,
        system_message=(
            "You are a financial assistant. Give concise, structured answers. "
            "When exact live data is required, say what data source should be checked."
        ),
    )
    research_assistant = autogen.AssistantAgent(
        name="Researcher",
        llm_config=llm_config,
        system_message="You are a research assistant. Explain likely causes and cite uncertainty clearly.",
    )
    writer = autogen.AssistantAgent(
        name="Writer",
        llm_config=llm_config,
        system_message="You are a professional writer. Reply 'TERMINATE' when done.",
    )
    user = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"last_n_messages": 1, "work_dir": "tasks", "use_docker": False},
    )

    return user, financial_assistant, research_assistant, writer


def run_financial_workflow(price_task, research_task, writing_task, include_table):
    llm_config = load_llm_config()
    user, financial_assistant, research_assistant, writer = create_agents(llm_config)

    carryover = "Include a figure or table of data in the blog post." if include_table else ""
    chat_queue = [
        {
            "recipient": financial_assistant,
            "message": price_task,
            "clear_history": True,
            "summary_method": "last_msg",
        },
        {
            "recipient": research_assistant,
            "message": research_task,
            "summary_method": "reflection_with_llm",
        },
        {
            "recipient": writer,
            "message": writing_task,
            "carryover": carryover,
        },
    ]

    logs = io.StringIO()
    with redirect_stdout(logs):
        chat_results = user.initiate_chats(chat_queue)

    return chat_results, logs.getvalue()


st.set_page_config(page_title="AutoGen Financial Writer", layout="wide")

st.title("AutoGen Financial Writer")

with st.sidebar:
    st.header("Settings")
    include_table = st.checkbox("Ask writer for a table", value=True)
    show_logs = st.checkbox("Show AutoGen console logs", value=False)

st.caption("Runs three AutoGen agents locally: financial assistant, researcher, and writer.")

default_price_task = (
    "What are the current stock prices of NVDA and TSLA, and how have they performed over the past month?"
)
default_research_task = "Investigate possible reasons for the stock performance."
default_writing_task = "Develop an engaging blog post using any information provided."

price_task = st.text_area("Financial task", value=default_price_task, height=100)
research_task = st.text_area("Research task", value=default_research_task, height=90)
writing_task = st.text_area("Writing task", value=default_writing_task, height=90)

run_clicked = st.button("Run agents", type="primary")

if run_clicked:
    if not price_task.strip() or not research_task.strip() or not writing_task.strip():
        st.warning("Please fill in all three tasks before running.")
        st.stop()

    with st.spinner("Running AutoGen agents..."):
        try:
            results, console_logs = run_financial_workflow(
                price_task=price_task.strip(),
                research_task=research_task.strip(),
                writing_task=writing_task.strip(),
                include_table=include_table,
            )
        except RateLimitError:
            st.error(
                "OpenAI API quota error. Check your OpenAI billing/quota or replace OPENAI_API_KEY in .env."
            )
            st.stop()
        except APIConnectionError:
            st.error("OpenAI API connection error. Check your internet, firewall, proxy, or network permissions.")
            st.stop()
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
            st.stop()

    st.success("Done")

    for index, chat_result in enumerate(results, start=1):
        with st.expander(f"Chat {index} summary", expanded=index == len(results)):
            st.markdown(chat_result.summary or "_No summary returned._")

            cost = getattr(chat_result, "cost", None)
            if cost:
                st.code(str(cost), language="text")

            human_input = getattr(chat_result, "human_input", None)
            if human_input:
                st.write("Human input:", human_input)

    if show_logs:
        st.subheader("AutoGen Logs")
        st.code(console_logs, language="text")
else:
    st.info("Edit the tasks, then click Run agents.")
