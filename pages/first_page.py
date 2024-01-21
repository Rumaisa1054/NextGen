import os
import streamlit as st
from clarifai.client.model import Model
from clarifai.client.input import Inputs
from clarifai.client.auth import create_stub
from clarifai.client.auth.helper import ClarifaiAuthHelper
from clarifai.client.user import User
from clarifai.modules.css import ClarifaiStreamlitCSS
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from google.protobuf import json_format, timestamp_pb2

st.set_page_config(layout="wide")
ClarifaiStreamlitCSS.insert_default_css(st)

st.title("Clarifai NextGen Nexus App")

def main():

    IMAGE_URL = st.text_input("Paste an image URL to get Started" , value = "https://th.bing.com/th/id/R.41505c0285b04412ab6351a9ec5543c0?rik=ZbtgOlw1vTPJOw&pid=ImgRaw&r=0")
    
    with st.sidebar:
        #Clarifai credentials
        st.subheader( "Add your clarifai pat")
        clarifai_pat = st.text_input("CLARIFAI PAT " , type='password')
    if not clarifai_pat:
        st.warning("PLease enter pat to continue")
    else:
        os.environ['CLARIFAI_PAT'] = clarifai_pat


        prompt = "Extract names of its nutritional components and a rough extimate of their quantity only - I need just names and quantity in json - only json required?"
        image_url = IMAGE_URL
        inference_params = dict(temperature=0.2, max_tokens=100)

        model_prediction = Model("https://clarifai.com/openai/chat-completion/models/openai-gpt-4-vision").predict(
            inputs=[Inputs.get_multimodal_input(input_id="", image_url=image_url, raw_text=prompt)],
            inference_params=inference_params)

        json_string = model_prediction.outputs[0].data.text.raw
        #history = st.text_input("Enter your History" , value = "Back in 2020, I was diagnosed with diabetes. It all started with feeling tired and always needing a drink. My body was like a confused traffic cop with the sugar levels. The doctor said it was Type 2 diabetes, so I had to change my food game.")
        history = st.text_area("Enter your History")
        if st.button("Submit"):
            ######################################################################################################
            # In this section, we set the user authentication, user and app ID, model details, and the URL of
            # the text we want as an input. Change these strings to run your own example.
            ######################################################################################################

            # Your PAT (Personal Access Token) can be found in the portal under Authentification
            PAT = clarifai_pat
            # Specify the correct user_id/app_id pairings
            # Since you're making inferences outside your app's scope
            USER_ID = 'openai'
            APP_ID = 'chat-completion'
            # Change these to whatever model and text URL you want to use
            MODEL_ID = 'GPT-3_5-turbo'
            MODEL_VERSION_ID = '4471f26b3da942dab367fe85bc0f7d21'
            RAW_TEXT = f'You  are a Nutritionist  with 10 years of experience in domain. Write just the 2 question to ask a patient with this History given : {history} - just '
            # To use a hosted text file, assign the url variable
            # TEXT_FILE_URL = 'https://samples.clarifai.com/negative_sentence_12.txt'
            # Or, to use a local text file, assign the url variable
            # TEXT_FILE_LOCATION = 'YOUR_TEXT_FILE_LOCATION_HERE'

            ############################################################################
            # YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
            ############################################################################



            channel = ClarifaiChannel.get_grpc_channel()
            stub = service_pb2_grpc.V2Stub(channel)

            metadata = (('authorization', 'Key ' + PAT),)

            userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

            # To use a local text file, uncomment the following lines
            # with open(TEXT_FILE_LOCATION, "rb") as f:
            #    file_bytes = f.read()

            post_model_outputs_response = stub.PostModelOutputs(
                service_pb2.PostModelOutputsRequest(
                    user_app_id=userDataObject,
                    # The userDataObject is created in the overview and is required when using a PAT
                    model_id=MODEL_ID,
                    version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
                    inputs=[
                        resources_pb2.Input(
                            data=resources_pb2.Data(
                                text=resources_pb2.Text(
                                    raw=RAW_TEXT
                                    # url=TEXT_FILE_URL
                                    # raw=file_bytes
                                )
                            )
                        )
                    ]
                ),
                metadata=metadata
            )
            if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
                print(post_model_outputs_response.status)
                raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

            # Since we have one input, one output will exist here
            output = post_model_outputs_response.outputs[0]
            Q = output.data.text.raw
            ss = "Answer these questions : " + Q
            ans = st.text_area(ss)
            #ans = st.text_input("Answer these questions : ")
            if st.button("Submit-Answer"):
                st.title("Patient History : ")
                st.text(history + "\n" + ans)
                st.title("Food Nutritional Info : ")
                st.text(json_string)
                prompt = f"You are an experienced doctor. Given a patient with History : {history + ans} , Make a strict Suggestion on whether He/she can eat a food Item with nutritional information given : {json_string} or he should striclty avoid eating it"

                ######################################################################################################
                # In this section, we set the user authentication, user and app ID, model details, and the URL of
                # the text we want as an input. Change these strings to run your own example.
                ######################################################################################################

                # Your PAT (Personal Access Token) can be found in the portal under Authentification
                PAT = clarifai_pat
                # Specify the correct user_id/app_id pairings
                # Since you're making inferences outside your app's scope
                USER_ID = 'openai'
                APP_ID = 'chat-completion'
                # Change these to whatever model and text URL you want to use
                MODEL_ID = 'GPT-3_5-turbo'
                MODEL_VERSION_ID = '4471f26b3da942dab367fe85bc0f7d21'
                RAW_TEXT = prompt
                # To use a hosted text file, assign the url variable
                # TEXT_FILE_URL = 'https://samples.clarifai.com/negative_sentence_12.txt'
                # Or, to use a local text file, assign the url variable
                # TEXT_FILE_LOCATION = 'YOUR_TEXT_FILE_LOCATION_HERE'

                ############################################################################
                # YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
                ############################################################################



                channel = ClarifaiChannel.get_grpc_channel()
                stub = service_pb2_grpc.V2Stub(channel)

                metadata = (('authorization', 'Key ' + PAT),)

                userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

                # To use a local text file, uncomment the following lines
                # with open(TEXT_FILE_LOCATION, "rb") as f:
                #    file_bytes = f.read()

                post_model_outputs_response = stub.PostModelOutputs(
                    service_pb2.PostModelOutputsRequest(
                        user_app_id=userDataObject,
                        # The userDataObject is created in the overview and is required when using a PAT
                        model_id=MODEL_ID,
                        version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
                        inputs=[
                            resources_pb2.Input(
                                data=resources_pb2.Data(
                                    text=resources_pb2.Text(
                                        raw=RAW_TEXT
                                        # url=TEXT_FILE_URL
                                        # raw=file_bytes
                                    )
                                )
                            )
                        ]
                    ),
                    metadata=metadata
                )
                if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
                    print(post_model_outputs_response.status)
                    raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

                # Since we have one input, one output will exist here
                output1 = post_model_outputs_response.outputs[0]
                
                st.title(" RECoMMENDATION : ")
                st.text(output1.data.text.raw)

if __name__ == '__main__':
    main()
