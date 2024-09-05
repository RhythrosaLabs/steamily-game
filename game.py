import streamlit as st
import random
from openai import OpenAI
import json

# Initialize OpenAI client
client = None

# Function to generate image using DALL-E 3
def generate_image(prompt):
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

# Function to generate story using GPT-4
def generate_story(prompt, memory):
    try:
        messages = [
            {"role": "system", "content": "You are a creative RPG game master. Generate a short, engaging story segment based on the given prompt and previous events."},
            {"role": "user", "content": f"Previous events: {json.dumps(memory)}\n\nNew prompt: {prompt}"}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating story: {str(e)}")
        return "An error occurred while generating the story."

# Function to generate choices using GPT-4
def generate_choices(story, memory):
    try:
        messages = [
            {"role": "system", "content": "You are a creative RPG game master. Generate three interesting choices for the player based on the given story segment and previous events."},
            {"role": "user", "content": f"Previous events: {json.dumps(memory)}\n\nCurrent story: {story}\n\nProvide three choices for the player."}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        choices = response.choices[0].message.content.split('\n')
        return [choice.strip() for choice in choices if choice.strip()]
    except Exception as e:
        st.error(f"Error generating choices: {str(e)}")
        return ["Continue", "Rest", "Give up"]

# Function to update inventory
def update_inventory(action, memory):
    try:
        messages = [
            {"role": "system", "content": "You are an RPG inventory manager. Update the player's inventory based on their actions and the story."},
            {"role": "user", "content": f"Previous events and inventory: {json.dumps(memory)}\n\nPlayer action: {action}\n\nUpdate the inventory. Add or remove items as necessary. Provide the updated inventory as a JSON object."}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error updating inventory: {str(e)}")
        return memory.get('inventory', {})

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
        character_prompt = f"Generate 4 unique {st.session_state.memory['genre']} RPG character descriptions, each in one sentence. Focus on {', '.join(st.session_state.memory['story_focus'])}."
        characters = generate_story(character_prompt, st.session_state.memory).split('\n')
        character_images = [generate_image(char) for char in characters if char]

        cols = st.columns(4)
        for i, (char, img) in enumerate(zip(characters, character_images)):
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
        initial_prompt = f"Start a {st.session_state.memory['genre']} RPG adventure for this character: {st.session_state.character}. The story should focus on {', '.join(st.session_state.memory['story_focus'])} with a difficulty level of {st.session_state.memory['difficulty']}."
        st.session_state.story = generate_story(initial_prompt, st.session_state.memory)
        st.session_state.memory['events'].append(st.session_state.story)
        st.session_state.choices = generate_choices(st.session_state.story, st.session_state.memory)
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
                new_story = generate_story(f"{st.session_state.story} The player chose to {choice}.", st.session_state.memory)
                st.session_state.memory['events'].append(f"Player chose: {choice}")
                st.session_state.memory['events'].append(new_story)
                st.session_state.story = new_story
                st.session_state.choices = generate_choices(new_story, st.session_state.memory)
                st.session_state.memory['inventory'] = update_inventory(choice, st.session_state.memory)
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
