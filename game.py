import streamlit as st
import random
from PIL import Image
import io
import base64

# Function to generate image using DALL-E 3
def generate_image(prompt):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url

# Function to generate story using GPT-4
def generate_story(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative RPG game master. Generate a short, engaging story segment based on the given prompt."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

# Function to generate choices using GPT-4
def generate_choices(story):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative RPG game master. Generate three interesting choices for the player based on the given story segment."},
            {"role": "user", "content": f"Given this story: {story}\nProvide three choices for the player."}
        ]
    )
    choices = response.choices[0].message['content'].split('\n')
    return [choice.strip() for choice in choices if choice.strip()]

def main():
    st.title("AI-Generated RPG Adventure")

    # API Key input
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        openai.api_key = api_key
    else:
        st.warning("Please enter your OpenAI API key to play the game.")
        return

    # Initialize session state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'character_selection'
        st.session_state.character = None
        st.session_state.story = None
        st.session_state.choices = None

    if st.session_state.game_state == 'character_selection':
        st.header("Choose Your Character")
        character_prompt = "Generate 4 unique fantasy RPG character descriptions, each in one sentence."
        characters = generate_story(character_prompt).split('\n')
        character_images = [generate_image(char) for char in characters]

        cols = st.columns(4)
        for i, (char, img) in enumerate(zip(characters, character_images)):
            with cols[i]:
                st.image(img, use_column_width=True)
                st.write(char)
                if st.button(f"Choose Character {i+1}"):
                    st.session_state.character = char
                    st.session_state.game_state = 'game_start'
                    st.rerun()

    elif st.session_state.game_state == 'game_start':
        st.header("Your Adventure Begins")
        initial_prompt = f"Start an RPG adventure for this character: {st.session_state.character}"
        st.session_state.story = generate_story(initial_prompt)
        st.session_state.choices = generate_choices(st.session_state.story)
        st.session_state.game_state = 'playing'
        st.rerun()

    elif st.session_state.game_state == 'playing':
        st.write(st.session_state.story)
        st.image(generate_image(st.session_state.story), use_column_width=True)

        choice = st.radio("What do you want to do?", st.session_state.choices)

        if st.button("Make choice"):
            new_story = generate_story(f"{st.session_state.story} The player chose to {choice}.")
            st.session_state.story = new_story
            st.session_state.choices = generate_choices(new_story)
            st.rerun()

if __name__ == "__main__":
    main()
