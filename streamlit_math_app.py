
import streamlit as st
from util.llm.deepseek_invoke import invoke_deepseek_model
from util.llm.claude_invoke import invoke_claude_3_multimodal
from util.llm.llama_invoke import invoke_llamma_multimodal
from util.image_decode import get_image, process_image


def main():
    st.title("Multimodel Math Question Solver on AWS")

    input_method = st.radio("Choose input method:", ("Upload Image", "Enter Text"))
    image_base64 = None
    question_prompt = None

    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image of a math question. Consider option as well if present as part of image.", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = get_image(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            image_base64 = process_image(image)
        else:
            image_base64 = None
    else:
        image_base64 = None
        question_prompt = st.text_area("Enter your math question:")

    if st.button("Solve Question"):
        if image_base64 or question_prompt is not None:
            with st.spinner("Processing..."):
                if input_method == "Upload Image":
                    question_prompt = """
                                        Please extract the question and it's options from the image. 
                                        Also Clearly state the mathematical question presented in this image. 
                                        Make use ot latex tag for any equations. 
                                        Do not solve it or provide tips.
                                        """
                    question = invoke_model(question_prompt,SYSTEM_PROMPT, "claude", image_base64)
                    st.subheader("Extracted Question:")
                    st.write(question)
                    answer_1 = solve_my_question(question=question, model="deepseek")
                    st.subheader("Answer from Deepseek:")
                    st.write(answer_1)

                    answer_2 = solve_my_question(question=question, model="llama")
                    st.subheader("Answer from Llama:")
                    st.write(answer_2)

                    st.subheader("Validation and Critique: (Claude)")
                    validation_result = validate_my_answer(question, answer_1, answer_2, "claude")
                    st.write(validation_result)
                else:
                    question = question_prompt
                    st.subheader("Your Question:")
                    st.write(question)
                    answer_1 = solve_my_question(question=question, model="deepseek")
                    st.subheader("Answer from DeepSeek:")
                    st.write(answer_1)

                    answer_2 = solve_my_question(question=question, model="llama")
                    st.subheader("Answer from Llama:")
                    st.write(answer_2)

                    st.subheader("Validation and Critique: (Claude)")
                    validation_result = validate_my_answer(question_prompt, answer_1, answer_2,"claude")
                    st.write(validation_result)
        else:
            st.warning("Please upload an image or enter a question.")




SYSTEM_PROMPT = """You are a J2EE math expert teacher, you will be getting math questions or doubts from variety of students in an image format. 
                    CAREFULLY Extract math question or doubt from it. Do not hallucinate. If you are unclear about any text, do not make assumption. 
                    Simply respond, can you clarify and ask them to upload clear version of image.

                    once you extract question or doubt from image, Your job is to carefully analyse the questions, build your thought process around what concepts it uses.
                    You explain those concepts in brief, then solve the problem step-by-step in details. 
                    At the end show the final answer along with your confidence level of how correct your approach and solution look like. 
                    When in doubt, please mention it clearly and do not showcase wrong concepts or solution, simply say I may need further assistance with this.
                    """



def solve_my_question(question, model):

    user_prompt = f"""You are an J2EE entrance exam expert teacher helping student in solving their Math Problems..
                    You are helping student solve <question> mentioned below.
                    Provide clear step-by-step ways to solve the <question>.
                    For each step inside, break down each line with detailed steps to make it easier to understand solution.
                    For eg: to solve |A - B| = √(5^2 + 10^2 - 2 × 5 × 10 × cos(30°))
                    Step 1: |A - B| = √(25 + 10^2 - 2 × 5 × 10 × cos(30°))
                    Step 2: |A - B| = √(25 + 100 - 2 × 5 × 10 × cos(30°))
                    Step 3: |A - B| = √(25 + 100 - 10 × 10 × cos(30°))
                    Step 4: |A - B| = √(25 + 100 - 100 × cos(30°))
                    Step 5: |A - B| = √(25 + 100 - 100 × 0.866)
                    Step 6: |A - B| = √(25 + 100 - 86.6)
                    Step 7: |A - B| = √(25 + 13.4)
                    Step 8: |A - B| = √(38.4)

                    <question>
                    {question}
                    </question>
                """
    
    return invoke_model(user_prompt,system_prompt=SYSTEM_PROMPT, model=model)

def validate_my_answer(question, answer_1, answer_2,model):
    validate_prompt = f"""
                        Please validate both the answers if it is correct and in case of wrong where exactly it made wrong decision with step-by-step instruction.
                        
                        Question: 
                        
                        {question}

                        Answer 1: 
                        
                        {answer_1}
                        
                        Answer 2:

                        {answer_2}
                        
                        """
    
    return invoke_model(validate_prompt, SYSTEM_PROMPT, model)

def invoke_model(prompt, system_prompt, model, base64_image_data=None):
    if model == "claude":
        return invoke_claude_3_multimodal(user_prompt=prompt, system_prompt=system_prompt, base64_image_data=base64_image_data)
    elif model == "llama":
        return invoke_llamma_multimodal(user_prompt=prompt, system_prompt=system_prompt, base64_image_data=base64_image_data)
    elif model == "deepseek":
        return invoke_deepseek_model(user_prompt=prompt, system_prompt=system_prompt)

if __name__ == "__main__":
    main()
