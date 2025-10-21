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


      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th>SR26 Description</th>
              <th>ReqIF.ForeignID</th>
              <th>Source Id</th>
              <th>SR24 Description</th>
              <th>Melco Id</th>
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
              <td class="sr26-description" v-html="highlightDifferences(requirement.description, requirement.sr24_description)"></td>
              <td class="reqif-foreign-id">{{ requirement.req_id }}</td>
              <td class="source-id">
                {{ requirement.source_id || '' }}
              </td>
              <td class="sr24-description">{{ requirement.sr24_description || '' }}</td>
              <td class="melco-id">
                <template v-if="requirement.melco_id">
                  <div v-for="(melcoId, idx) in splitMelcoIds(requirement.melco_id)" :key="idx" class="melco-id-item">
                    <a @click.prevent="viewMelcoDetail(melcoId)" class="melco-link">
                      {{ melcoId }}
                    </a>
                  </div>
                </template>
                <span v-else>-</span>
              </td>
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
  computed: {
    filteredRequirements() {
      if (!this.searchResults || !this.searchResults.requirements) {
        return []
      }
      return this.searchResults.requirements
    }
  },
  methods: {
    viewMelcoDetail(melcoId) {
      // Clean the Melco ID before emitting (already cleaned by splitMelcoIds, but ensure it's clean)
      const cleanedId = melcoId.trim().replace(/^#+|#+$/g, '')
      this.$emit('view-melco-detail', cleanedId)
    },
    splitMelcoIds(melcoIdString) {
      // Split by newline or comma, clean # symbols, and filter out empty strings
      if (!melcoIdString) return []
      return melcoIdString
        .split(/[\n,]+/)
        .map(id => id.trim().replace(/^#+|#+$/g, ''))  // Remove leading/trailing # symbols
        .filter(id => id.length > 0)
    },
    highlightDifferences(sr26Text, sr24Text) {
      // Compare SR26 and SR24, highlight differences in SR26
      if (!sr26Text) return ''

      // If SR24 is empty but SR26 has content, highlight all SR26
      if (!sr24Text) {
        return `<span class="text-diff">${this.escapeHtml(sr26Text)}</span>`
      }

      // If they're exactly the same, no highlighting needed
      if (sr26Text === sr24Text) {
        return this.escapeHtml(sr26Text)
      }

      // Split by sentence (period, comma, semicolon, etc.)
      const sr26Sentences = sr26Text.split(/([.,;!?]+\s*)/)
      const sr24Sentences = sr24Text.split(/([.,;!?]+\s*)/)

      let result = []

      for (let i = 0; i < sr26Sentences.length; i++) {
        const sentence = sr26Sentences[i]
        if (!sentence) continue

        if (i >= sr24Sentences.length || sentence !== sr24Sentences[i]) {
          // Different sentence/fragment - highlight it
          result.push(`<span class="text-diff">${this.escapeHtml(sentence)}</span>`)
        } else {
          // Same sentence/fragment
          result.push(this.escapeHtml(sentence))
        }
      }

      return result.join('')
    },
    escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }
  },
  watch: {
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* Global style for dynamically inserted text-diff spans */
:deep(.text-diff) {
  background-color: #fef3c7;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
  color: #92400e;
}

.cfts-results, .req-results {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

h2 {
  color: #1f2937;
  padding: 20px 24px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.result-summary {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.summary-item {
  font-size: 14px;
  color: #6b7280;
}

.summary-item strong {
  color: #374151;
  font-weight: 600;
  margin-right: 8px;
}

.table-container {
  overflow-x: auto;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.excel-table th {
  background: #f9fafb;
  color: #374151;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.excel-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
  color: #1f2937;
  line-height: 1.5;
}

.excel-table tbody tr {
  transition: background-color 0.15s ease;
}

.excel-table tbody tr:hover {
  background: #f3f4f6;
}

.sr24-description,
.sr26-description {
  min-width: 250px;
  max-width: 400px;
  word-wrap: break-word;
}

.source-id {
  min-width: 140px;
  text-align: center;
  color: #6b7280;
  white-space: nowrap;
}

.source-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s ease;
}

.source-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.reqif-foreign-id {
  font-weight: 500;
  color: #059669;
  min-width: 100px;
  text-align: center;
}

.melco-id {
  min-width: 150px;
  text-align: center;
  vertical-align: top;
}

.melco-id-item {
  margin: 2px 0;
}

.melco-link {
  color: #7c3aed;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  white-space: nowrap;
}

.melco-link:hover {
  color: #6d28d9;
  background: #ede9fe;
  text-decoration: none;
}

.no-results {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  padding: 48px 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.target-row {
  background: #fef3c7 !important;
  border-left: 3px solid #f59e0b;
}

.target-row td {
  font-weight: 500;
}

@media (max-width: 768px) {
  .requirement-table {
    padding: 16px;
  }

  .result-summary {
    flex-direction: column;
    gap: 12px;
  }

  .excel-table {
    font-size: 12px;
  }

  .excel-table th,
  .excel-table td {
    padding: 10px 12px;
  }
}
</style>