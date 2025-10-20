<template>
  <div id="app">
    <!-- Search Page -->
    <div v-if="currentPage === 'search'">
      <SearchInterface @search="handleSearch" />
      <RequirementTable
        :search-results="searchResults"
        :search-type="searchType"
        @view-melco-detail="handleViewMelcoDetail"
      />
    </div>

    <!-- Melco Detail Page -->
    <div v-else-if="currentPage === 'melco-detail'">
      <MelcoDetailPage
        :melco-id="selectedMelcoId"
        @back="handleBackToSearch"
      />
    </div>
  </div>
</template>

<script>
import SearchInterface from './components/SearchInterface.vue'
import RequirementTable from './components/RequirementTable.vue'
import MelcoDetailPage from './components/MelcoDetailPage.vue'

export default {
  name: 'App',
  components: {
    SearchInterface,
    RequirementTable,
    MelcoDetailPage
  },
  data() {
    return {
      currentPage: 'search',
      searchResults: null,
      searchType: null,
      selectedMelcoId: null
    }
  },
  methods: {
    async handleSearch({ type, query }) {
      this.searchType = type
      try {
        if (type === 'cfts') {
          const response = await fetch(`/api/cfts/search?cfts_id=${query}`)
          this.searchResults = await response.json()
        } else if (type === 'req') {
          const response = await fetch(`/api/req/search?req_id=${query}`)
          this.searchResults = await response.json()
        }
      } catch (error) {
        console.error('Search error:', error)
        this.searchResults = null
      }
    },
    handleViewMelcoDetail(melcoId) {
      this.selectedMelcoId = melcoId
      this.currentPage = 'melco-detail'
    },
    handleBackToSearch() {
      this.currentPage = 'search'
      this.selectedMelcoId = null
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f7fa;
  color: #2c3e50;
}

#app {
  font-family: 'Inter', sans-serif;
  color: #2c3e50;
  min-height: 100vh;
  padding: 0;
  margin: 0;
  background: #f5f7fa;
}
</style>