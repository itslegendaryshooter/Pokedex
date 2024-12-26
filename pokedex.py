import tkinter as tk
from tkinter import messagebox,Label,Toplevel,OptionMenu,StringVar,Button,Frame,FLAT,LEFT,PhotoImage
import sqlite3
from utils import create_gui,load_pokemon_data2
import random
from PIL import Image, ImageTk
from io import BytesIO

import requests


pokemon_data = []
filtered_pokemon_data = []
current_pokemon_index = 0
searched_pokemon = ""
selected_region = "All Regions"

type_weaknesses = {
    "Normal": ["Fighting"],
    "Fire": ["Water", "Ground", "Rock"],
    "Water": ["Electric", "Grass"],
    "Electric": ["Ground"],
    "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
    "Ice": ["Fire", "Fighting", "Rock", "Steel"],
    "Fighting": ["Flying", "Psychic", "Fairy"],
    "Poison": ["Ground", "Psychic"],
    "Ground": ["Water", "Ice", "Grass"],
    "Flying": ["Electric", "Ice", "Rock"],
    "Psychic": ["Bug", "Ghost", "Dark"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Rock": ["Water", "Grass", "Fighting", "Ground", "Steel"],
    "Ghost": ["Ghost", "Dark"],
    "Dragon": ["Ice", "Dragon", "Fairy"],
    "Dark": ["Fighting", "Bug", "Fairy"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"]
}
def help():
    
    load_pokemon_data2()
    create_gui()

def load_pokemon_data():
    global pokemon_data
    conn = sqlite3.connect('pokedex.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon")
    pokemon_data = cursor.fetchall()
    conn.close()
    filter_pokemon_by_region()

def filter_pokemon_by_region():
    global filtered_pokemon_data, current_pokemon_index, selected_region
    if selected_region == "All Regions":
        filtered_pokemon_data = pokemon_data
    else:
        filtered_pokemon_data = [pokemon for pokemon in pokemon_data if pokemon[14] == selected_region]
    
    current_pokemon_index = 0
    if filtered_pokemon_data:
        display_pokemon(filtered_pokemon_data[current_pokemon_index])
        update_suggestions_listbox()  
    else:
        result_text.set("No Pokémon found for the selected region.")
        image_label.config(image='')
        prev_button.config(state="disabled")
        next_button.config(state="disabled")

def region_selected(region):
    global selected_region
    selected_region = region
    filter_pokemon_by_region()

def update_suggestions(event):
    typed_text = search_entry.get().strip().lower()
    suggestions_listbox.delete(0, tk.END)

    if typed_text:
        matching_pokemon = [pokemon[1] for pokemon in filtered_pokemon_data if pokemon[1].lower().startswith(typed_text)]
        for name in matching_pokemon:
            suggestions_listbox.insert(tk.END, name)
    else:
        update_suggestions_listbox()

def update_suggestions_listbox():
    suggestions_listbox.delete(0, tk.END)
    for pokemon in filtered_pokemon_data:
        suggestions_listbox.insert(tk.END, pokemon[1])

def select_suggestion(event=None):
    global searched_pokemon
    selection = suggestions_listbox.get(tk.ACTIVE)
    search_entry.delete(0, tk.END)
    search_entry.insert(0, selection)
    search_pokemon()

def search_pokemon():
    global current_pokemon_index, searched_pokemon
    pokemon_name = search_entry.get().strip().lower()
    found = False

    for i, pokemon in enumerate(filtered_pokemon_data):
        if pokemon[1].lower() == pokemon_name:
            searched_pokemon = pokemon_name
            current_pokemon_index = i
            display_pokemon(pokemon)
            found = True
            break
    
    if not found:
        messagebox.showerror("Error", f"Pokémon {pokemon_name.capitalize()} not found!")

def display_pokemon(pokemon):
    evolutions = parse_evolution_chain(pokemon[13])
    
    result_text.set(f"Name: {pokemon[1]}\n\n"
                    f"Type: {pokemon[2]}\n"
                    f"Height: {pokemon[3]}\n"
                    f"Weight: {pokemon[4]}\n"
                    f"Region: {pokemon[14]}\n"
                    f"Evolutions:\n{',\n'.join(evolutions)}")
    
    sprite_filename = f"sprites/{pokemon[0]}_{pokemon[1].lower()}.png"
    try:
        img_data = Image.open(sprite_filename)
        img_resized = img_data.resize((300, 300))
        pokemon_image = ImageTk.PhotoImage(img_resized)
        image_label.config(image=pokemon_image)
        image_label.image = pokemon_image
    except FileNotFoundError:
        image_label.config(image='')

    update_button_states()

def update_button_states():
    evolutions = parse_evolution_chain(filtered_pokemon_data[current_pokemon_index][13])
    current_name = filtered_pokemon_data[current_pokemon_index][1]
    current_evolution_index = evolutions.index(current_name) if current_name in evolutions else 0
    
    prev_button.config(state="normal" if current_evolution_index > 0 else "disabled")
    next_button.config(state="normal" if current_evolution_index < len(evolutions) - 1 else "disabled")

def parse_evolution_chain(evolution_data):
    evolutions = [evo.strip() for evo in evolution_data.split(', ') if evo.strip()]
    evolutions_sorted = sorted(evolutions, key=lambda evo: next(i for i, p in enumerate(filtered_pokemon_data) if p[1] == evo))
    return evolutions_sorted

def next_pokemon():
    global current_pokemon_index
    evolutions = parse_evolution_chain(filtered_pokemon_data[current_pokemon_index][13])
    current_name = filtered_pokemon_data[current_pokemon_index][1]
    current_evolution_index = evolutions.index(current_name)
    
    if current_evolution_index < len(evolutions) - 1:
        next_name = evolutions[current_evolution_index + 1]
        current_pokemon_index = next(i for i, p in enumerate(filtered_pokemon_data) if p[1] == next_name)
        display_pokemon(filtered_pokemon_data[current_pokemon_index])

def previous_pokemon():
    global current_pokemon_index
    evolutions = parse_evolution_chain(filtered_pokemon_data[current_pokemon_index][13])
    current_name = filtered_pokemon_data[current_pokemon_index][1]
    current_evolution_index = evolutions.index(current_name)
    
    if current_evolution_index > 0:
        prev_name = evolutions[current_evolution_index - 1]
        current_pokemon_index = next(i for i, p in enumerate(filtered_pokemon_data) if p[1] == prev_name)
        display_pokemon(filtered_pokemon_data[current_pokemon_index])

def find_worst_opponent():
    current_pokemon = filtered_pokemon_data[current_pokemon_index]
    current_types = current_pokemon[2].split(',')  
    weaknesses = set()  

    for pokemon_type in current_types:
        weaknesses.update(type_weaknesses.get(pokemon_type, []))

    if not weaknesses:
        messagebox.showinfo("Worst Opponent", f"No weaknesses found for types: {', '.join(current_types)}")
        return

    potential_opponents = [pokemon for pokemon in filtered_pokemon_data if any(weak_type in pokemon[2].split(',') for weak_type in weaknesses)]

    if not potential_opponents:
        messagebox.showinfo("Worst Opponent", "No potential opponents found based on type weaknesses.")
        return

    current_total_stats = sum([int(current_pokemon[5]), int(current_pokemon[6]), int(current_pokemon[7]), int(current_pokemon[11])])

    min_stat_difference = current_total_stats * 0.1  
    max_stat_difference = current_total_stats * 1.2  

    best_opponent = None
    best_stat_difference = float('-inf')

    for opponent in potential_opponents:
        opponent_total_stats = sum([int(opponent[5]), int(opponent[6]), int(opponent[7]), int(opponent[11])])
        
        stat_difference = opponent_total_stats - current_total_stats
        
        if min_stat_difference <= stat_difference <= max_stat_difference and stat_difference > best_stat_difference:
            best_stat_difference = stat_difference
            best_opponent = opponent

    if best_opponent:
        open_worst_opponent_window(current_pokemon, best_opponent)
    else:
        messagebox.showinfo("Worst Opponent", "No suitable opponent found within the acceptable range.")


def open_worst_opponent_window(current_pokemon, worst_opponent):
    opponent_window = tk.Toplevel(root)
    opponent_window.title(f"Worst Opponent for {current_pokemon[1]}")
    opponent_window.geometry("700x700")
    opponent_window.config(bg="#D32F2F")

    opponent_label = tk.Label(opponent_window, text=f"Worst Opponent: {worst_opponent[1]}", font=("Courier", 20, "bold"), fg="white", bg="#D32F2F")
    opponent_label.pack(pady=10)

    opponent_image_label = tk.Label(opponent_window, bg="#424242")
    opponent_image_label.pack(pady=10)
    
    sprite_filename = f"sprites/{worst_opponent[0]}_{worst_opponent[1].lower()}.png"
    try:
        img_data = Image.open(sprite_filename)
        img_resized = img_data.resize((200, 200))
        opponent_image = ImageTk.PhotoImage(img_resized)
        opponent_image_label.config(image=opponent_image)
        opponent_image_label.image = opponent_image
    except FileNotFoundError:
        opponent_image_label.config(image='')

    comparison_text = (f"Stats Comparison:\n"
                       f"{current_pokemon[1]} - HP: {current_pokemon[5]}, Attack: {current_pokemon[6]}, Defense: {current_pokemon[7]}, Speed: {current_pokemon[11]}\n"
                       f"{worst_opponent[1]} - HP: {worst_opponent[5]}, Attack: {worst_opponent[6]}, Defense: {worst_opponent[7]}, Speed: {worst_opponent[11]}")
    
    comparison_label = tk.Label(opponent_window, text=comparison_text, font=("Courier", 14), fg="white", bg="#D32F2F", justify="left")
    comparison_label.pack(padx=20, pady=10)
    
    reason_text = f"{worst_opponent[1]} has a type advantage over {current_pokemon[1]} due to {', '.join(type_weaknesses.get(current_pokemon[2].split(',')[0], []))} types."
    
    reason_label = tk.Label(opponent_window, text=reason_text, font=("Courier", 14), fg="white", bg="#D32F2F", wraplength=500)
    reason_label.pack(padx=20, pady=10)

root = tk.Tk()
root.title("Pokédex")
root.geometry("1000x1000")
root.config(bg="#D32F2F")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(5, weight=1)

title_label = tk.Label(root, text="Pokédex", font=("Courier", 32, "bold"), fg="white", bg="#D32F2F")
title_label.grid(row=0, column=0, columnspan=3, pady=10)

search_frame = tk.Frame(root, bg="#D32F2F")
search_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

search_entry = tk.Entry(search_frame, font=("Courier", 14), width=30)
search_entry.pack(side="left", padx=10, pady=5)

search_button = tk.Button(search_frame, text="Search", font=("Courier", 12, "bold"), bg="#0288D1", fg="white", command=search_pokemon)
search_button.pack(side="left")

screen_frame = tk.Frame(root, bg="#424242", bd=10, relief="sunken", width=400, height=400)
screen_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

image_label = tk.Label(screen_frame, bg="#424242")
image_label.pack(pady=10)

result_text = tk.StringVar()
result_label = tk.Label(screen_frame, textvariable=result_text, font=("Courier", 16), fg="white", bg="#424242", justify="left")
result_label.pack(padx=20, pady=10)

button_frame = tk.Frame(root, bg="#D32F2F")
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

prev_button = tk.Button(button_frame, text="<<", font=("Courier", 12, "bold"), bg="#0288D1", fg="white", width=5, command=previous_pokemon)
prev_button.grid(row=0, column=0, padx=20)

next_button = tk.Button(button_frame, text=">>", font=("Courier", 12, "bold"), bg="#0288D1", fg="white", width=5, command=next_pokemon)
next_button.grid(row=0, column=1, padx=20)

recommendations_frame = tk.Frame(root, bg="#D32F2F")
recommendations_frame.grid(row=1, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")
regions_frame = tk.Frame(root, bg="#D32F2F")
regions_frame.grid(row=1, column=3, rowspan=2, padx=10, pady=10, sticky="nsew")

regions_label = tk.Label(regions_frame, text="Regions", font=("Courier", 14, "bold"), fg="white", bg="#D32F2F")
regions_label.pack(pady=5)

regions = ["All Regions", "Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Paldea"]

for region in regions:
    region_button = tk.Button(regions_frame, text=region, font=("Courier", 12, "bold"), bg="#0288D1", fg="white", command=lambda r=region: region_selected(r))
    region_button.pack(fill="both", padx=10, pady=5)


recommendations_label = tk.Label(recommendations_frame, text="Recommendations", font=("Courier", 14, "bold"), fg="white", bg="#D32F2F")
recommendations_label.pack(pady=5)

suggestions_listbox = tk.Listbox(recommendations_frame, font=("Courier", 14), bg="white", fg="black")
suggestions_listbox.pack(fill="both", expand=True)

search_entry.bind("<KeyRelease>", update_suggestions)
suggestions_listbox.bind("<Double-Button-1>", select_suggestion)  # Double click
suggestions_listbox.bind("<Return>", select_suggestion)  # Enter key

worst_opponent_button = tk.Button(root, text="Find Worst Opponent", font=("Courier", 12, "bold"), bg="#F44336", fg="white", command=find_worst_opponent)
worst_opponent_button.grid(row=4, column=0, columnspan=3, pady=10)
battle_button = Button(root, text="Open Battle Simulator", command=help , bg="#F44336", fg="white",)
battle_button.grid(row=4, column=2, columnspan=3, pady=10)
footer_label = tk.Label(root, text="© Pokémon Company", font=("Courier", 12), fg="white", bg="#D32F2F")
footer_label.grid(row=5, column=0, columnspan=3, pady=5)

load_pokemon_data()

if pokemon_data:
    pok = random.randint(0, len(pokemon_data) - 1)
    display_pokemon(pokemon_data[pok])

root.mainloop()
