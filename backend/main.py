from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from constraint import *
import networkx as nx
from datetime import datetime

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_grid(puzzle_grid):
    for row in puzzle_grid:
        for cell in row:
            if cell["cage_num"] == -1:
                return False
            if cell["value"] < 0:
                return False
    return True


def get_cage_cells(puzzle_grid, grid_width, grid_height):
    graph = nx.Graph()
    for i in range(grid_height):
        for j in range(grid_width):
            if puzzle_grid[i][j]["cage_num"] == -1:
                continue
            graph.add_node((i, j))
            if (
                i < grid_height - 1
                and puzzle_grid[i][j]["cage_num"] == puzzle_grid[i + 1][j]["cage_num"]
            ):
                graph.add_edge((i, j), (i + 1, j))
            if (
                j < grid_width - 1
                and puzzle_grid[i][j]["cage_num"] == puzzle_grid[i][j + 1]["cage_num"]
            ):
                graph.add_edge((i, j), (i, j + 1))

    return list(nx.connected_components(graph))


def cell_ranges(cages):
    result = {}
    for cage in cages:
        for cell in cage:
            result[cell] = list(range(1, len(cage) + 1))
    return result


@FunctionConstraint
def NotEqualConstraint(a, b):
    return a != b


@app.post("/solve")
async def solve_suguru(request: Request):
    request = await request.json()

    # Extract the grid and its size from the request data
    grid = request["grid"]
    grid_width = request["grid_width"]
    grid_height = request["grid_height"]

    if not validate_grid(grid):
        return {"status": "fail", "message": "Invalid grid."}

    # Create a problem
    problem = Problem()

    cages = get_cage_cells(grid, grid_width, grid_height)
    cell_range_map = cell_ranges(cages)

    # Add variables for each cell in the grid
    for i in range(grid_height):
        for j in range(grid_width):
            cell_value = int(grid[i][j].get("value", 0))
            if cell_value > 0:
                problem.addVariable((i, j), [cell_value])
            else:
                problem.addVariable((i, j), cell_range_map[(i, j)])

    # Add constraints for each cell in the grid
    for cage in cages:
        problem.addConstraint(AllDifferentConstraint(), [(i, j) for i, j in cage])

    for i in range(grid_height):
        for j in range(grid_width):
            if i > 0:
                problem.addConstraint(NotEqualConstraint, [(i, j), (i - 1, j)])
            if j > 0:
                problem.addConstraint(NotEqualConstraint, [(i, j), (i, j - 1)])
            if i > 0 and j > 0:
                problem.addConstraint(NotEqualConstraint, [(i, j), (i - 1, j - 1)])

    # Solve the problem
    print("solving", datetime.utcnow().isoformat())
    solutions_iter = problem.getSolutionIter()

    try:
        solution = next(solutions_iter)
    except StopIteration:
        return {"status": "fail", "message": "No solution found."}

    result = []
    for i in range(grid_height):
        result.append([])
        for j in range(grid_width):
            result[i].append(solution[(i, j)])
    return {"solution": result, "status": "success", "message": "Solution found!"}
