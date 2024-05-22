import argparse
import ast
import math

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def compute_savings(pickup_dropoff_points, tweak=True):
    n = len(pickup_dropoff_points)
    savings = []
    for i, (p1_pickup, p1_dropoff) in enumerate(pickup_dropoff_points):
        for j, (p2_pickup, p2_dropoff) in enumerate(pickup_dropoff_points):
            if i != j:
                # normal clark wright
                savings_value = (euclidean_distance((0, 0), p1_pickup) +
                                 euclidean_distance(p1_dropoff, (0, 0)) +
                                 euclidean_distance((0, 0), p2_pickup) +
                                 euclidean_distance(p2_dropoff, (0, 0)) -
                                 euclidean_distance(p1_dropoff, p2_pickup))
                # tweak
                # bias preferentially towards points in a cluster of other similar points
                # the purpose here is to clear the map of junky points so the greedy algorithm doesn't shoot itself in the foot
                # junky in the sense of 'there are plenty of nearly identical pitstops nearby that other routes could take'
                # we are trying to load balance the junk so we don't end up with a small number of great schedules and a bunch of bad ones
                # this heuristic should reduce the number of drivers overall by reducing the pressure from junk
                if tweak:
                    proximity_score = 0
                    for k, (p3_pickup, p3_dropoff) in enumerate(pickup_dropoff_points):
                        if k != i and k != j:
                            proximity_score += (euclidean_distance(p1_pickup, p3_pickup) +
                                                euclidean_distance(p1_dropoff, p3_dropoff) +
                                                euclidean_distance(p2_pickup, p3_pickup) +
                                                euclidean_distance(p2_dropoff, p3_dropoff))
                    proximity_score /= (n - 2) * 4
                    savings_value /= proximity_score
                savings.append((savings_value, i, j))
    return sorted(savings, reverse=True)

def calculate_route_distance(route, loads):
    route_distance = 0
    current_location = (0, 0)
    for load_index in route:
        pickup, dropoff = loads[load_index]['pickup'], loads[load_index]['dropoff']
        route_distance += euclidean_distance(current_location, pickup)
        route_distance += euclidean_distance(pickup, dropoff)
        current_location = dropoff
    route_distance += euclidean_distance(current_location, (0, 0))
    return route_distance

def tweaked_clarke_wright_savings_algorithm(loads, max_route_time=720):  # max_route_time in minutes (12 hours)
    pickup_dropoff_points = [(load['pickup'], load['dropoff']) for load in loads]
    r = []
    for tweak in [True, False]:
        routes = [[i] for i in range(len(loads))]
        savings = compute_savings(pickup_dropoff_points, tweak)
        load_to_route = {i: route for i, route in enumerate(routes)}
        for saving, i, j in savings:
            if load_to_route[i] != load_to_route[j]:
                route_i = load_to_route[i]
                route_j = load_to_route[j]
                combined_route = route_i + route_j
                if calculate_route_distance(combined_route, loads) <= max_route_time:
                    routes.remove(route_i)
                    routes.remove(route_j)
                    routes.append(combined_route)
                    for load_index in combined_route:
                        load_to_route[load_index] = combined_route
        cost = calculate_total_cost(routes, loads)
        r.append((cost, routes))
    win = min(r, key=lambda x: x[0])
    routes = win[1]
    return routes

def calculate_total_cost(routes, loads):
    total_driving_time = 0
    number_of_drivers = len(routes)

    for route in routes:
        route_distance = 0
        current_location = (0, 0)
        for load_index in route:
            pickup, dropoff = loads[load_index]['pickup'], loads[load_index]['dropoff']
            route_distance += euclidean_distance(current_location, pickup)
            route_distance += euclidean_distance(pickup, dropoff)
            current_location = dropoff
        route_distance += euclidean_distance(current_location, (0, 0))
        total_driving_time += route_distance

    total_cost = 500 * number_of_drivers + total_driving_time
    return total_cost

def read_loads_from_file(filename):
    loads = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the header
            parts = line.split()
            load_number = int(parts[0])
            pickup = ast.literal_eval(parts[1])
            dropoff = ast.literal_eval(parts[2])
            loads.append({'loadNumber': load_number, 'pickup': pickup, 'dropoff': dropoff})
    return loads

def main():
    parser = argparse.ArgumentParser(description='VRP solver')
    parser.add_argument('path_to_problem', type=str, help='Path to the file containing the problem data')
    args = parser.parse_args()
    filename = args.path_to_problem
    loads = read_loads_from_file(filename)
    routes = tweaked_clarke_wright_savings_algorithm(loads)
    for route in routes:
        print([index + 1 for index in route])

if __name__ == "__main__":
    main()
