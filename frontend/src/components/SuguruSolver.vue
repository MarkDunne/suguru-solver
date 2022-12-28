<script setup>
defineProps({});
</script>

<template>
  <div id="suguru_solver">
    <div>
      <div id="create_grid_form">
        <h2>Create a Grid</h2>
        <div>
          <label for="grid_width">Grid Width</label>
          <input
            inputmode="numeric"
            id="grid_width"
            v-model.number="grid_width"
          />
        </div>
        <div>
          <label for="grid_height">Grid Height</label>
          <input
            inputmode="numeric"
            id="grid_height"
            v-model.number="grid_height"
          />
        </div>
        <button
          @click="this.grid = create_grid(this.grid_width, this.grid_height)"
        >
          Create
        </button>
      </div>
    </div>
    <div id="grid_section">
      <table>
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
            @mouseup="mouseUp"
            @mouseenter="mouseEnter(rowIndex, cellIndex)"
          >
            <div class="table-cell">
              <input
                @mousedown.stop
                type="text"
                autocomplete="off"
                inputmode="numeric"
                min="0"
                v-model="cell.value"
              />
            </div>
          </td>
        </tr>
      </table>
      <button @click="submit_puzzle">Solve Puzzle</button>
    </div>
    <h3
      id="statusMessage"
      v-if="statusMessage"
      :class="[statusSuccess ? 'success' : 'fail']"
    >
      {{ statusMessage }}
    </h3>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    const grid_width = 3;
    const grid_height = 5;

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
    };
  },
  methods: {
    create_grid(grid_width, grid_height) {
      let grid = [];
      for (let i = 0; i < grid_height; i++) {
        grid[i] = [];
        for (let j = 0; j < grid_width; j++) {
          grid[i][j] = { value: 0, cage_num: -1 };
        }
      }
      return grid;
    },
    mouseDown(row, col) {
      this.currentRow = row;
      this.currentCol = col;
      this.cage_counter += 1;
      this.isDrawing = true;
      this.mouseEnter(row, col);
    },
    mouseUp() {
      this.isDrawing = false;
    },
    mouseEnter(row, col) {
      if (this.isDrawing) {
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
        .then((response) => response.json())
        .then((data) => {
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

<style scoped>
table {
  /* border-collapse: collapse; */
  user-select: none;
  table-layout: fixed;
}

td {
  border: 2px solid #e6e6e6;
  border-radius: 5px;
}

td.top_border {
  border-top: 2px solid red;
}

td.bot_border {
  border-bottom: 2px solid red;
}

td.left_border {
  border-left: 2px solid red;
}

td.right_border {
  border-right: 2px solid red;
}

div.table-cell {
  min-width: 60px;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

td.not_in_cage {
  background-color: rgba(252, 246, 67, 0.539);
}

.table-cell input {
  width: 50%;
  text-align: center;
  user-select: none;
  /* pointer-events: none; */
}

#create_grid_form,
#grid_section {
  margin-bottom: 2rem;
}

label {
  margin-right: 1rem;
}

#statusMessage.success {
  color: green;
}
#statusMessage.fail {
  color: red;
}
</style>
