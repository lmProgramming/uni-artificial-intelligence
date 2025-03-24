import models
import matplotlib.pyplot as plt

csv_filename = "connection_graph.csv"
separator = ","
try:
    rows = open(f"data/{csv_filename}",
                encoding="utf-8").read().splitlines()[1:]
except:
    rows = open(f"lab01/data/{csv_filename}",
                encoding="utf-8").read().splitlines()[1:]

# Parse rows into CommunicationStep objects and remove duplicates
unique_steps = set()
for row in rows:
    step: models.CommunicationStep = models.CommunicationStep.from_parsed_csv_line(
        list(row.split(separator)))
    unique_steps.add(step.start_stop)  # Add step directly to the set
    unique_steps.add(step.end_stop)  # Add step directly to the set

print("done")

# Convert the set back to a list for further processing
unique_steps = list(unique_steps)

# Plot the map
plt.figure(figsize=(10, 8))
for node in unique_steps:
    plt.scatter(node.location[1], node.location[0],
                color="red", s=10, label=node.name)

# Add labels and legend
plt.title("Visualization of Communication Steps")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(loc="upper right")
plt.grid(True)

# Show the map
plt.show()
