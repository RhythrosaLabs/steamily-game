import streamlit as st
import json

# Function to generate image using DALL·E
def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt + " Full body portrait with no background, focusing on the character.",
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Function to generate story using GPT-4
def generate_story(prompt, memory):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a creative RPG game master. Generate a short, engaging story segment based on the given prompt and previous events."
            },
            {
                "role": "user",
                "content": f"Previous events: {json.dumps(memory)}\n\nNew prompt: {prompt}"
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating story: {str(e)}")
        return "An error occurred while generating the story."

# Function to generate choices using GPT-4
def generate_choices(story, memory):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a creative RPG game master. Generate three interesting choices for the player based on the given story segment and previous events."
            },
            {
                "role": "user",
                "content": f"Previous events: {json.dumps(memory)}\n\nCurrent story: {story}\n\nProvide three choices for the player. Format them as a numbered list."
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        choices_text = response['choices'][0]['message']['content']
        choices = []
        for line in choices_text.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line[0] == '-'):
                choice_text = line.split('.', 1)[-1].strip()
                choices.append(choice_text)
            else:
                choices.append(line)
        return choices
    except Exception as e:
        st.error(f"Error generating choices: {str(e)}")
        return ["Continue", "Rest", "Give up"]

# Function to update inventory
def update_inventory(action, memory):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an RPG inventory manager. Update the player's inventory based on their actions and the story."
            },
            {
                "role": "user",
                "content": f"Previous events and inventory: {json.dumps(memory)}\n\nPlayer action: {action}\n\nUpdate the inventory. Add or remove items as necessary. Provide the updated inventory as a JSON object."
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        updated_inventory_text = response['choices'][0]['message']['content']
        updated_inventory = json.loads(updated_inventory_text)
        return updated_inventory
    except Exception as e:
        st.error(f"Error updating inventory: {str(e)}")
        return memory.get('inventory', {})

def main():
    st.title("AI-Generated RPG Adventure")

    # API Key input
    api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        openai.api_key = api_key
        # Perform a minimal test request to validate the API key
        try:
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}]
            )
        except openai.error.AuthenticationError:
            st.error("Invalid API key. Please check and try again.")
            return
        except Exception as e:
            st.error(f"Error validating API key: {str(e)}")
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
        
        story_focus = st.multiselect("Select up to 2 story focuses:", 
                                     ["Combat", "Exploration", "Puzzle-solving", "Character interaction", "Resource management"],
                                     default=["Exploration"])
        if len(story_focus) > 2:
            st.warning("Please select no more than 2 story focuses.")
        else:
            if st.button("Begin Adventure"):
                st.session_state.memory['genre'] = genre
                st.session_state.memory['difficulty'] = difficulty
                st.session_state.memory['story_focus'] = story_focus
                st.session_state.game_state = 'character_selection'
                st.experimental_rerun()

    elif st.session_state.game_state == 'character_selection':
        st.header("Choose Your Character")
        character_prompt = f"Generate 4 unique {st.session_state.memory['genre']} RPG character descriptions, each in one sentence. Focus on {', '.join(st.session_state.memory['story_focus'])}."
        characters_text = generate_story(character_prompt, st.session_state.memory)
        characters = [line.strip() for line in characters_text.strip().split('\n') if line.strip()]
        if len(characters) < 4:
            st.error("Failed to generate character descriptions.")
            return
        character_images = []
        with st.spinner("Generating character images..."):
            character_images = [generate_image(char) for char in characters]

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
                    st.experimental_rerun()

    elif st.session_state.game_state == 'game_start':
        st.header("Your Adventure Begins")
        initial_prompt = (
            f"Start a {st.session_state.memory['genre']} RPG adventure for this character: {st.session_state.character}. "
            f"The story should focus on {', '.join(st.session_state.memory['story_focus'])} with a difficulty level of {st.session_state.memory['difficulty']}."
        )
        st.session_state.story = generate_story(initial_prompt, st.session_state.memory)
        st.session_state.memory['events'].append(st.session_state.story)
        st.session_state.choices = generate_choices(st.session_state.story, st.session_state.memory)
        st.session_state.game_state = 'playing'
        st.experimental_rerun()

    elif st.session_state.game_state == 'playing':
        st.write(st.session_state.story)
        with st.spinner("Generating image..."):
            story_image = generate_image(st.session_state.story)
        if story_image:
            st.image(story_image, use_column_width=True)

        choice = st.radio("What do you want to do?", st.session_state.choices)

        if st.button("Make choice"):
            st.session_state.memory['events'].append(f"Player chose: {choice}")
            new_story = generate_story(f"{st.session_state.story} The player chose to {choice}.", st.session_state.memory)
            st.session_state.memory['events'].append(new_story)
            st.session_state.story = new_story
            st.session_state.choices = generate_choices(new_story, st.session_state.memory)
            st.session_state.memory['inventory'] = update_inventory(choice, st.session_state.memory)
            st.experimental_rerun()

        # Move inventory and event log to sidebar
        st.sidebar.subheader("Inventory")
        inventory = st.session_state.memory.get('inventory', {})
        if inventory:
            for item, quantity in inventory.items():
                st.sidebar.write(f"{item}: {quantity}")
        else:
            st.sidebar.write("Your inventory is empty.")

        st.sidebar.subheader("Event Log")
        for event in st.session_state.memory['events'][-5:]:
            st.sidebar.write(event)

        # Save and Load game functionality
        st.sidebar.subheader("Game Management")
        if st.sidebar.button("Save Game"):
            game_state_json = json.dumps({
                'game_state': st.session_state.game_state,
                'character': st.session_state.character,
                'story': st.session_state.story,
                'choices': st.session_state.choices,
                'memory': st.session_state.memory
            })
            st.sidebar.text_area("Copy this game state to save your progress:", value=game_state_json)
        
        load_game_state = st.sidebar.text_area("Paste your saved game state here to load the game:")
        if st.sidebar.button("Load Game"):
            try:
                saved_game = json.loads(load_game_state)
                st.session_state.game_state = saved_game['game_state']
                st.session_state.character = saved_game['character']
                st.session_state.story = saved_game['story']
                st.session_state.choices = saved_game['choices']
                st.session_state.memory = saved_game['memory']
                st.success("Game loaded successfully.")
                st.experimental_rerun()
            except json.JSONDecodeError:
                st.error("Invalid game state JSON.")
            except Exception as e:
                st.error(f"Error loading game: {str(e)}")

if __name__ == "__main__":
    main()
