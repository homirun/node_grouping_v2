<template>
  <h1>NodeStatusViewer</h1>
  <NodeStatus />
</template>

<script>
import NodeStatus from './components/NodeStatus'

export default {
  name: 'App',
  components: {
    NodeStatus
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
