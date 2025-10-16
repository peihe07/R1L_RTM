<template>
  <div id="app">
    <SearchInterface @search="handleSearch" />
    <RequirementTable 
      :search-results="searchResults" 
      :search-type="searchType"
    />
  </div>
</template>

<script>
import SearchInterface from './components/SearchInterface.vue'
import RequirementTable from './components/RequirementTable.vue'

export default {
  name: 'App',
  components: {
    SearchInterface,
    RequirementTable
  },
  data() {
    return {
      searchResults: null,
      searchType: null
    }
  },
  methods: {
    async handleSearch({ type, query }) {
      this.searchType = type
      try {
        if (type === 'cfts') {
          const response = await fetch(`http://localhost:8000/cfts/search?cfts_id=${query}`)
          this.searchResults = await response.json()
        } else if (type === 'req') {
          const response = await fetch(`http://localhost:8000/req/search?req_id=${query}`)
          this.searchResults = await response.json()
        }
      } catch (error) {
        console.error('Search error:', error)
        this.searchResults = null
      }
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap');

body {
  margin: 0;
  padding: 0;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  background: 
    linear-gradient(90deg, rgba(0,255,255,0.1) 0%, rgba(0,255,255,0) 50%, rgba(0,255,255,0.1) 100%),
    linear-gradient(45deg, #c0c0c0 25%, transparent 25%), 
    linear-gradient(-45deg, #c0c0c0 25%, transparent 25%), 
    linear-gradient(45deg, transparent 75%, #c0c0c0 75%), 
    linear-gradient(-45deg, transparent 75%, #c0c0c0 75%);
  background-size: 100% 2px, 4px 4px, 4px 4px, 4px 4px, 4px 4px;
  background-position: 0 0, 0 0, 0 2px, 2px -2px, -2px 0px;
  background-color: #003333;
  color: #000;
  animation: scanlines 3s linear infinite;
}

@keyframes scanlines {
  0% { background-position: 0 0, 0 0, 0 2px, 2px -2px, -2px 0px; }
  100% { background-position: 100% 0, 0 0, 0 2px, 2px -2px, -2px 0px; }
}

#app {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  color: #000000;
  margin: 16px;
  max-width: 1000px;
  margin: 16px auto;
  padding: 16px;
  background: linear-gradient(145deg, #d0d0d0 0%, #c0c0c0 50%, #b0b0b0 100%);
  border: 3px outset #c0c0c0;
  box-shadow: 
    2px 2px 0px #000,
    0 0 20px rgba(0,255,255,0.3),
    inset 0 0 0 1px rgba(255,255,255,0.5);
  position: relative;
  overflow: hidden;
}

#app::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, transparent 30%, rgba(0,255,255,0.1) 50%, transparent 70%);
  animation: glow-border 2s ease-in-out infinite alternate;
  z-index: -1;
}

@keyframes glow-border {
  0% { opacity: 0.5; }
  100% { opacity: 1; }
}

* {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}
</style>