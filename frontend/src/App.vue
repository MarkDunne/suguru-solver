<template>
  <header>
    <h1>Suguru Solver</h1>
  </header>

  <main class="wrapper container grid">
    <div id="blurb">
      <p>
        <a href="https://dkmgames.com/Suguru/SuguruTutBasic.htm">Suguru</a> is a
        very simple but enjoyable puzzle game, a little like Sodoku. There are
        only two rules. The first is that each cage of size <i>N</i> must
        contain all of the numbers from 1 to <i>N</i>. The second rule is that
        no two adjacent cells (including diagonally) can contain the same
        number.
      </p>

      <p>Sometimes puzzles can have multiple solutions!</p>

      <p>This page can help you solve suguru puzzles.</p>

      <p>
        Click and drag over the boxes to create the cages, and enter the number
        to specify the puzzle. All boxes must be part of a cage for the puzzle
        to valid.
      </p>
      <div>
        <button @click="load_example" type="submit" class="secondary">
          Load example
        </button>
      </div>
    </div>

    <SuguruSolver ref="solver" />
  </main>

  <footer>
    <p>Updated 2022-12-30</p>
  </footer>
</template>

<style scoped></style>

<script setup>
import { ref } from "vue";
import SuguruSolver from "./components/SuguruSolver.vue";

const solver = ref(null);

function load_example() {
  solver.value.load_example();
}
</script>
