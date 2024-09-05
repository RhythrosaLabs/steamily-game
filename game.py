import streamlit as st
import random
from openai import OpenAI
import json
import time

# Initialize OpenAI client
client = None

# Caching the OpenAI API calls
@st.cache_data(ttl=3600)
def cached_openai_call(model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

# Function to generate image using DALL-E 3
@st.cache_data(ttl=3600)
def generate_image(prompt):
    with st.spinner("Generating image..."):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt + " Full body portrait with no background, focusing on the character.",
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None

# Combined function to generate story and choices
def generate_story_and_choices(prompt, memory):
    with st.spinner("Generating story and choices..."):
        try:
            messages = [
                {"role": "system", "content": "You are a creative RPG game master. Generate a short, engaging story segment based on the given prompt and previous events. Then, provide three interesting choices for the player."},
                {"role": "user", "content": f"Previous events: {json.dumps(memory)}\n\nNew prompt: {prompt}\n\nProvide the story followed by three choices for the player."}
            ]
            response = cached_openai_call("gpt-4o-mini", messages)
            parts = response.split("\n\nChoices:")
            story = parts[0].strip()
            choices = parts[1].strip().split("\n") if len(parts) > 1 else ["Continue", "Rest", "Give up"]
            return story, [choice.strip() for choice in choices if choice.strip()]
        except Exception as e:
            st.error(f"Error generating story and choices: {str(e)}")
            return "An error occurred while generating the story.", ["Continue", "Rest", "Give up"]

# Function to update inventory and generate next story segment
def update_inventory_and_continue(action, memory):
    with st.spinner("Updating inventory and continuing the story..."):
        try:
            messages = [
                {"role": "system", "content": "You are an RPG game master and inventory manager. Update the player's inventory based on their actions and the story, then continue the story and provide new choices."},
                {"role": "user", "content": f"Previous events and inventory: {json.dumps(memory)}\n\nPlayer action: {action}\n\nUpdate the inventory, continue the story, and provide three new choices for the player."}
            ]
            response = cached_openai_call("gpt-4o-mini", messages)
            parts = response.split("\n\n")
            inventory = json.loads(parts[0])
            story = parts[1]
            choices = parts[2].split("\n") if len(parts) > 2 else ["Continue", "Rest", "Give up"]
            return inventory, story, [choice.strip() for choice in choices if choice.strip()]
        except Exception as e:
            st.error(f"Error updating inventory and continuing story: {str(e)}")
            return memory.get('inventory', {}), "An error occurred while updating the story.", ["Continue", "Rest", "Give up"]

def main():
    global client
    st.title("AI-Generated RPG Adventure")

    # API Key input
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            client.models.list()
        except Exception as e:
            st.error(f"Invalid API key: {str(e)}")
            return
    else:
        st.warning("Please enter your OpenAI API key to play the game.")
        return

    # Initialize session state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'begin'
        st.session_state.character = None
        st.session_state.story = None
        st.session_state.choices = None
        st.session_state.memory = {'events': [], 'inventory': {}}

    if st.session_state.game_state == 'begin':
        st.header("Welcome to the AI-Generated RPG Adventure!")
        st.write("Customize your adventure before you begin:")
        
        genre = st.selectbox("Choose your adventure genre:", 
                             ["Fantasy", "Sci-Fi", "Post-Apocalyptic", "Steampunk", "Modern"])
        
        difficulty = st.slider("Select difficulty level:", 1, 5, 3)
        
        story_focus = st.multiselect("Select story focus (max 2):", 
                                     ["Combat", "Exploration", "Puzzle-solving", "Character interaction", "Resource management"],
                                     default=["Exploration"],
                                     max_selections=2)
        
        if st.button("Begin Adventure"):
            st.session_state.memory['genre'] = genre
            st.session_state.memory['difficulty'] = difficulty
            st.session_state.memory['story_focus'] = story_focus
            st.session_state.game_state = 'character_selection'
            st.rerun()

    elif st.session_state.game_state == 'character_selection':
        st.header("Choose Your Character")
        
        if 'characters' not in st.session_state:
            with st.spinner("Generating characters..."):
                character_prompt = f"Generate 4 unique {st.session_state.memory['genre']} RPG character descriptions, each in one sentence. Focus on {', '.join(st.session_state.memory['story_focus'])}."
                st.session_state.characters = cached_openai_call("gpt-4o-mini", [{"role": "user", "content": character_prompt}]).split('\n')
                st.session_state.character_images = [generate_image(char) for char in st.session_state.characters if char]

        cols = st.columns(4)
        for i, (char, img) in enumerate(zip(st.session_state.characters, st.session_state.character_images)):
            with cols[i]:
                if img:
                    st.image(img, use_column_width=True)
                st.write(char)
                if st.button(f"Choose Character {i+1}"):
                    st.session_state.character = char
                    st.session_state.memory['events'].append(f"Character selected: {char}")
                    st.session_state.game_state = 'game_start'
                    st.rerun()

    elif st.session_state.game_state == 'game_start':
        st.header("Your Adventure Begins")
        with st.spinner("Starting your adventure..."):
            initial_prompt = f"Start a {st.session_state.memory['genre']} RPG adventure for this character: {st.session_state.character}. The story should focus on {', '.join(st.session_state.memory['story_focus'])} with a difficulty level of {st.session_state.memory['difficulty']}."
            st.session_state.story, st.session_state.choices = generate_story_and_choices(initial_prompt, st.session_state.memory)
            st.session_state.memory['events'].append(st.session_state.story)
        st.session_state.game_state = 'playing'
        st.rerun()

    elif st.session_state.game_state == 'playing':
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(st.session_state.story)
            story_image = generate_image(st.session_state.story)
            if story_image:
                st.image(story_image, use_column_width=True)

            choice = st.radio("What do you want to do?", st.session_state.choices)

            if st.button("Make choice"):
                with st.spinner("Processing your choice..."):
                    inventory, new_story, new_choices = update_inventory_and_continue(choice, st.session_state.memory)
                    st.session_state.memory['inventory'] = inventory
                    st.session_state.memory['events'].append(f"Player chose: {choice}")
                    st.session_state.memory['events'].append(new_story)
                    st.session_state.story = new_story
                    st.session_state.choices = new_choices
                st.rerun()

        with col2:
            st.subheader("Inventory")
            inventory = st.session_state.memory.get('inventory', {})
            for item, quantity in inventory.items():
                st.write(f"{item}: {quantity}")

            st.subheader("Event Log")
            for event in st.session_state.memory['events'][-5:]:
                st.write(event)

if __name__ == "__main__":
    main()
