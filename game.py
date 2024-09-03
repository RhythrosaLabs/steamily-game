import streamlit as st
import random
from PIL import Image

# Simulated story generation function
def generate_story(prompt):
    stories = [
        "As you venture deeper into the cave, you discover a glowing crystal formation.",
        "You encounter a group of friendly dwarves who offer to guide you through the cavern.",
        "An underground river blocks your path. You need to find a way to cross it.",
        "You stumble upon an ancient artifact that seems to possess magical properties.",
        "The cave suddenly trembles, and you realize you're in the lair of a sleeping dragon."
    ]
    return random.choice(stories)

# Simulated image generation function
def generate_image(prompt):
    # Create a simple colored rectangle as a placeholder image
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.new('RGB', (300, 200), color=color)
    return img

# Simulated choice generation function
def generate_choices(story):
    choice_sets = [
        ["Examine the crystals", "Look for an exit", "Rest for a while"],
        ["Accept the dwarves' help", "Continue alone", "Ask about the cave's history"],
        ["Try to build a raft", "Look for a bridge", "Attempt to swim across"],
        ["Pick up the artifact", "Leave it alone", "Try to decipher its inscriptions"],
        ["Attempt to sneak past", "Try to communicate with the dragon", "Search for another route"]
    ]
    return random.choice(choice_sets)

def main():
    st.title("AI-Simulated RPG Adventure")

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
        # Generate new story based on choice
        new_story = generate_story(f"{st.session_state.story} The player chose to {choice}.")
        st.session_state.story = new_story
        
        # Generate new choices
        st.session_state.choices = generate_choices(new_story)

        # Instead of using experimental_rerun, we'll use st.rerun()
        st.rerun()

if __name__ == "__main__":
    main()
