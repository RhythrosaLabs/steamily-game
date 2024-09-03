import streamlit as st
import requests
from PIL import Image
import io

# Placeholder for GPT-4o-mini API call
def generate_story(prompt):
    # In a real implementation, you would make an API call to GPT-4o-mini here
    api_url = "https://api.gpt4o-mini.example.com/generate"  # Replace with actual API endpoint
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    data = {"prompt": prompt, "max_tokens": 100}
    
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["generated_text"]
    else:
        return "Error generating story. Please try again."

# Placeholder for DALLE-3 API call
def generate_image(prompt):
    # In a real implementation, you would make an API call to DALLE-3 here
    api_url = "https://api.dalle3.example.com/generate"  # Replace with actual API endpoint
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    data = {"prompt": prompt, "size": "256x256"}
    
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        image_data = response.content
        return Image.open(io.BytesIO(image_data))
    else:
        # Return a placeholder image if there's an error
        return Image.new('RGB', (256, 256), color = (73, 109, 137))

def main():
    st.title("AI-Powered RPG Adventure")

    # Initialize session state
    if 'story' not in st.session_state:
        st.session_state.story = "You find yourself at the entrance of a mysterious cave..."
    if 'choices' not in st.session_state:
        st.session_state.choices = ["Enter the cave", "Look around", "Leave"]

    # Display current story and image
    st.write(st.session_state.story)
    st.image(generate_image(st.session_state.story))

    # Display choices
    choice = st.radio("What do you want to do?", st.session_state.choices)

    if st.button("Make choice"):
        # Generate new story based on choice using GPT-4o-mini
        new_story = generate_story(f"{st.session_state.story} The player chose to {choice}.")
        st.session_state.story = new_story
        
        # Generate new choices using GPT-4o-mini
        choices_prompt = f"Based on this story: {new_story}, generate three possible actions for the player."
        new_choices = generate_story(choices_prompt).split(", ")  # Assuming the API returns choices separated by commas
        st.session_state.choices = new_choices

        # Force a rerun to update the page
        st.experimental_rerun()

if __name__ == "__main__":
    main()
