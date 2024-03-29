from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from constraint import *
import networkx as nx
from datetime import datetime

app = FastAPI(docs_url="/api/docs", openapi_url="/api/v1/openapi.json")


def parse_cell_value(cell_value):
    if cell_value is None:
        return 0
    if isinstance(cell_value, str):
        cell_value = cell_value.strip()
        if cell_value == "":
            return 0
        else:
            return int(cell_value)
    else:
        return int(cell_value)


def validate_grid(puzzle_grid):
    for row in puzzle_grid:
        for cell in row:
            if cell["cage_num"] == -1:
                return False
            if parse_cell_value(cell["value"]) < 0:
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


def print_solution(solution):
    cell_ids = solution.keys()
    for i in sorted(set(i for i, _ in cell_ids)):
        for j in sorted(set(j for _, j in cell_ids)):
            print(f"{solution[(i, j)]} ", end="")
        print()


def count_additional_solutions(solutions_iter, max_iter=10):
    counter = 0
    try:
        while counter < max_iter:
            solution = next(solutions_iter)
            counter += 1
    except StopIteration:
        pass
    return counter


@app.get("/api/healthcheck")
async def healthcheck():
    return {"status": "success", "message": "API is running."}


@app.post("/api/solve")
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
            cell_value = parse_cell_value(grid[i][j].get("value"))
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
        print_solution(solution)
    except StopIteration:
        return {"status": "fail", "message": "No solution found."}

    num_solutions = 1 + count_additional_solutions(solutions_iter, 9)
    if num_solutions >= 10:
        message = (
            f"Solution found! At least {num_solutions} unique solutions were found."
        )
    else:
        message = f"Solution found! Found {num_solutions} unique solutions."

    result = []
    for i in range(grid_height):
        result.append([])
        for j in range(grid_width):
            result[i].append(solution[(i, j)])
    return {"solution": result, "status": "success", "message": message}


# This goes at the bottom so that the API routes are registered first
app.mount("/", StaticFiles(directory="dist", html=True), name="dist")
