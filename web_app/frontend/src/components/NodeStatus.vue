<template>
  {{ results }}
  <div id="node_status_view">
    <h2>Group1</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup1FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup1LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>
    </div>
    <h2>Group2</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup2FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup2LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>
    </div>
    <h2>Group3</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup3FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup3LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">{{n}}</div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'NodeStatus',
  data: function () {
    return {
      results: []
    }
  },
  computed:{
    filteredGroup1FirstHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 1 && value.ip.slice(-1) !== '0' && value.ip.slice(-1) <= 5
          }
      );
    },
    filteredGroup1LatterHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 1 && (value.ip.slice(-1) > 5 || value.ip.slice(-1) === '0')
          }
      );
    },
    filteredGroup2FirstHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 2 && value.ip.slice(-1) !== '0'&& value.ip.slice(-1) <= 5
          }
      );
    },
    filteredGroup2LatterHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 2 && (value.ip.slice(-1) > 5 || value.ip.slice(-1) === '0')
          }
      );
    },
    filteredGroup3FirstHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 3 && value.ip.slice(-1) !== '0' && value.ip.slice(-1) <= 5
          }
      );
    },
    filteredGroup3LatterHalf () {
      return this.results.filter(
          function (value) {
            return value.group_id === 3 && (value.ip.slice(-1) > 5 || value.ip.slice(-1) === '0')
          }
      );
    }
  },
  mounted() {
    let me = this
    axios.get('http://localhost:5500/nodes_status').then(function(response) {
      me.results = response.data;
      console.log(me.results);
    }).catch(function(error){ console.log(error); });
    setInterval(function() {
      axios.get('http://localhost:5500/nodes_status').then(function(response){
        me.results = response.data;

      console.log(me.results);
    }).catch(function(error){ console.log(error);});
  }, 1000);
  }
}

</script>

<style>
#node_status_view{
  width: 70%;
  margin: 0 auto;
}

.first_half{
  width: 50%;
}
.latter_half{
  width: 50%;
}

.group{
  border: #000 dashed .1rem;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  margin: 2rem 0;
}

.node{
  width: 85%;
  height: 5rem;
  margin: 1rem auto;
}

.group1_node{
  background-color: #F48FB1;
}

.group2_node{
  background-color: #C5E1A5;
}

.group3_node{
  background-color: #90CAF9;
}

.is_leader{
  border: #F44336 solid 3px;
}

</style>