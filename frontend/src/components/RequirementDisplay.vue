<template>
  <div class="requirement-display">
    <div v-if="searchType === 'cfts' && searchResults" class="cfts-results">
      <h2>CFTS 搜尋結果</h2>
      <div class="cfts-header">
        <div class="cfts-id">CFTS-ID: {{ searchResults.cfts_id }}</div>
        <div class="total-count">共 {{ searchResults.total_count }} 筆需求</div>
      </div>
      
      <div class="requirements-list">
        <div 
          v-for="requirement in searchResults.requirements" 
          :key="requirement.req_id"
          class="requirement-card"
        >
          <RequirementCard :requirement="requirement" />
        </div>
      </div>
    </div>

    <div v-else-if="searchType === 'req' && searchResults" class="req-results">
      <h2>Req.ID 搜尋結果</h2>
      <RequirementCard :requirement="searchResults" />
    </div>

    <div v-else-if="searchResults === null" class="no-results">
      <p>請使用上方搜尋欄進行搜尋</p>
    </div>
  </div>
</template>

<script>
import RequirementCard from './RequirementCard.vue'

export default {
  name: 'RequirementDisplay',
  components: {
    RequirementCard
  },
  props: {
    searchResults: {
      type: [Object, null],
      default: null
    },
    searchType: {
      type: String,
      default: null
    }
  }
}
</script>

<style scoped>
.requirement-display {
  margin-top: 20px;
}

.cfts-results, .req-results {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.8em;
  border-bottom: 3px solid #3498db;
  padding-bottom: 10px;
}

.cfts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ecf0f1;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.cfts-id {
  font-size: 1.3em;
  font-weight: bold;
  color: #2c3e50;
}

.total-count {
  color: #7f8c8d;
  font-size: 1.1em;
}

.requirements-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.requirement-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: box-shadow 0.3s;
}

.requirement-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.no-results {
  text-align: center;
  color: #7f8c8d;
  font-size: 1.2em;
  margin-top: 50px;
}
</style>