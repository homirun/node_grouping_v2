<template>
  <div id="node_status_view">
    {{ results }}
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'NodeStatus',
  data: function () {
    return {
      results: null
    }
  },
  mounted() {
      axios.get('http://localhost:5500/nodes_status').then(response => {
        this.results = response;
        console.log(this.results)
      }).catch( error => { console.log(error); });
  }
}
</script>