import heapq
from collections import defaultdict
import customtkinter as ctk
from tkinter import messagebox, END
import time
import random

# Graph representation using adjacency list
class Graph:
    def __init__(self):  # Correct constructor
        self.graph = defaultdict(list)

    def add_edge(self, city1, city2, road_distance):
        self.graph[city1].append((city2, road_distance))
        self.graph[city2].append((city1, road_distance))

    def remove_edge(self, city1, city2):
        self.graph[city1] = [edge for edge in self.graph[city1] if edge[0] != city2]
        self.graph[city2] = [edge for edge in self.graph[city2] if edge[0] != city1]

    def dijkstra(self, start, animate_func):
        distances = {city: float('inf') for city in self.graph}
        distances[start] = 0
        pq = [(0, start)]
        previous_nodes = {city: None for city in self.graph}
        visited = set()

        while pq:
            current_distance, current_city = heapq.heappop(pq)
            visited.add(current_city)

            animate_func(current_city, visited, previous_nodes, distances)  # Call animation function

            for neighbor, road_distance in self.graph[current_city]:
                if neighbor in visited:
                    continue
                new_distance = current_distance + road_distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_city
                    heapq.heappush(pq, (new_distance, neighbor))

        return distances, previous_nodes

    def shortest_distance_between(self, city1, city2, animate_func):
        distances, previous_nodes = self.dijkstra(city1, animate_func)
        path = []
        current_city = city2
        while current_city is not None:
            path.append(current_city)
            current_city = previous_nodes[current_city]

        path.reverse()
        return distances[city2], path

class App:
    def __init__(self, master):  # Correct constructor
        self.master = master
        self.graph = Graph()
        self.city_positions = {}
        self.master.title("City Road Optimization")
        self.master.geometry("1000x800")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.setup_layout()

    def setup_layout(self):
        # Left frame for input
        self.input_frame = ctk.CTkFrame(self.master)
        self.input_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.input_frame, text="City 1:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=5)
        self.city1_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.city1_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="City 2:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=10, pady=5)
        self.city2_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.city2_entry.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="Distance (km):", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=10, pady=5)
        self.distance_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.distance_entry.grid(row=2, column=1, padx=10, pady=5)

        self.add_distance_button = ctk.CTkButton(self.input_frame, text="Add Distance", command=self.add_edge, fg_color="#4CAF50", font=ctk.CTkFont(size=14))
        self.add_distance_button.grid(row=3, columnspan=2, pady=10)

        self.delete_distance_button = ctk.CTkButton(self.input_frame, text="Delete Distance", command=self.delete_edge, fg_color="#FF5722", font=ctk.CTkFont(size=14))
        self.delete_distance_button.grid(row=4, columnspan=2, pady=5)

        self.calculate_path_button = ctk.CTkButton(self.input_frame, text="Calculate Shortest Path", command=self.calculate_shortest_path, fg_color="#2196F3", font=ctk.CTkFont(size=14))
        self.calculate_path_button.grid(row=5, columnspan=2, pady=10)

        # Right frame for output and visualization
        self.output_frame = ctk.CTkFrame(self.master)
        self.output_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.distances_listbox = ctk.CTkTextbox(self.output_frame, height=150, width=300, font=ctk.CTkFont(size=12))
        self.distances_listbox.pack(pady=10)

        self.result_area = ctk.CTkTextbox(self.output_frame, height=50, width=300, font=ctk.CTkFont(size=12))
        self.result_area.pack(pady=10)

        self.canvas = ctk.CTkCanvas(self.output_frame, width=800, height=600, bg="lightblue")  # Light blue for sky
        self.canvas.pack(pady=10)

    def add_edge(self):
        try:
            city1 = self.city1_entry.get().strip()
            city2 = self.city2_entry.get().strip()
            distance = int(self.distance_entry.get().strip())

            self.graph.add_edge(city1, city2, distance)

            # Assign random positions for cities
            if city1 not in self.city_positions:
                self.city_positions[city1] = self.get_random_position()
            if city2 not in self.city_positions:
                self.city_positions[city2] = self.get_random_position()

            messagebox.showinfo("Success", "Distance added successfully.")
            self.display_distances()
            self.animate_graph()

            self.city1_entry.delete(0, END)
            self.city2_entry.delete(0, END)
            self.distance_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values. Distance should be a number.")

    def get_random_position(self):
        # Generate random positions within the canvas size
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        return x, y

    def delete_edge(self):
        selected_text = self.distances_listbox.get("sel.first", "sel.last")
        if selected_text:
            parts = selected_text.split(":")[0].split(" to ")
            if len(parts) == 2:
                city1, city2 = parts
                self.graph.remove_edge(city1.strip(), city2.strip())
                messagebox.showinfo("Success", "Distance deleted successfully.")
                self.display_distances()
                self.animate_graph()
        else:
            messagebox.showerror("Error", "Please select a distance to delete.")

    def display_distances(self):
        self.distances_listbox.delete("1.0", END)
        for city, roads in self.graph.graph.items():
            for neighbor, distance in roads:
                if city < neighbor:  # Avoid duplicates
                    self.distances_listbox.insert(END, f"{city} to {neighbor}: {distance} km\n")

    def animate_graph(self):
        self.canvas.delete("all")

        # Draw roads and cities
        for city, roads in self.graph.graph.items():
            for neighbor, distance in roads:
                if city in self.city_positions and neighbor in self.city_positions:
                    x1, y1 = self.city_positions[city]
                    x2, y2 = self.city_positions[neighbor]
                    self.draw_line(x1, y1, x2, y2, "black", distance)

        # Draw cities
        for city, (x, y) in self.city_positions.items():
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="yellow")  # Cities as yellow circles
            self.canvas.create_text(x, y, text=city, font=("Arial", 10), fill="black")

    def draw_line(self, x1, y1, x2, y2, color, distance):
        # Draw the line and display the distance
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        self.canvas.create_text(mid_x, mid_y, text=f"{distance} km", font=("Arial", 10), fill="black")

    def calculate_shortest_path(self):
        city1 = self.city1_entry.get().strip()
        city2 = self.city2_entry.get().strip()
        if city1 in self.graph.graph and city2 in self.graph.graph:
            distance, path = self.graph.shortest_distance_between(city1, city2, self.animate_graph)
            if distance == float('inf'):
                self.result_area.delete("1.0", END)
                self.result_area.insert(END, f"No path exists between {city1} and {city2}.")
            else:
                self.result_area.delete("1.0", END)
                self.result_area.insert(END, f"Shortest distance from {city1} to {city2} is {distance} km.\n")
                self.result_area.insert(END, f"Path: {' -> '.join(path)}")
        else:
            messagebox.showerror("Error", "One or both cities do not exist.")

if __name__ == "__main__":  # Correct usage
    root = ctk.CTk()  # Using CustomTkinter CTk
    app = App(root)
    root.mainloop()
