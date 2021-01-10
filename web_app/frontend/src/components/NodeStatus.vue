<template>
  <button v-on:click="startNetworkPartition">ネットワーク分断開始</button>
  <button v-on:click="stopNetworkPartition">ネットワーク分断終了</button>
  <div id="node_status_view">
    <h2 v-if="!is_partition">Group1</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup1FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
      </div>
      <div class="v_line" v-if="is_partition"></div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup1LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
      </div>
    </div>
    <div class="v_line" v-if="is_partition"></div>
    <h2 v-if="!is_partition">Group2</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup2FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
      </div>
      <div class="v_line" v-if="is_partition"></div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup2LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
      </div>
    </div>
    <div class="v_line" v-if="is_partition"></div>
    <h2 v-if="!is_partition">Group3</h2>
    <div class="group">
      <div class="first_half">
        <div class="node" v-for="n in filteredGroup3FirstHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
      </div>
      <div class="v_line" v-if="is_partition"></div>
      <div class="latter_half">
        <div class="node" v-for="n in filteredGroup3LatterHalf" :class="['group'+n.group_id+'_node', n.is_leader ? 'is_leader' : '']"  :key="n">
          {{'Node' + [n.ip.slice((-1))==='0' ? '10' :n.ip.slice((-1))]}}
        </div>
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
      results: [],
      is_partition: false
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
    let me = this;
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
  },
  methods:{
    startNetworkPartition() {
      let me = this;
      axios.get('http://localhost:5500/network_partition/start').then(function() {
        me.is_partition = true;
      }).catch(function(error){ console.log(error); });
    },
    stopNetworkPartition() {
      let me = this;
      axios.get('http://localhost:5500/network_partition/stop').then(function() {
        me.is_partition = false;
    }).catch(function(error){ console.log(error); });
    }

  }

}

</script>

<style>
#node_status_view{
  width: 70%;
  margin: 0 auto;
}

.first_half{
  width: 49%;
}
.latter_half{
  width: 49%;
}

.group{
  border: #000 dashed .1rem;
  width: calc(100% - 0.2rem);
  display: flex;
  flex-wrap: wrap;
  margin: 0;
}

.node{
  width: 85%;
  height: 5rem;
  margin: 1rem auto;
  font-size: 3rem;
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
  font-weight: bold;
}

.group > .v_line {
  width: 5px;
  background-color: brown;
  margin: 0 auto;
}

#node_status_view > .v_line {
  width: 5px;
  background-color: brown;
  height: 50px;
  margin: 0 auto;
}
button {
  font-size: 3rem;
  margin: 1rem;
}

</style>