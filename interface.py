import streamlit as st
import streamlit.components.v1 as components
import json
from data_utils import *
import os
import streamlit_survey as ss

survey = ss.StreamlitSurvey()

BUCKET_NAME = st.secrets.filenames["bucket_name"]
DATASET_FILE = st.secrets.filenames["dataset_file"]

st.set_page_config(layout="wide")

# Change it to True when you want to store on Google Cloud
save_on_cloud = False

# Updates the global dictionary
def update_global_dict(keys, dump=False):
    for key in keys:
        global_dict[key] = st.session_state[key]

    if not dump:
        return

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g7_{st.session_state['logged_in']}.json", global_dict)
        else:
            json.dump(global_dict, open(f"data/state_eval_g7_{st.session_state['logged_in']}.json", 'w'))
    elif "pid" in st.session_state and st.session_state["pid"]:
        if save_on_cloud:
            client = get_gc_client()
            bucket = client.get_bucket(BUCKET_NAME)
            if storage.Blob(bucket=bucket, name=f"data/state_eval_g7_{st.session_state['pid']}.json").exists(client):
                return
        else:
            if os.path.exists(f"data/state_eval_g7_{st.session_state['pid']}.json"):
                # load
                return
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g7_{st.session_state['pid']}.json", global_dict)
        else:
            json.dump(global_dict, open(f"data/state_eval_g7_{st.session_state['pid']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval.json", global_dict)
        else:
            json.dump(global_dict, open(f'data/state_eval.json', 'w'))


def select_main_option():
    st.session_state.selected_main_option = st.session_state.main_option


def example_finished_callback():
    for _ in st.session_state:
        global_dict[_] = st.session_state[_]
    global_dict["current_example_ind"] += 1

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g7_{st.session_state['logged_in']}.json", global_dict) 
        else:
            json.dump(dict(global_dict), open(f"data/state_eval_g7_{st.session_state['logged_in']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval.json", global_dict)
        else:
            json.dump(dict(global_dict), open(f'data/state_eval.json', 'w'))
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


# Function takes in the unique user login and consent
def get_id():
    """Document Prolific ID"""

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        return True

    col1, col2, col3 = st.columns([2,3,2])
    with col2:
        # Checks if the id is in session, if true it marks the user as logged in
        if "pid" in st.session_state and st.session_state["pid"]:
            st.session_state["logged_in"] = st.session_state["pid"]
            st.session_state["reload"] = True
            return True
        # Otherwise asks the user to enter user login
        else:
            st.markdown(f'## Annotation Interface')
            st.warning("""Before you log in and begin annotating data,
                        please ensure you have read and fully understood our research information sheet.
                        :red[**By providing your Prolific ID, you are providing your informed consent**] to
                       participate in this research project. Please note that this study may contain
                       conversations related to distressing topics. If you have any questions or 
                       concerns about the research or your role in it, please reach out to our team before proceeding.""", icon="⚠️")
            st.text_input("Enter your Prolific ID", key="pid", on_change=update_global_dict, args=[["pid"], "True"])
            st.session_state["reload"] = True
            return False


def update_strengths():
    st.session_state["strengths"] = st.session_state[f"strengths_{example_ind}"]

def update_bad_areas():
    selected_bad_areas = st.session_state[f"badareas_{example_ind}"]
    st.session_state["badareas"] = selected_bad_areas

if __name__ == "__main__":

    # global styles for horizontal radio buttons and bordered text
    st.write("""
    <style>
        div.row-widget.stRadio > div {
            flex-direction: row;
            justify-content: center;
        }
        div.st-bf {
            flex-direction: column;
        }
        div.st-ag {
            font-weight: bold;
            padding-left: 2px;
        }
        .border-box {
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
            background-color: #222021;
        }
    </style>
    """, unsafe_allow_html=True)

    if "reload" not in st.session_state or st.session_state["reload"]:
        # Load the state only once at the start
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval_g7_{st.session_state['logged_in']}.json")
            else:
                global_dict = json.load(open(f"data/state_eval_g7_{st.session_state['logged_in']}.json", 'r'))
        elif "pid" in st.session_state and st.session_state["pid"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval_g7_{st.session_state['pid']}.json")
            else:
                global_dict = json.load(open(f"data/state_eval_g7_{st.session_state['pid']}.json", 'r'))
        else:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval.json")
            else:
                global_dict = json.load(open(f'data/state_eval.json', 'r'))
        st.session_state["reload"] = False
        st.session_state.update(global_dict)
    else:
        global_dict = st.session_state

    if "testcases_text" not in st.session_state:
        if save_on_cloud:
            testcases = read_or_create_json_from_gcs(BUCKET_NAME, DATASET_FILE)
            eval_info = read_or_create_json_from_gcs(BUCKET_NAME, f"data/session_level_definitions.json") 
        else:
            testcases = json.load(open('dialogues_1.json', 'r'))
            eval_info = json.load(open('data/session_level_definitions.json', 'r'))
        st.session_state["testcases_text"] = testcases
        st.session_state["eval_text"] = eval_info

    testcases = st.session_state["testcases_text"]
    eval_info = st.session_state["eval_text"]

    if get_id():

        example_ind = global_dict["current_example_ind"]

        c1, c2 = st.columns(2)
        for key in global_dict:
            st.session_state[key] = global_dict[key]

        if example_ind >= len(global_dict["testcases"]):
            st.title("Thank you!")
            st.balloons()
            st.success("You have annotated all the examples! 🎉")
            st.success("Here is your completion code: C17FE3ZT")
        else:
            testcase = testcases[global_dict["testcases"][example_ind]]

            with c1.container():
                st.header("Conversation")
                st.markdown(
                    """
                    <div class="border-box">
                    <p>Instructions: Below is a <span style="color:#1E90FF;">conversation context</span> for psychotherapy conversation. 
                    We will analyze the helper response in <span style="color:#FF4500;">red</span>. 
                    Your task is to read through the conversation to identify the strengths and bad areas of the <span style="color:#FF4500;">response</span>.</p>
                    
                    <p>Disclaimer: The conversations might contain grammatical or structural errors. Please ignore them when annotating.</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
                # Check if 'context' key exists in the testcase dictionary
                if 'context' in testcase:
                    conversation = testcase['context']
                    for line in conversation:
                        st.markdown(f'<span style="color:#1E90FF;">{line}</span>', unsafe_allow_html=True)

                    # Display the next patient line (the one to be evaluated)
                    if 'next' in testcase and len(testcase['next']) > 0:
                        next_line = testcase['next'][0]
                        st.markdown(f'<span style="color:#FF4500;">{next_line}</span>', unsafe_allow_html=True)
                else:
                    st.error("The 'context' key is missing in the testcase.")

                st.markdown('</div>', unsafe_allow_html=True)


            with c2.container():
                with st.container():
                    st.header("Evaluate Helper Response")
                    st.markdown("""
                        <div class="border-box">
                        Questions below assess the different aspects of the flawed response.
                        </div>
                    """, unsafe_allow_html=True)
                    
                    skill_options = ["Empathy", "Questions", "Suggestions", "Validation", "Structure", "Reflection", "Professionalism"]
                    st.subheader("For the response, select the :green[strengths]")
                    selected_strengths = st.multiselect(
                        "Select strengths:", options=skill_options, key=f"strengths_{example_ind}", on_change=update_strengths
                    )

                    # Select bad areas
                    st.subheader("For the response, select the :red[bad areas]")
                    selected_bad_areas = st.multiselect(
                        "Select bad areas:", options=skill_options, key=f"badareas_{example_ind}", on_change=update_bad_areas
                    )
                    st.subheader("Provide more details for selected bad areas")
                    bad_area_details = {}
                    for area in selected_bad_areas:
                        detail_key = f"detail_{example_ind}_{area}"
                        detail = st.selectbox(
                            f"Select the reason for {area} being a bad area:",
                            options=["Did not use at all", "Used inappropriately", "Should not use"],
                            key=detail_key
                        )
                        bad_area_details[area] = detail
                        
                    st.checkbox('I have finished annotating', key=f"finished_{example_ind}", on_change=update_global_dict, args=[[f"finished_{example_ind}"]])

                    if f"finished_{example_ind}" in st.session_state and st.session_state[f"finished_{example_ind}"]:
                        st.success('We got your annotations!', icon="✅")
                        st.button("Submit final answers and go to next testcase", type="primary", on_click=example_finished_callback)
                        st.session_state["reload"] = True