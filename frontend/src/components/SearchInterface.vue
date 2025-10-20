<template>
  <div class="search-container">
    <h1>R1L Requirements and Test Case</h1>


    <div class="search-section">
      <div class="search-group">
        <label for="cfts-search">CFTS ID 搜尋:</label>
        <div class="input-group">
          <input
            id="cfts-search"
            v-model="cftsQuery"
            type="text"
            list="cfts-datalist"
            @keyup.enter="searchCFTS"
            @focus="loadCftsIds"
          />
          <datalist id="cfts-datalist">
            <option v-for="id in cftsIds" :key="id" :value="id"></option>
          </datalist>
          <button @click="searchCFTS" :disabled="!cftsQuery.trim()">搜尋</button>
        </div>
      </div>

      <div class="search-group">
        <label for="req-search">ReqID.ForeignID 搜尋:</label>
        <div class="input-group">
          <input
            id="req-search"
            v-model="reqQuery"
            type="text"
            @keyup.enter="searchReq"
          />
          <button @click="searchReq" :disabled="!reqQuery.trim()">搜尋</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SearchInterface',
  data() {
    return {
      cftsQuery: '',
      reqQuery: '',
      cftsIds: []
    }
  },
  methods: {
    async loadCftsIds() {
      if (this.cftsIds.length > 0) return // Already loaded

      try {
        const response = await axios.get('/api/cfts/autocomplete/cfts-ids')
        this.cftsIds = response.data
      } catch (error) {
        console.error('Failed to load CFTS IDs:', error)
      }
    },
    searchCFTS() {
      if (this.cftsQuery.trim()) {
        // Extract CFTS ID from the query (handles both "CFTS016" and "CFTS016 Anti-Theft" formats)
        const cftsIdMatch = this.cftsQuery.trim().match(/CFTS\d+/)
        const cftsId = cftsIdMatch ? cftsIdMatch[0] : this.cftsQuery.trim()
        this.$emit('search', { type: 'cfts', query: cftsId })
        // Clear the input field after search
        this.cftsQuery = ''
      }
    },
    searchReq() {
      if (this.reqQuery.trim()) {
        this.$emit('search', { type: 'req', query: this.reqQuery.trim() })
        // Clear the input field after search
        this.reqQuery = ''
      }
    }
  }
}
</script>

<style scoped>
.search-container {
  background: white;
  padding: 32px;
  margin-bottom: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e5e7eb;
}

h1 {
  text-align: center;
  color: #1f2937;
  margin-bottom: 32px;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.search-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  margin-bottom: 4px;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  background: white;
  color: #1f2937;
  transition: all 0.2s ease;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

input::placeholder {
  color: #9ca3af;
}

button {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  transition: all 0.2s ease;
  white-space: nowrap;
}

button:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
  }

  .search-container {
    padding: 24px 16px;
  }
}
</style>