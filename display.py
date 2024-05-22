import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd

def plot_graphs_from_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path) or not file_path.endswith('.txt'):
            continue
        data = pd.read_csv(file_path, sep=' ')
        data['pickup'] = data['pickup'].apply(eval)
        data['dropoff'] = data['dropoff'].apply(eval)
        pickup_x, pickup_y = zip(*data['pickup'])
        dropoff_x, dropoff_y = zip(*data['dropoff'])
        plt.figure(figsize=(10, 8))
        plt.scatter(pickup_x, pickup_y, color='blue', label='Pickup Points')
        plt.scatter(dropoff_x, dropoff_y, color='red', label='Dropoff Points')
        for i, row in data.iterrows():
            plt.annotate(row['loadNumber'], (pickup_x[i], pickup_y[i]), textcoords="offset points", xytext=(0,10), ha='center')
            plt.annotate(row['loadNumber'], (dropoff_x[i], dropoff_y[i]), textcoords="offset points", xytext=(0,10), ha='center')
        plt.title(f'Graph of Pickup and Dropoff Points for {filename}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='display training set')
    parser.add_argument('path_to_training', type=str, help='Path to the training data directory')
    args = parser.parse_args()
    directory = args.path_to_training
    plot_graphs_from_files(directory)
