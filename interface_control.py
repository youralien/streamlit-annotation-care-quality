#Annotation Interface for Control Group

import streamlit as st
import streamlit.components.v1 as components
import json
from data_utils import *
import os

st.set_page_config(layout="wide")

STATE_FILENAME_PREFIX = "state_control_eval"
LOCAL_TESTCASES_FILENAME = "all_control_dialogues.json"

# Change it to True when you want to store on Google Cloud
save_on_cloud = True
if save_on_cloud:
    BUCKET_NAME = st.secrets.filenames["bucket_name"]
    DATASET_FILE = st.secrets.filenames["dataset_file"]


# Updates the global dictionary
def update_global_dict(keys, dump=False):
    for key in keys:
        global_dict[key] = st.session_state[key]

    if not dump:
        return

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json", dict(global_dict))
        else:
            json.dump(dict(global_dict), open(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json", 'w'))
    elif "pid" in st.session_state and st.session_state["pid"]:
        if save_on_cloud:
            client = get_gc_client()
            bucket = client.get_bucket(BUCKET_NAME)
            if storage.Blob(bucket=bucket, name=f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json").exists(client):
                return
        else:
            if os.path.exists(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json"):
                return
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json", dict(global_dict))
        else:
            json.dump(dict(global_dict), open(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}.json", dict(global_dict))
        else:
            json.dump(dict(global_dict), open(f'data/{STATE_FILENAME_PREFIX}.json', 'w'))


def example_finished_callback():
    global_dict["current_example_ind"] += 1
    global_dict["current_conversation_number"] = st.session_state["current_conversation_number"]
    next_example_index = global_dict["current_example_ind"]

    if next_example_index < len(global_dict["testcases"]):
        next_testcase = testcases[global_dict["testcases"][next_example_index]]
        # if next_testcase.get("therapist_index", 0) == 0:  # New conversation
        #     st.session_state["current_conversation_number"] += 1

    # Save the state
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json", dict(global_dict))
        else:
            json.dump(dict(global_dict), open(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}.json", dict(global_dict))
        else:
            json.dump(dict(global_dict), open(f'data/{STATE_FILENAME_PREFIX}.json', 'w'))
    st.session_state["reload"] = True
    js = '''
    <script>
        function scrollToTop() {
            var body = window.parent.document.querySelector(".main");
            body.scrollTop = 0;
        }
        setTimeout(scrollToTop, 300);  // 300 milliseconds delay
    </script>
    '''
    components.html(js)

def get_id():
    """Document Prolific ID"""

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        return True

    col1, col2, col3 = st.columns([2,3,2])
    with col2:
        if "pid" in st.session_state and st.session_state["pid"]:
            st.session_state["logged_in"] = st.session_state["pid"]
            st.session_state["reload"] = True
            return True
        else:
            st.markdown(f'## Annotation Interface')
            st.warning("""Please note that this study may contain conversations related to distressing topics. If you have any questions or concerns about the research goals or your role as an expert annotator, please reach out to our team before proceeding.""", icon="⚠️")
            st.text_input("Email ID", key="pid", on_change=update_global_dict, args=[["pid"], "True"])
            st.session_state["reload"] = True
            return False

def update_strengths():
    example_ind = global_dict["current_example_ind"]
    key = f"strengths_{example_ind}"
    if key in st.session_state:  # Only update if there's actually a selection
        global_dict[key] = st.session_state[key]
        update_global_dict([key], dump=True)

def update_bad_areas():
    example_ind = global_dict["current_example_ind"]
    key = f"badareas_{example_ind}"
    if key in st.session_state:  # Only update if there's actually a selection
        global_dict[key] = st.session_state[key]
        update_global_dict([key], dump=True)

def update_bad_areas_reason():
    example_ind = global_dict["current_example_ind"]

    # Get all the detail keys for the current example's bad areas
    bad_areas = st.session_state.get(f"badareas_{example_ind}", [])

    # Create a dictionary to store all reasons for this example
    reasons_dict = {}
    for area in bad_areas:
        detail_key = f"detail_{example_ind}_{area}"
        if detail_key in st.session_state:
            reasons_dict[area] = st.session_state[detail_key]

    # Update the global dictionary with the reasons
    global_dict[f"bad_areas_reasons_{example_ind}"] = reasons_dict
    update_global_dict([], dump=True)

if __name__ == "__main__":
    # st.write("""
    # <style>
    #     div.row-widget.stRadio > div {
    #         flex-direction: row;
    #         justify-content: center;
    #     }
    #     div.st-bf {
    #         flex-direction: column;
    #     }
    #     div.st-ag {
    #         font-weight: bold;
    #         padding-left: 2px;
    #     }
    #     .border-box {
    #         border: 1px solid #d3d3d3;
    #         border-radius: 5px;
    #         padding: 10px;
    #         margin-bottom: 15px;
    #         background-color: #222021;
    #     }
    # </style>
    # """, unsafe_allow_html=True)

    if "reload" not in st.session_state or st.session_state["reload"]:
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json")
            else:
                global_dict = json.load(open(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['logged_in']}.json", 'r'))
        elif "pid" in st.session_state and st.session_state["pid"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json")
            else:
                global_dict = json.load(open(f"data/{STATE_FILENAME_PREFIX}_{st.session_state['pid']}.json", 'r'))
        else:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/{STATE_FILENAME_PREFIX}.json")
            else:
                global_dict = json.load(open(f'data/{STATE_FILENAME_PREFIX}.json', 'r'))
        st.session_state["reload"] = False
        st.session_state.update(global_dict)
    else:
        global_dict = st.session_state

    if "testcases_text" not in st.session_state:
        if save_on_cloud:
            testcases = read_or_create_json_from_gcs(BUCKET_NAME, DATASET_FILE)
        else:
            testcases = json.load(open(LOCAL_TESTCASES_FILENAME, 'r'))
        st.session_state["testcases_text"] = testcases

    testcases = st.session_state["testcases_text"]

    

    if get_id():

        if "current_conversation_number" not in st.session_state:
            st.session_state["current_conversation_number"] = 1  # Initialize the conversation counter


        example_ind = global_dict["current_example_ind"]
        

        c1, c2 = st.columns(2)

        for key in global_dict:
            st.session_state[key] = global_dict[key]

        # Check if either the current example index or the conversation number exceeds the limit
        if st.session_state["current_example_ind"] >= len(global_dict["testcases"]):
            st.title("Thank you!")
            st.balloons()
            st.success("You have annotated all the examples! 🎉")
            st.success("Here is your completion code: CODE")
        else:
            testcase = testcases[global_dict["testcases"][example_ind]]

            with c1.container():
                # # if "current_conversation_number" not in st.session_state:
                # #     st.session_state["current_conversation_number"] = 1

                if testcase.get("therapist_index", 0) == 0 and example_ind != 0:
                    st.session_state["current_conversation_number"] += 1

                st.header(f"Conversation {st.session_state['current_conversation_number']}")
                st.markdown("""
                    <div class="border-box">
                    <p>Instructions: Below is a <span style="color:#1E90FF;">conversation context</span> for psychotherapy conversation.
                    We will analyze the helper response in <span style="color:#FF4500;">red</span>. 
                    Your task is to read through the conversation to identify the strengths and bad areas of the <span style="color:#FF4500;">response</span>.</p>
                    <p>Disclaimer: The conversations might contain grammatical or structural errors. Please ignore them when annotating.</p>
                    </div>
                    """, unsafe_allow_html=True)

                if 'context' in testcase:
                    if 'therapist_index' in testcase:
                        st.markdown(f"### Segment: {testcase['therapist_index']}")

                    conversation = testcase['context']
                    for line in conversation:
                        st.markdown(f'<span style="color:#1E90FF;">{line}</span>', unsafe_allow_html=True)

                    if 'next' in testcase and len(testcase['next']) > 0:
                        next_line = testcase['next'][0]
                        st.markdown(f'<span style="color:#FF4500;">{next_line}</span>', unsafe_allow_html=True)
                else:
                    st.error("The 'context' key is missing in the testcase.")

            with c2.container():
                with st.container():
                    st.header("Evaluate Helper Response")
                    st.markdown("""
                        <div class="border-box">
                        Questions below assess the different aspects of the last response. 
                        <a href="https://docs.google.com/document/d/1rg3FjczuUtn-_mRqJdQpv7HKauAxvFQD1uIMlKd0-bI/edit?usp=sharing" target="_blank">Click Here to see the ANNOTATION MANUAL</a>
                        </div>
                    """, unsafe_allow_html=True)

                    skill_options = ["Reflections", "Validation", "Empathy", "Questions", "Suggestions", "Self-disclosure", "Session Management", "Professionalism"]
                    st.subheader("For the response, select the :green[strengths]")
                    selected_strengths = st.multiselect(
                        "Select strengths:", options=skill_options, key=f"strengths_{example_ind}", on_change=update_strengths
                    )

                    st.subheader("For the response, select the :red[bad areas]")
                    selected_bad_areas = st.multiselect(
                        "Select bad areas:", options=skill_options, key=f"badareas_{example_ind}", on_change=update_bad_areas
                    )

                    st.subheader("Provide more details for selected bad areas")
                    options_per_area = {
                        "Reflections": ["Reflections should have been used here, but weren't", "Reflections were used, but could have been done better", "Reflections were not appropriate here"],
                        "Validation": ["Validation should have been used here, but wasn't", "Validation was used, but could have been done better", "Validation was not appropriate here"],
                        "Questions": ["Questions should have been used here, but weren't", "Questions were used, but could have been phrased better", "Questions were not appropriate here"],
                        "Empathy": ["Empathy should have been used here, but wasn't", "Empathy was used, but could have been done better", "Empathy was not appropriate here"],
                        "Suggestions": ["Suggestions should have been used here, but weren't", "Suggestions were used, but could have been done better", "Suggestions were not appropriate here"],
                        "Self-disclosure": ["Self-disclosure should have been used here, but wasn't", "Self-disclosure was used, but could have been done better", "Self-disclosure was not appropriate here"],
                        "Session Management": ["Session Management should have been used here, but wasn't", "Session Management was used, but could have been done better", "Session Management was not appropriate here"],
                        "Professionalism": ["Professional Tone should have been used here, but wasn't", "Professional Tone was used, but could have been done better", "Professional Tone was not appropriate here"]
                    }
                    for area in selected_bad_areas:
                        detail_key = f"detail_{example_ind}_{area}"
                        st.radio(f"Select the reason for {area} being a bad area:",
                            options=["Reason NOT YET selected (choose from below)"] + options_per_area[area],
                            key=detail_key,
                            on_change=update_bad_areas_reason
                            )
                    st.checkbox('I have finished annotating', key=f"finished_{example_ind}", on_change=update_global_dict, args=[[f"finished_{example_ind}"]])

                    if f"finished_{example_ind}" in st.session_state and st.session_state[f"finished_{example_ind}"]:
                        st.success('We got your annotations!', icon="✅")
                        st.button("Submit final answers and go to next testcase", type="primary", on_click=example_finished_callback)
                        st.session_state["reload"] = True



