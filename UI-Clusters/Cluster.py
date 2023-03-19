import math



def distance(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


class Cluster:
    def __init__(self, ref_point, xs, ys, changed=False):
        self.ref_point = ref_point
        self.xs = xs
        self.ys = ys
        self.changed = changed

    def calculate_centroid(self):
        if not self.xs:
            return self.ref_point[0], self.ref_point[1]
        amount = len(self.xs)
        x_total = 0
        y_total = 0
        for i in range(0, amount):
            x_total += self.xs[i]
            y_total += self.ys[i]
        return x_total / amount, y_total / amount

    def calculate_medoid(self):
        if not self.xs:
            return self.ref_point[0], self.ref_point[1]
        amount = len(self.xs)
        min_distance = math.inf
        best = None
        for i in range(0, amount):
            curr_dist = 0
            for j in range(0, amount):
                curr_dist += distance(self.xs[i], self.ys[i],
                                      self.xs[j], self.ys[j])
            if curr_dist < min_distance:
                min_distance = curr_dist
                best = (self.xs[i], self.ys[i])
        return best

    # Average distance of points from the centre of the cluster
    def average_dist(self):
        if not self.xs:
            return 0
        dist_sum = 0
        center = self.calculate_centroid()
        amount = len(self.xs)
        for i in range(0, amount):
            dist_sum += math.sqrt(distance(self.xs[i], self.ys[i], center[0], center[1]))
        return dist_sum / amount

    def new_ref(self, type):
        if self.changed:
            if type == "centroid":
                return self.calculate_centroid()
            if type == "medoid":
                return self.calculate_medoid()
        else: return self.ref_point[0], self.ref_point[1]

    def merge(self, cluster):
        self.xs.extend(cluster.xs)
        self.ys.extend(cluster.ys)
