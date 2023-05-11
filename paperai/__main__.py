"""Main script for the k8scli-gpt package."""
import os
import sys
from paperai.config import load_config, set_api_key
from paperai.paperai import execute
from paperai.docloader import upload
import streamlit.web.bootstrap
# from dbrun.snowflake_agent import execute,verify_prompt

if __name__ == '__main__':
    config_file_path = 'config.ini'
    if 'OPENAI_API_KEY' not in os.environ and not config_file_path:
        raise ValueError(
            'Environment variable OPENAI_API_KEY not found, you can set it in Project Settings')

    if not config_file_path:
        print("*"*100)
        set_api_key()
    else:
        load_config(config_file_path)

    if sys.argv[1].lower() == "upload":
        upload()
    else:
        # execute(sys.argv[1])
        streamlit.web.bootstrap.run("paperai/newapp.py", sys.argv[1], [], [])
