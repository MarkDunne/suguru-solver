<script setup>
defineProps({});
</script>

<template>
  <div id="suguru_solver">
    <div>
      <h3>Step 1: Create a Grid</h3>
      <div id="create_grid_form">
        <div class="grid">
          <label for="grid_width"
            >Grid Width
            <input
              inputmode="numeric"
              id="grid_width"
              v-model.number="grid_width"
            />
          </label>

          <label for="grid_height">
            Grid Height
            <input
              inputmode="numeric"
              id="grid_height"
              v-model.number="grid_height"
            />
          </label>
        </div>
        <button @click="update_grid" type="submit">Create</button>
      </div>
    </div>

    <div id="grid_section">
      <h3>Step 2: Add cages and numbers</h3>
      <p>
        Click and drag the cells to create suguru cages. Every cell must be in a
        cage. Enter numbers when you're done!
      </p>
      <div id="change_mode" class="grid">
        <button
          :class="{ outline: mode != 'draw_cages' }"
          @click="mode = 'draw_cages'"
        >
          Draw Cages
        </button>
        <button
          :class="{ outline: mode != 'enter_numbers' }"
          @click="mode = 'enter_numbers'"
        >
          Enter Numbers
        </button>
      </div>
      <table @touchmove="touchmove">
        <tr v-for="(row, rowIndex) in grid" :key="rowIndex">
          <td
            v-for="(cell, cellIndex) in row"
            :key="cellIndex"
            :class="{
              top_border: cell.top_border,
              bot_border: cell.bot_border,
              left_border: cell.left_border,
              right_border: cell.right_border,
              not_in_cage: cell.cage_num == -1,
            }"
            @mousedown="mouseDown(rowIndex, cellIndex)"
            @touchstart.prevent="mouseDown(rowIndex, cellIndex)"
            @mouseup="mouseUp"
            @touchend="mouseUp"
            @mouseenter="mouseEnter(rowIndex, cellIndex)"
          >
            <div
              class="table-cell"
              :cellRowIndex="rowIndex"
              :cellColIndex="cellIndex"
            >
              <input
                type="text"
                autocomplete="off"
                inputmode="numeric"
                min="0"
                v-model="cell.value"
                :disabled="mode == 'draw_cages'"
              />
            </div>
          </td>
        </tr>
      </table>
    </div>

    <div>
      <h3>Step 3: Solve!</h3>
      <button :disabled="solving" @click="submit_puzzle">Solve Puzzle</button>
      <p
        id="statusMessage"
        v-if="statusMessage"
        :class="[statusSuccess ? 'success' : 'fail']"
      >
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    const grid_width = 9;
    const grid_height = 9;

    return {
      grid_width: grid_width,
      grid_height: grid_height,
      grid: this.create_grid(grid_width, grid_height),
      cage_counter: 0,
      statusMessage: "",
      statusSuccess: false,
      isDrawing: false,
      currentRow: -1,
      currentCol: -1,
      mode: "draw_cages",
      last_touch_cell_row: null,
      last_touch_cell_col: null,
      solving: false,
    };
  },
  methods: {
    create_grid(grid_width, grid_height) {
      let grid = [];
      for (let i = 0; i < grid_height; i++) {
        grid[i] = [];
        for (let j = 0; j < grid_width; j++) {
          grid[i][j] = { value: "", cage_num: -1 };
        }
      }
      return grid;
    },
    update_grid() {
      this.grid = this.create_grid(this.grid_width, this.grid_height);
    },
    mouseDown(row, col) {
      this.last_touch_cell_row = null;
      this.last_touch_cell_col = null;

      if (this.mode == "draw_cages") {
        this.currentRow = row;
        this.currentCol = col;
        this.cage_counter += 1;
        this.isDrawing = true;
        this.mouseEnter(row, col);
      }
    },
    touchmove(event) {
      if (this.mode == "draw_cages" && this.isDrawing) {
        const elem = document.elementFromPoint(
          event.touches[0].clientX,
          event.touches[0].clientY
        );
        if (
          elem.hasAttribute("cellrowindex") &&
          elem.hasAttribute("cellcolindex")
        ) {
          let cell_row = elem.getAttribute("cellrowindex");
          let cell_col = elem.getAttribute("cellcolindex");

          if (
            this.last_touch_cell_row != cell_row ||
            this.last_touch_cell_col != cell_col
          ) {
            this.mouseEnter(cell_row, cell_col);
          }

          this.last_touch_cell_row = cell_row;
          this.last_touch_cell_col = cell_col;
        }
      }
    },
    mouseUp() {
      if (this.mode == "draw_cages") {
        this.isDrawing = false;
      }
    },
    mouseEnter(row, col) {
      if (this.mode == "draw_cages" && this.isDrawing) {
        this.grid[row][col].cage_num = this.cage_counter;

        for (let i = 0; i < this.grid_height; i++) {
          for (let j = 0; j < this.grid_width; j++) {
            this.grid[i][j].top_border =
              i > 0 && this.grid[i][j].cage_num != this.grid[i - 1][j].cage_num;
            this.grid[i][j].bot_border =
              i < this.grid_height - 1 &&
              this.grid[i][j].cage_num != this.grid[i + 1][j].cage_num;

            this.grid[i][j].left_border =
              j > 0 && this.grid[i][j].cage_num != this.grid[i][j - 1].cage_num;
            this.grid[i][j].right_border =
              j < this.grid_width - 1 &&
              this.grid[i][j].cage_num != this.grid[i][j + 1].cage_num;
          }
        }
      }
    },
    submit_puzzle() {
      this.solving = true;
      this.statusMessage = "Solving...";
      fetch("/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          grid_width: this.grid_width,
          grid_height: this.grid_height,
          grid: this.grid,
        }),
      })
        .then((response) => {
          console.log(response);
          if (response.ok) {
            return response.json();
          } else {
            return {
              status: "fail",
              message: "Failed with status: " + response.status,
            };
          }
        })
        .then((data) => {
          this.solving = false;
          this.statusSuccess = data.status == "success";
          this.statusMessage = data.message;
          if ("solution" in data) {
            for (let i = 0; i < this.grid_height; i++) {
              for (let j = 0; j < this.grid_width; j++) {
                this.grid[i][j].value = data.solution[i][j];
              }
            }
          }
        });
    },
  },
};
</script>

<style scoped></style>
