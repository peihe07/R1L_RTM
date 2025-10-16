<template>
  <div class="search-container">
    <h1>Requirements and Test Case Management</h1>


    <div class="search-section">
      <div class="search-group">
        <label for="cfts-search">搜尋 CFTS 搜尋欄:</label>
        <div class="input-group">
          <input
            id="cfts-search"
            v-model="cftsQuery"
            type="text"
            list="cfts-datalist"
            placeholder="輸入 CFTS ID (例: CFTS016)"
            @keyup.enter="searchCFTS"
            @focus="loadCftsIds"
          />
          <datalist id="cfts-datalist">
            <option v-for="id in cftsIds" :key="id" :value="id">{{ id }}</option>
          </datalist>
          <button @click="searchCFTS" :disabled="!cftsQuery.trim()">搜尋</button>
        </div>
      </div>

      <div class="search-group">
        <label for="req-search">搜尋 Req.ID 搜尋欄:</label>
        <div class="input-group">
          <input
            id="req-search"
            v-model="reqQuery"
            type="text"
            placeholder="輸入 Req.ID (例: 4942459)"
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
        const response = await axios.get('http://localhost:8000/cfts/autocomplete/cfts-ids')
        this.cftsIds = response.data
      } catch (error) {
        console.error('Failed to load CFTS IDs:', error)
      }
    },
    searchCFTS() {
      if (this.cftsQuery.trim()) {
        this.$emit('search', { type: 'cfts', query: this.cftsQuery.trim() })
      }
    },
    searchReq() {
      if (this.reqQuery.trim()) {
        this.$emit('search', { type: 'req', query: this.reqQuery.trim() })
      }
    }
  }
}
</script>

<style scoped>
.search-container {
  background: linear-gradient(145deg, #d0d0d0 0%, #c0c0c0 50%, #b0b0b0 100%);
  padding: 24px;
  border: 3px outset #c0c0c0;
  margin-bottom: 24px;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: 
    2px 2px 0px #000,
    0 0 15px rgba(0,255,255,0.3),
    inset 0 0 0 1px rgba(255,255,255,0.3);
  position: relative;
  overflow: hidden;
}

.search-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0,255,255,0.8), transparent);
  animation: scan 3s linear infinite;
}

@keyframes scan {
  0% { left: -100%; }
  100% { left: 100%; }
}

h1 {
  text-align: center;
  color: #000000;
  margin-bottom: 20px;
  font-size: 24px;
  font-family: 'Press Start 2P', monospace;
  text-shadow: 
    2px 2px 0px #fff, 
    4px 4px 0px #808080,
    0 0 10px rgba(0,255,255,0.8),
    0 0 20px rgba(0,255,255,0.4);
  line-height: 1.3;
  letter-spacing: 1px;
  animation: title-glow 2s ease-in-out infinite alternate;
  position: relative;
}

@keyframes title-glow {
  0% { 
    text-shadow: 
      2px 2px 0px #fff, 
      4px 4px 0px #808080,
      0 0 10px rgba(0,255,255,0.8),
      0 0 20px rgba(0,255,255,0.4);
  }
  100% { 
    text-shadow: 
      2px 2px 0px #fff, 
      4px 4px 0px #808080,
      0 0 15px rgba(0,255,255,1),
      0 0 30px rgba(0,255,255,0.6),
      0 0 40px rgba(0,255,255,0.3);
  }
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 700px;
  margin: 0 auto;
}

.search-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: bold;
  color: #000000;
  font-size: 16px;
  font-family: 'JetBrains Mono', monospace;
  display: block;
  margin-bottom: 8px;
  text-shadow: 1px 1px 0px #fff;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

input {
  flex: 1;
  padding: 12px;
  border: 2px inset #c0c0c0;
  font-size: 16px;
  font-family: 'JetBrains Mono', monospace;
  background: linear-gradient(145deg, #ffffff 0%, #f8f8f8 100%);
  color: #000;
  box-sizing: border-box;
  font-weight: 500;
  box-shadow: 
    inset 1px 1px 2px #000,
    0 0 5px rgba(0,255,255,0.1);
  transition: all 0.3s ease;
}

input:focus {
  background: linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%);
  outline: none;
  border: 2px inset #808080;
  box-shadow: 
    inset 1px 1px 2px #000,
    0 0 10px rgba(0,255,255,0.3),
    0 0 20px rgba(0,255,255,0.1);
  text-shadow: 0 0 3px rgba(0,255,255,0.3);
}

button {
  padding: 12px 20px;
  background: linear-gradient(145deg, #d0d0d0 0%, #c0c0c0 50%, #b0b0b0 100%);
  color: #000000;
  border: 2px outset #c0c0c0;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: 
    1px 1px 0px #000,
    0 0 10px rgba(0,255,255,0.2);
  text-shadow: 
    1px 1px 0px #fff,
    0 0 5px rgba(0,255,255,0.5);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

button::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, transparent, rgba(0,255,255,0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

button:hover:not(:disabled) {
  background: linear-gradient(145deg, #e0e0e0 0%, #d0d0d0 50%, #c0c0c0 100%);
  box-shadow: 
    1px 1px 0px #000,
    0 0 15px rgba(0,255,255,0.4),
    0 0 25px rgba(0,255,255,0.2);
  text-shadow: 
    1px 1px 0px #fff,
    0 0 8px rgba(0,255,255,0.8);
  transform: translateY(-1px);
}

button:hover:not(:disabled)::before {
  opacity: 1;
}

button:disabled {
  background: #808080;
  color: #c0c0c0;
  cursor: not-allowed;
  border: 2px inset #c0c0c0;
}

</style>