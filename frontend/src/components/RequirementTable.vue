<template>
  <div class="requirement-table">
    <div v-if="searchResults" class="cfts-results">
      <h2>{{ searchType === 'req' ? 'Req.ID 搜尋結果' : 'CFTS 搜尋結果' }}</h2>
      <div class="result-summary">
        <div class="summary-item">
          <strong>CFTS ID:</strong> {{ searchResults.cfts_id }}
        </div>
        <div class="summary-item">
          <strong>總筆數:</strong> {{ searchResults.total_count }} 筆
        </div>
        <div v-if="searchResults.target_req_id" class="summary-item">
          <strong>目標 Req.ID:</strong> {{ searchResults.target_req_id }}
        </div>
      </div>

      <div class="filter-controls">
        <div class="filter-checkboxes">
          <label class="filter-checkbox">
            <input type="checkbox" v-model="showOnlySW" />
            <span>只顯示 SW</span>
          </label>
          <label class="filter-checkbox">
            <input type="checkbox" v-model="showOnlySystem" />
            <span>只顯示 System</span>
          </label>
          <label class="filter-checkbox">
            <input type="checkbox" v-model="showSWAndSystem" />
            <span>只顯示 SW 和 System</span>
          </label>
        </div>
        <div v-if="showOnlySW || showOnlySystem || showSWAndSystem" class="filter-info">
          顯示 {{ filteredRequirements.length }} / {{ searchResults.requirements.length }} 筆
        </div>
      </div>

      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th>序號</th>
              <th>CFTS-ID</th>
              <th>Req.ID</th>
              <th>Polarian ID</th>
              <th>Scope</th>
              <th>Test Case</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(requirement, index) in filteredRequirements"
              :key="requirement.req_id"
              :class="{
                'even-row': index % 2 === 1,
                'target-row': requirement.req_id === searchResults.target_req_id
              }"
              :ref="requirement.req_id === searchResults.target_req_id ? 'targetRow' : null"
            >
              <td class="row-number">
                <span v-if="requirement.req_id === searchResults.target_req_id" class="target-indicator">▶</span>
                {{ index + 1 }}
              </td>
              <td class="cfts-id">{{ requirement.cfts_id }}</td>
              <td class="req-id">{{ requirement.req_id }}</td>
              <td class="polarian-id">
                <a v-if="requirement.polarian_url" :href="requirement.polarian_url" target="_blank" class="polarian-link">
                  {{ requirement.polarian_id }}
                </a>
                <span v-else>{{ requirement.polarian_id }}</span>
              </td>
              <td class="scope">
                <span v-if="requirement.sys2_scope" :class="{ 'scope-sw': requirement.sys2_scope === 'SW' }">
                  {{ requirement.sys2_scope }}
                </span>
              </td>
              <td class="test-case">{{ requirement.test_case || '待填' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="searchResults === null" class="no-results">
      <p>請使用上方搜尋欄進行搜尋</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RequirementTable',
  props: {
    searchResults: {
      type: [Object, null],
      default: null
    },
    searchType: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      showOnlySW: false,
      showOnlySystem: false,
      showSWAndSystem: false
    }
  },
  computed: {
    filteredRequirements() {
      if (!this.searchResults || !this.searchResults.requirements) {
        return []
      }
      if (this.showOnlySW) {
        return this.searchResults.requirements.filter(req => req.sys2_scope === 'SW')
      }
      if (this.showOnlySystem) {
        return this.searchResults.requirements.filter(req => req.sys2_scope === 'System')
      }
      if (this.showSWAndSystem) {
        return this.searchResults.requirements.filter(req =>
          req.sys2_scope === 'SW' || req.sys2_scope === 'System'
        )
      }
      return this.searchResults.requirements
    }
  },
  watch: {
    showOnlySW(newVal) {
      if (newVal) {
        this.showOnlySystem = false
        this.showSWAndSystem = false
      }
    },
    showOnlySystem(newVal) {
      if (newVal) {
        this.showOnlySW = false
        this.showSWAndSystem = false
      }
    },
    showSWAndSystem(newVal) {
      if (newVal) {
        this.showOnlySW = false
        this.showOnlySystem = false
      }
    },
    searchResults(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          if (newVal.target_req_id && this.$refs.targetRow) {
            // Scroll to target row for Req.ID search
            this.$refs.targetRow.scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            })
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.requirement-table {
  margin-top: 20px;
}

.cfts-results, .req-results {
  background: linear-gradient(145deg, #d0d0d0 0%, #c0c0c0 50%, #b0b0b0 100%);
  border: 3px outset #c0c0c0;
  padding: 24px;
  margin: 16px;
  font-family: 'JetBrains Mono', monospace;
  box-shadow:
    2px 2px 0px #000,
    4px 4px 0px #808080;
  position: relative;
  overflow: hidden;
}

h2 {
  color: #000000;
  margin-bottom: 16px;
  font-size: 20px;
  font-family: 'Press Start 2P', monospace;
  text-shadow: 1px 1px 0px #fff;
}

.result-summary {
  display: flex;
  justify-content: space-between;
  background: #c0c0c0;
  padding: 16px;
  border: 2px inset #c0c0c0;
  margin-bottom: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  box-shadow: inset 1px 1px 2px #000;
}

.filter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #c0c0c0;
  padding: 12px 16px;
  border: 2px outset #c0c0c0;
  margin-bottom: 16px;
  font-family: 'JetBrains Mono', monospace;
}

.filter-checkboxes {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  color: #000000;
}

.filter-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  cursor: pointer;
}

.filter-checkbox span {
  user-select: none;
}

.filter-info {
  font-size: 13px;
  color: #cc0000;
  font-weight: bold;
}

.summary-item {
  font-size: 14px;
  font-family: 'JetBrains Mono', monospace;
}

.summary-item strong {
  color: #000000;
  font-weight: bold;
}

.table-container {
  overflow-x: auto;
  border: 2px inset #c0c0c0;
  background: #ffffff;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
}

.excel-table th {
  background: linear-gradient(145deg, #d0d0d0 0%, #c0c0c0 50%, #b0b0b0 100%);
  color: #000000;
  padding: 8px;
  text-align: left;
  font-weight: bold;
  border: 2px outset #c0c0c0;
  font-size: 14px;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: 1px 1px 0px #000;
  text-shadow: 1px 1px 0px #fff;
  position: relative;
}

.excel-table td {
  padding: 8px;
  border: 1px solid #808080;
  vertical-align: top;
  background: linear-gradient(145deg, #ffffff 0%, #f8f8f8 100%);
  font-family: 'JetBrains Mono', monospace;
  transition: all 0.3s ease;
  position: relative;
}

.excel-table tbody tr:hover {
  background: #000080; /* Classic navy blue - 1995 retro */
  color: #ffffff;
}

.excel-table tbody tr:hover td {
  background: transparent;
  color: #ffffff !important;
}

.excel-table tbody tr:hover .polarian-link {
  color: #ffffff !important;
}

.excel-table tbody tr:hover .polarian-id {
  color: #ffffff !important;
}

.even-row {
  background: #c0c0c0 !important;
}

.even-row:hover {
  background: #000080 !important; /* Same hover color for consistency */
  color: #ffffff !important;
}

/* Column specific styling - 1995 Retro Colors */
.row-number {
  background: #c0c0c0;
  text-align: center;
  font-weight: bold;
  color: #000000;
  width: 50px;
  border: 1px inset #c0c0c0;
}

.cfts-id {
  font-weight: bold;
  color: #800080; /* Classic purple */
  min-width: 100px;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
}

.req-id {
  font-weight: bold;
  color: #008000; /* Classic green */
  min-width: 90px;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
}

.polarian-id {
  color: #0066cc; /* Brighter blue for better visibility */
  min-width: 120px;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
  font-weight: 600;
}

.polarian-link {
  color: #0066ff; /* Brighter blue hyperlink */
  text-decoration: underline;
  font-weight: bold;
  cursor: pointer;
  transition: color 0.2s ease;
}

.polarian-link:hover {
  color: #cc00cc; /* Brighter magenta on hover */
  text-decoration: underline;
}


.scope {
  min-width: 150px;
  max-width: 200px;
  word-wrap: break-word;
}

.scope-sw {
  font-weight: bold;
  color: #cc0000; /* Strong red text */
  text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
}

.scope-empty {
  color: #808080;
  font-style: italic;
}

.test-case {
  min-width: 200px;
  max-width: 300px;
  word-wrap: break-word;
}

.no-results {
  text-align: center;
  color: #000000;
  font-size: 14px;
  margin-top: 32px;
  padding: 24px;
  background: #c0c0c0;
  border: 3px inset #c0c0c0;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: inset 1px 1px 2px #000;
}

/* Simple highlight for target row in Req.ID search - 1995 style */
.target-row {
  background: #ffff00 !important; /* Bright yellow highlight */
  border-left: 4px solid #ff0000; /* Red border */
}

.target-row td {
  background: transparent !important;
  font-weight: bold;
  color: #000000 !important;
}

/* Target indicator triangle */
.target-indicator {
  color: #ff0000; /* Red indicator */
  font-size: 14px;
  margin-right: 6px;
  font-weight: bold;
  display: inline-block;
  animation: pulse-indicator 1.5s ease-in-out infinite;
}

@keyframes pulse-indicator {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .result-summary {
    flex-direction: column;
    gap: 10px;
  }
  
  .excel-table {
    font-size: 12px;
  }
  
  .excel-table th,
  .excel-table td {
    padding: 8px 4px;
  }
}
</style>