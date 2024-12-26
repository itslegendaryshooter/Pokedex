import tkinter as tk
from PIL import Image, ImageTk
import sqlite3

def load_pokemon_data2():
    global pokemon_data
    conn = sqlite3.connect('pokedex.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon")
    pokemon_data = cursor.fetchall()
    conn.close()

def display_pokemon2(pokemon_name, canvas, stats_label):
    pokemon = next((p for p in pokemon_data if p[1].lower() == pokemon_name.lower()), None)
    if pokemon:
        sprite_filename = f"sprites/{pokemon[0]}_{pokemon[1].lower()}.png"
        try:
            img_data = Image.open(sprite_filename)
            img_resized = img_data.resize((150, 150))
            pokemon_image = ImageTk.PhotoImage(img_resized)
            canvas.delete("all") 
            canvas.create_image(0, 0, anchor=tk.NW, image=pokemon_image)

            canvas.image = pokemon_image

            stats_text = (f"HP: {pokemon[5]}\n"
                          f"Attack: {pokemon[7]}\n"
                          f"Defense: {pokemon[8]}\n"
                          f"Type: {pokemon[2]}")
            stats_label.config(text=stats_text)

            print(f"Loaded image: {sprite_filename}")
        except FileNotFoundError:
            canvas.delete("all") 
            stats_label.config(text="")
            print(f"Image not found: {sprite_filename}")
        except Exception as e:
            canvas.delete("all")
            stats_label.config(text="")
            print(f"Error loading image {sprite_filename}: {e}") 
    else:
        canvas.delete("all")  
        stats_label.config(text="Pokémon not found") 
        print(f"Pokémon not found in database: {pokemon_name}") 

def format_types(types):
    """Convert list of types to a readable string."""
    if not types:
        return "Unknown"
    return ", ".join(types).capitalize()
def get_type_advantage(types1, types2):
    """
    Calculate type advantage considering dual types.
    
    Args:
    types1: A list of types for Pokémon 1.
    types2: A list of types for Pokémon 2.
    
    Returns:
    Advantage multiplier based on type effectiveness.
    """
    type_chart = {
        'fire': {'grass': 2, 'water': 0.5, 'electric': 1, 'bug': 2, 'steel': 2, 'fairy': 2},
        'water': {'fire': 2, 'grass': 0.5, 'electric': 1, 'rock': 2, 'ground': 2},
        'grass': {'water': 2, 'fire': 0.5, 'electric': 1, 'rock': 2, 'ground': 2},
        'electric': {'water': 1, 'grass': 1, 'fire': 1, 'ground': 0.5},
        'bug': {'grass': 2, 'fire': 0.5, 'flying': 1},
        'rock': {'fire': 2, 'water': 1, 'grass': 1, 'flying': 1, 'bug': 1},
        'steel': {'fairy': 2, 'rock': 1, 'ice': 2, 'fire': 0.5},
        'fairy': {'dark': 2, 'dragon': 2, 'fighting': 2, 'bug': 1},
        'dark': {'psychic': 2, 'ghost': 2, 'fighting': 0.5, 'fairy': 0.5},
        'psychic': {'fighting': 2, 'poison': 2, 'dark': 0.5},
        'ghost': {'psychic': 2, 'ghost': 2, 'dark': 1},
    }
    
    def get_advantage(type1, type2):
        return type_chart.get(type1, {}).get(type2, 1)

    advantage = 1
    for t1 in types1:
        for t2 in types2:
            advantage *= get_advantage(t1, t2)
    return advantage

def simulate_battle(pokemon1_name, pokemon2_name, result_label, pokemon1_canvas, pokemon2_canvas, pokemon1_stats, pokemon2_stats):
    pokemon1 = next((p for p in pokemon_data if p[1].lower() == pokemon1_name.lower()), None)
    pokemon2 = next((p for p in pokemon_data if p[1].lower() == pokemon2_name.lower()), None)

    if not pokemon1 or not pokemon2:
        result_label.config(text="Error: Pokémon not found!")
        pokemon1_canvas.delete("all")
        pokemon2_canvas.delete("all")
        pokemon1_stats.config(text="")
        pokemon2_stats.config(text="")
        return

    type1 = format_types(pokemon1[2].split(','))
    type2 = format_types(pokemon2[2].split(','))

    type_advantages = [get_type_advantage(type1, t) for t in type2.split(',')]
    max_type_advantage = max(type_advantages) if type_advantages else 1

    pokemon1_total = (pokemon1[5] + pokemon1[7] + pokemon1[8]) * max_type_advantage  # HP + Attack + Defense
    pokemon2_total = pokemon2[5] + pokemon2[7] + pokemon2[8]  # HP + Attack + Defense

    if pokemon1_total > pokemon2_total:
        winner = pokemon1
        loser = pokemon2
        advantage = f"{type1} has an advantage over {type2}"
    elif pokemon2_total > pokemon1_total:
        winner = pokemon2
        loser = pokemon1
        advantage = f"{type2} has an advantage over {type1}"
    else:
        winner = None
        advantage = "It's a tie!"

    if winner:
        result_label.config(text=f"Result: {winner[1]} wins! ({advantage})")
        display_pokemon2(winner[1], pokemon1_canvas, pokemon1_stats)
        display_pokemon2(loser[1], pokemon2_canvas, pokemon2_stats)
    else:
        result_label.config(text="Result: It's a tie!")
        pokemon1_canvas.delete("all")
        pokemon2_canvas.delete("all")
        pokemon1_stats.config(text="")
        pokemon2_stats.config(text="")
def create_gui():
    load_pokemon_data2()

    root = tk.Toplevel()
    root.title("Pokédex Battle Simulator")
    root.geometry("800x600")
    root.configure(bg="#D32F2F")

    main_frame = tk.Frame(root, bg="#D32F2F", bd=2, relief="ridge")
    main_frame.place(relx=0.5, rely=0.5, anchor="center", width=750, height=550)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_rowconfigure(2, weight=1)
    main_frame.grid_rowconfigure(3, weight=1)
    main_frame.grid_rowconfigure(4, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)

    title_label = tk.Label(main_frame, text="Pokédex Battle Simulator", font=("Helvetica", 24, "bold"), bg="#D32F2F", fg="white")
    title_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

    pokemon1_canvas = tk.Canvas(main_frame, bg="#ffffff", width=150, height=150, bd=2, relief="groove")
    pokemon1_canvas.grid(row=1, column=0, padx=20, pady=20, sticky="n")

    pokemon2_canvas = tk.Canvas(main_frame, bg="#ffffff", width=150, height=150, bd=2, relief="groove")
    pokemon2_canvas.grid(row=1, column=2, padx=20, pady=20, sticky="n")

    pokemon1_stats = tk.Label(main_frame, text="", font=("Helvetica", 12), bg="#ff0000", fg="white", justify="left")
    pokemon1_stats.grid(row=2, column=0, padx=20, pady=10, sticky="n")

    pokemon2_stats = tk.Label(main_frame, text="", font=("Helvetica", 12), bg="#ff0000", fg="white", justify="left")
    pokemon2_stats.grid(row=2, column=2, padx=20, pady=10, sticky="n")

    pokemon1_entry = tk.Entry(main_frame, font=("Helvetica", 14), justify="center", relief="groove")
    pokemon1_entry.grid(row=3, column=0, padx=20, pady=10, sticky="n")

    vs_label = tk.Label(main_frame, text="VS", font=("Helvetica", 18, "bold"), bg="#ff0000", fg="white")
    vs_label.grid(row=3, column=1, pady=10, sticky="n")

    pokemon2_entry = tk.Entry(main_frame, font=("Helvetica", 14), justify="center", relief="groove")
    pokemon2_entry.grid(row=3, column=2, padx=20, pady=10, sticky="n")

    battle_button = tk.Button(main_frame, text="Simulate Battle", font=("Helvetica", 16), bg="#4CAF50", fg="white", relief="raised",
                              command=lambda: simulate_battle(pokemon1_entry.get(), pokemon2_entry.get(), result_label, pokemon1_canvas, pokemon2_canvas, pokemon1_stats, pokemon2_stats))
    battle_button.grid(row=4, column=0, columnspan=3, pady=20, sticky="n")

    result_label = tk.Label(main_frame, text="", font=("Helvetica", 18), bg="#ff0000", fg="white")
    result_label.grid(row=5, column=0, columnspan=3, pady=20, sticky="n")

    pokemon1_entry.bind("<Return>", lambda event: display_pokemon2(pokemon1_entry.get(), pokemon1_canvas, pokemon1_stats))
    pokemon2_entry.bind("<Return>", lambda event: display_pokemon2(pokemon2_entry.get(), pokemon2_canvas, pokemon2_stats))

    root.mainloop()
