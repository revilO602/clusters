from bokeh.plotting import figure, show
import random as rn
from Cluster import Cluster
from Cluster import distance
import time
import numpy as np

MIN = - 5000  # Border of the plane
MAX = 5000  # Border of the plane
INIT_DIST = 1500 ** 2   # Minimal distance between initial point (for medoids and centroids)

colors = {0: "orange", 1: "navy", 2: "red", 3: "olive", 4: "black", 5: "tomato", 6: "yellow", 7: "blue",
          8: "brown", 9: "green", 10: "darkmagenta", 11: "magenta", 12: "dimgray", 13: "khaki", 14: "deepskyblue",
          15: "goldenrod", 16: "sienna", 17: "wheat", 18: "cyan", 19: "lime", 20: "deeppink", 21: "lightgray",
          22: "teal", 23: "turquoise", 24: "gold", 25: "rosybrown"}


# Generate 20020 points used for clustering
def generate_start():
    rn.seed()
    points = [rn.sample(range(MIN, MAX + 1), 20),
              rn.sample(range(MIN, MAX + 1), 20)]
    for i in range(19, 20019):
        x_offset = rn.randint(-100, 100)
        y_offset = rn.randint(-100, 100)
        base = rn.randint(0, i)
        points[0].append(points[0][base] + x_offset)
        points[1].append(points[1][base] + y_offset)
    return points

# Create and display a graph of all the points with clusters distinguished by color
def create_graph(clusters):
    plane = figure(x_range=(MIN, MAX), y_range=(MIN, MAX))
    for i, cluster in enumerate(clusters):
        plane.circle(cluster.xs, cluster.ys, color=colors[i % len(colors)])
    show(plane)

# Randomly select initial medoids - if min_dist is True, they will be apart at least by INIT_DIST
def random_medoids(k, points, min_dist=False):
    ref_points = [[], []]
    if min_dist:
        amount = len(points[0])
        i = rn.randint(0, amount-1)
        ref_points = [[points[0][i]],
                      [points[1][i]]]
        bad_indexes = set()
        for i in range(0, k):
            while 1:    # Keep re-generating a point until its far enough from all other points
                index = rn.randint(0, amount-1)
                if index in bad_indexes:
                    continue
                good_point = True
                point_x = points[0][index]
                point_y = points[1][index]
                for j in range(0, len(ref_points[0])):
                    if distance(point_x, point_y, ref_points[0][j], ref_points[1][j]) < INIT_DIST:
                        good_point = False
                        break
                    else:
                        bad_indexes.add(index)
                        if len(bad_indexes) >= amount/2:
                            return random_medoids(k, points, False)
                if good_point:
                    ref_points[0].append(point_x)
                    ref_points[1].append(point_y)
                    break
    else:
        indexes = rn.sample(range(0, len(points[0])), k)
        for i in indexes:
            ref_points[0].append(points[0][i])
            ref_points[1].append((points[1][i]))
    return ref_points

# Randomly select coordinates for initial centroids - if min_dist is True, they will be apart at least by INIT_DIST
def random_centroids(k, min_dist=False):
    if min_dist:
        ref_points = [[rn.randint(MIN, MAX)],
                      [rn.randint(MIN, MAX)]]
        for i in range(0, k):
            while 1:    # Keep re-generating a point until its far enough from all other points
                good_point = True
                point_x = rn.randint(MIN, MAX)
                point_y = rn.randint(MIN, MAX)
                for j in range(0, len(ref_points[0])):
                    if distance(point_x, point_y, ref_points[0][j], ref_points[1][j]) < INIT_DIST:
                        good_point = False
                        break
                if good_point:
                    ref_points[0].append(point_x)
                    ref_points[1].append(point_y)
                    break
    else:
        ref_points = [rn.sample(range(MIN, MAX + 1), k),
                      rn.sample(range(MIN, MAX + 1), k)]
    return ref_points

# Create initial reference points - centroids or medoids
def init_refs(k, points, type, min_dist):
    if type == "centroid":
        return random_centroids(k, min_dist)
    if type == "medoid":
        return random_medoids(k, points, min_dist)

# Create a cluster for every reference point and assign all the nearest points to that cluster
def init_clusters(k, points, ref_points):
    clusters = []
    for j in range(0, k):
        clusters.append(Cluster((ref_points[0][j], ref_points[1][j]), [], [], True))
    amount = len(points[0])
    for i in range(0, amount):
        x = points[0][i]
        y = points[1][i]
        cluster_num = 0
        this_d = distance(x, y, ref_points[0][0], ref_points[1][0])
        for j in range(1, k):
            tmp_d = distance(x, y, ref_points[0][j], ref_points[1][j])
            if tmp_d < this_d:
                this_d = tmp_d
                cluster_num = j
        clusters[cluster_num].xs.append(x)
        clusters[cluster_num].ys.append(y)
    return clusters

# K-means clustering with centroids or medoids (ref_type)
def k_means(k, points, ref_type, min_dist=False):
    ref_points = init_refs(k, points, ref_type, min_dist)
    clusters = init_clusters(k, points, ref_points)  # First k random points
    is_same = False
    while not is_same:  # Stop if no points have switched clusters
        is_same = True
        new_clusters = []
        for cluster in clusters:  # Recalculate reference points
            new_clusters.append(Cluster(cluster.new_ref(ref_type), [], []))
        for cl_i in range(0, k):
            old_cluster = clusters[cl_i]
            new_cluster = new_clusters[cl_i]
            point_amount = len(old_cluster.xs)
            for i in range(0, point_amount):
                best = cl_i
                this_d = distance(old_cluster.xs[i], old_cluster.ys[i],
                                  new_cluster.ref_point[0], new_cluster.ref_point[1])  # Distance from own reference point
                for cl_j in range(0, k):
                    if cl_i != cl_j:
                        diff_cluster = new_clusters[cl_j]
                        tmp_d = distance(old_cluster.xs[i], old_cluster.ys[i],  # Distance from other clusters reference point
                                         diff_cluster.ref_point[0], diff_cluster.ref_point[1])
                        if tmp_d < this_d:
                            is_same = False
                            best = cl_j
                new_clusters[best].xs.append(old_cluster.xs[i])
                new_clusters[best].ys.append(old_cluster.ys[i])
                if best != cl_i:
                    new_clusters[best].changed = True
                    new_clusters[cl_i].changed = True
                    is_same = False
            clusters[cl_i].xs.clear()
            clusters[cl_i].ys.clear()
        clusters = new_clusters
    final_clusters = []
    for cluster in clusters:    # Filter out empty clusters
        if cluster.xs:
            final_clusters.append(cluster)
    return final_clusters


def divisive(k, points):
    clusters = k_means(2, points, "centroid", True)
    is_success = False
    while not is_success:
        clust_am = len(clusters)
        if clust_am >= k:
            break
        new_clusters = []
        is_success = True
        for cluster in clusters:
            if cluster.average_dist() > 500 and clust_am < k:
                is_success = False
                new_points = [cluster.xs, cluster.ys]
                tmp = k_means(2, new_points, "centroid", True)
                clust_am += len(tmp) - 1
                for tmp_cluster in tmp:
                    new_clusters.append(tmp_cluster)
            else:
                new_clusters.append(cluster)
        clusters = new_clusters
    return clusters

def make_matrix(points):
    amount = len(points[0])
    matrix = np.zeros((amount, amount), dtype=np.int32)
    clusters = []
    Av = np.full(amount, -1, dtype=np.int16)
    Ad = np.full(amount, 300000000, dtype=np.int32)
    first_min = 0
    for i in range(0, amount-1):
        clusters.append(Cluster((points[0][i], points[1][i]), [points[0][i]], [points[1][i]]))
        for j in range(i+1, amount):
            tmp_d = distance(points[0][i], points[1][i], points[0][j], points[1][j])
            matrix[i][j] = tmp_d
            matrix[j][i] = tmp_d
            if tmp_d < Ad[i]:
                Ad[i] = tmp_d
                Av[i] = j
            if tmp_d < Ad[j]:
                Ad[j] = tmp_d
                Av[j] = i
            if tmp_d < Ad[first_min]:
                first_min = i
    clusters.append(Cluster((points[0][amount-1], points[1][amount-1]), [points[0][amount-1]], [points[1][amount-1]]))
    return clusters, matrix, Av, Ad, first_min

def recalc_matrix(matrix, v1, v2):
    length = len(matrix[0])
    min_new_d = (-1, 300000000)
    for i in range(0, length):
        new_d = min(matrix[v1][i], matrix[v2][i])
        if i != v1 and i != v2 and new_d < min_new_d[1]:
            min_new_d = (i, new_d)
        matrix[v1][i] = new_d
        matrix[i][v1] = new_d
    matrix = np.delete(matrix, obj=v2, axis=0)
    matrix = np.delete(matrix, obj=v2, axis=1)
    return matrix, min_new_d

def aglomerative(k, points):
    clusters, matrix, Av, Ad, a_min = make_matrix(points)
    is_success = False
    while not is_success:
        v1 = min(a_min, Av[a_min])
        v2 = max(a_min, Av[a_min])
        clusters[v1].merge(clusters[v2])
        clusters.pop(v2)
        matrix, min_new_d = recalc_matrix(matrix, v1, v2)
        Av[v1] = min_new_d[0]
        Ad[v1] = min_new_d[1]
        Av = np.delete(Av, obj=v2)
        Ad = np.delete(Ad, obj=v2)
        min_dist = 500000000
        a_min = -1
        for i in range(0, len(Av)):
            if Av[i] == v2:
                Av[i] = v1
            if Av[i] > v2:
                Av[i] -= 1
            if Ad[i] < min_dist:
                a_min = i
                min_dist = Ad[i]

        if len(clusters) <= k or clusters[v1].average_dist() >= 500:
            is_success = True

    return clusters

def succes_rate(clusters):
    amount = len(clusters)
    good_clusters = 0
    for cluster in clusters:
        if cluster.average_dist() < 500:
            good_clusters += 1
    return good_clusters / amount * 100

points = generate_start()
clusters = []
start = 0
end = 0
while 1:
    try:
        k = int(input("Enter k:\n"))
    except ValueError:
        print("Invalid input (integer expected)\n")
        continue
    command = input("Enter command (c - k-means centroid, m - k-means medoid, a - aglomerative, d - divisive, q - quit):\n")
    if command == 'c':
        start = time.time()
        clusters = k_means(k, points, 'centroid', True)
        end = time.time()
    elif command == 'm':
        start = time.time()
        if k <= 14:     # For bigger k its unrealistic to generate distanced points
            clusters = k_means(k, points, 'medoid', True)
        else:
            clusters = k_means(k, points, 'medoid', False)
        end = time.time()
    elif command == 'd':
        start = time.time()
        clusters = divisive(k, points)
        end = time.time()
    elif command == 'a':
        start = time.time()
        clusters = aglomerative(k, points)
        end = time.time()
    elif command == 'q':
        exit(0)
    if clusters:
        create_graph(clusters)
        print(f'{len(clusters)} clusters made')
        print(f'{end-start} seconds')
        print(f'{succes_rate(clusters)}% success rate')
        exit(0)

