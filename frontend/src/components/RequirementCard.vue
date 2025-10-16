<template>
  <div class="requirement-card">
    <div class="card-header">
      <div class="ids-section">
        <div class="cfts-id">CFTS-ID: {{ requirement.cfts_id }}</div>
        <div class="req-id">Req.ID: {{ requirement.req_id }}</div>
        <div v-if="requirement.polarian_id" class="polarian-id">
          Polarian ID: {{ requirement.polarian_id }}
        </div>
      </div>
    </div>
    
    <div class="card-content">
      <div class="field-group">
        <div class="field-label">Scope 欄位:</div>
        <div class="field-value scope">{{ requirement.scope }}</div>
      </div>
      
      <div class="field-group">
        <div class="field-label">Test Case 欄位:</div>
        <div class="field-value test-case">{{ requirement.test_case }}</div>
      </div>
    </div>
    
    <div v-if="requirement.created_at || requirement.updated_at" class="card-footer">
      <div v-if="requirement.created_at" class="timestamp">
        建立時間: {{ formatDate(requirement.created_at) }}
      </div>
      <div v-if="requirement.updated_at" class="timestamp">
        更新時間: {{ formatDate(requirement.updated_at) }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RequirementCard',
  props: {
    requirement: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-TW')
    }
  }
}
</script>

<style scoped>
.requirement-card {
  border: 1px solid #e1e8ed;
  border-radius: 10px;
  overflow: hidden;
  background: white;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
}

.ids-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cfts-id {
  font-size: 1.3em;
  font-weight: bold;
}

.req-id {
  font-size: 1.1em;
  opacity: 0.9;
}

.polarian-id {
  font-size: 1em;
  opacity: 0.8;
}

.card-content {
  padding: 25px;
}

.field-group {
  margin-bottom: 20px;
}

.field-group:last-child {
  margin-bottom: 0;
}

.field-label {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.1em;
  border-bottom: 2px solid #3498db;
  padding-bottom: 5px;
  display: inline-block;
}

.field-value {
  padding: 15px;
  border-radius: 6px;
  line-height: 1.6;
  font-size: 1em;
}

.scope {
  background: #e8f5e8;
  border-left: 4px solid #27ae60;
  color: #2d5a2d;
}

.test-case {
  background: #fff3e0;
  border-left: 4px solid #f39c12;
  color: #8b4513;
}

.card-footer {
  background: #f8f9fa;
  padding: 15px 25px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.timestamp {
  color: #7f8c8d;
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .ids-section {
    align-items: flex-start;
  }
  
  .card-content {
    padding: 20px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 5px;
  }
}
</style>