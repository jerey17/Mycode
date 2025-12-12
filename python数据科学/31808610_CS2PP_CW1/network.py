def file_to_edge_list(file_name):
    edge_list = set()                   # Use set to avoid duplicates
    # Read the file and extract edges
    with open(file_name, 'r') as file:
        for line in file:
            a, b = map(int, line.strip().split())
            #edge_list.add((min(a, b), max(a, b)))  # to ensure (a, b) and (b, a) are treated the same
            edge_list.add((a,b))
    return list(edge_list)

# Convert edge list to neighbour list
def edge_to_neighbour_list_1(edge_list):
    neighbour_list = {}
    for a, b in edge_list:
        if a not in neighbour_list:
            neighbour_list[a] = set()   #Use set to avoid duplicates
        if b not in neighbour_list:
            neighbour_list[b] = set()
        neighbour_list[a].add(b)     ## Add b to a's neighbours
        neighbour_list[b].add(a)     ## Add a to b's neighbours
    # Convert sets to lists
    return neighbour_list

def edge_to_neighbour_list_2(edge_list):
    neighbour_list = {}
    for a, b in edge_list:
        if a not in neighbour_list:
            neighbour_list[a] = []
        if b not in neighbour_list:
            neighbour_list[b] = []

        neighbour_list[a].append(b)   # Add b to a's neighbours 
        neighbour_list[b].append(a)   # Add a to b's neighbours 
    # Remove duplicates
    for node in neighbour_list:
        neighbour_list[node] = list(set(neighbour_list[node]))
    
    return neighbour_list


def inspect_node(network, node):
    """
    Return neighbors of a node from a network structure.
    Works for both neighbor list (dict) and edge list (list of tuples).
    """
    if isinstance(network, dict):
        return network.get(node, set())
    elif isinstance(network, list):
        return [edge for edge in network if node in edge]
    else:
        raise ValueError("Invalid network")
     

def get_degree_statistics(neighbour_list):
    """
    Compute degree-related statistics of a graph.
    Returns max, min, average, and most common degree.
    """
    degree = [len(neighbours) for neighbours in neighbour_list.values()]
    max_degree = max(degree)
    min_degree = min(degree)
    avg_degree = (lambda x: sum(x) / len(x))(degree)
    most_common_degree = max(set(degree),key=degree.count)

    return (max_degree, min_degree, avg_degree, most_common_degree)

def get_clustering_coefficient(network, node):
    """
    Compute the clustering coefficient of a specified node in an undirected graph.

    Args:
        network (dict): Neighbour list representation of the graph {node: [neighbours]}.
        node (int): The node for which the clustering coefficient is to be computed.

    Returns:
        float: Clustering coefficient value in range [0, 1]. Returns 0.0 if less than 2 neighbours.
    """
    neighbours = list(network.get(node, []))
    k = len(neighbours)
    
    if k < 2:
        return 0.0  # Not enough neighbours to form a triangle

    # Count the number of edges between neighbours
    E_N = 0
    for i in range(k):
        for j in range(i + 1, k):
            ni, nj = neighbours[i], neighbours[j]
            # Check if ni and nj are also neighbours (i.e., there's an edge between them)
            if nj in network.get(ni, []):
                E_N += 1

    # Clustering coefficient formula
    return (2 * E_N) / (k * (k - 1))