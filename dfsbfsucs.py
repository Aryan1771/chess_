from collections import deque
import heapq
class Graph:
    def __init__(self, graph):
        self.graph = graph
    def bfs(self, start, goal):
        queue = deque([[start]])
        visited = set()
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == goal:
                return path
            if node not in visited:
                visited.add(node)
                for neighbour in self.graph[node]:
                    queue.append(path + [neighbour])
        return None
    def dfs(self, start, goal):
        stack = [[start]]
        visited = set()
        while stack:
            path = stack.pop()
            node = path[-1]
            if node == goal:
                return path
            if node not in visited:
                visited.add(node)
                for neighbour in self.graph[node]:
                    stack.append(path + [neighbour])
        return None
    def ucs(self, start, goal):
        pq = [(0, start, [start])]
        cost_so_far = {start: 0}
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node == goal:
                return path, cost
            for neighbour, weight in self.graph[node].items():
                new_cost = cost + weight
                if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                    cost_so_far[neighbour] = new_cost
                    heapq.heappush(pq, (new_cost, neighbour, path + [neighbour]))
        return None
    def greedy_best_first(self, start, goal, heuristic):
        pq = [(heuristic[start], start, [start])]
        visited = set()
        while pq:
            h, node, path = heapq.heappop(pq)
            if node == goal:
                return path
            if node not in visited:
                visited.add(node)
                for neighbour in self.graph[node]:
                    heapq.heappush(pq, (heuristic[neighbour], neighbour, path + [neighbour]))
        return None
    def a_star(self, start, goal, heuristic):
        pq = [(heuristic[start], start, [start], 0)]
        cost_so_far = {start: 0}
        while pq:
            f, node, path, g = heapq.heappop(pq)
            if node == goal:
                return path, g
            for neighbour, weight in self.graph[node].items():
                new_g = g + weight
                if neighbour not in cost_so_far or new_g < cost_so_far[neighbour]:
                    cost_so_far[neighbour] = new_g
                    new_f = new_g + heuristic[neighbour]
                    heapq.heappush(pq, (new_f, neighbour, path + [neighbour], new_g))
        return None
class AOStar:
    def __init__(self, graph, heuristic):
        self.graph = graph
        self.heuristic = heuristic
        self.solution = {}
    def ao_star(self, node):
        if node not in self.graph:
            return self.heuristic[node]
        min_cost = float('inf')
        best_children = None
        for children in self.graph[node]:
            cost = 0
            for child, weight in children:
                cost += weight + self.ao_star(child)
            if cost < min_cost:
                min_cost = cost
                best_children = children
        self.solution[node] = best_children
        return min_cost
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'D': 2, 'E': 5},
    'C': {'F': 3},
    'D': {'G': 1},
    'E': {'G': 2},
    'F': {'G': 1},
    'G': {}
}
heuristic = {
    'A': 7,
    'B': 6,
    'C': 4,
    'D': 3,
    'E': 2,
    'F': 1,
    'G': 0
}
ao_graph = {
    'A': [[('B', 1), ('C', 1)]],
    'B': [[('D', 1)], [('E', 1)]],
    'C': [[('F', 1)]],
    'D': [[('G', 1)]],
    'E': [[('G', 1)]],
    'F': [[('G', 1)]],
    'G': []
}
ao_heuristic = {
    'D': 0,
    'E': 0,
    'C': 2,
    'B': 2,
    'A': 4,
    'F': 1,
    'G': 0
}
g = Graph(graph)
print("BFS:", g.bfs('A', 'G'))
print("DFS:", g.dfs('A', 'G'))
print("UCS:", g.ucs('A', 'G'))
print("Greedy:", g.greedy_best_first('A', 'G', heuristic))
print("A*:", g.a_star('A', 'G', heuristic))
ao_solver = AOStar(ao_graph, ao_heuristic)
ao_solver.ao_star('A')
print("AO* Solution:", ao_solver.solution)