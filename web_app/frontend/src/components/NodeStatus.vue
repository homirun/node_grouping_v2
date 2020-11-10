<template>
  {{ results }}
  <div id="node_status_view">

    <div class="group" v-for="n in results" :class="['group'+n.group_id, n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
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
    let me = this
    axios.get('http://localhost:5500/nodes_status').then(function(response) {
      me.results = response.data;
      console.log(me.results)
    }).catch(function(error){ console.log(error); });
    setInterval(function() {
      axios.get('http://localhost:5500/nodes_status').then(function(response){
        me.results = response.data;
      console.log(me.results)
    }).catch(function(error){ console.log(error);});
  }, 1000);
  }
}

</script>

<style>
#node_status_view{
  width: 70%;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

.group{
  background-color: #42b983;
  margin: 2rem;
  width: 30rem;
}

.group1{
  background-color: lightpink;
}

.group2{
  background-color: lightgreen;
}

.group3{

}

.is_leader{
  border: #F44336 solid 3px;
}

</style>