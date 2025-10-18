<template>
  <div class="melco-detail-page">
    <div class="header-section">
      <button @click="$emit('back')" class="back-button">← Back to Search</button>
      <h1 class="melco-title">{{ melcoId }}</h1>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="requirement" class="content-sections">
      <!-- Upper Section: SYS.2 Requirement Details -->
      <div class="requirement-section">
        <h2>SYS.2 Requirement Details</h2>
        <div class="detail-card">
          <div class="detail-row">
            <div class="detail-label">CFTS:</div>
            <div class="detail-value">{{ requirement.cfts_id }} - {{ requirement.cfts_name }}</div>
          </div>

          <div class="detail-row">
            <div class="detail-label">要件(英語):</div>
            <div class="detail-value">{{ requirement.requirement_en || 'N/A' }}</div>
          </div>

          <div class="detail-row">
            <div class="detail-label">理由(英語):</div>
            <div class="detail-value">{{ requirement.reason_en || 'N/A' }}</div>
          </div>

          <div class="detail-row">
            <div class="detail-label">補足(英語):</div>
            <div class="detail-value">{{ requirement.supplement_en || 'N/A' }}</div>
          </div>

          <div class="detail-row">
            <div class="detail-label">確認フェーズ:</div>
            <div class="detail-value">{{ requirement.confirmation_phase || 'N/A' }}</div>
          </div>

          <div class="detail-row">
            <div class="detail-label">検証基準:</div>
            <div class="detail-value">{{ requirement.verification_criteria || 'N/A' }}</div>
          </div>
        </div>
      </div>

      <!-- Lower Section: Test Cases -->
      <div class="testcase-section">
        <h2>Related Test Cases ({{ testcases.length }})</h2>
        <div v-if="testcases.length === 0" class="placeholder-card">
          <p>No test cases found for this Melco ID</p>
        </div>
        <div v-else class="testcase-table-container">
          <table class="testcase-table">
            <thead>
              <tr>
                <th>Source</th>
                <th>Title</th>
                <th>Section</th>
                <th>Test Item (EN)</th>
                <th>Precondition/Procedure (JP)</th>
                <th>Criteria (JP)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(tc, index) in testcases" :key="index">
                <td>{{ tc.source }}</td>
                <td>{{ tc.title }}</td>
                <td>{{ tc.section }}</td>
                <td class="test-item">{{ tc.test_item_en }}</td>
                <td class="precondition">{{ tc.precondition_procedure_jp }}</td>
                <td class="criteria">{{ tc.criteria_jp }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MelcoDetailPage',
  props: {
    melcoId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      requirement: null,
      testcases: [],
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.fetchRequirementDetails()
    await this.fetchTestCases()
  },
  methods: {
    async fetchRequirementDetails() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`http://localhost:8001/sys2/requirement/${this.melcoId}`)
        if (!response.ok) {
          throw new Error(`Failed to fetch requirement: ${response.statusText}`)
        }
        this.requirement = await response.json()
      } catch (err) {
        console.error('Error fetching requirement:', err)
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    async fetchTestCases() {
      try {
        const response = await fetch(`http://localhost:8001/testcases/by-feature-id/${this.melcoId}`)
        if (!response.ok) {
          console.warn('No test cases found for this Melco ID')
          this.testcases = []
          return
        }
        this.testcases = await response.json()
      } catch (err) {
        console.error('Error fetching test cases:', err)
        this.testcases = []
      }
    }
  }
}
</script>

<style scoped>
.melco-detail-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  min-height: 100vh;
}

.header-section {
  background: white;
  padding: 24px;
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.back-button {
  padding: 8px 16px;
  background: white;
  color: #3b82f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.back-button:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.melco-title {
  color: #1f2937;
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
}

.loading, .error {
  text-align: center;
  padding: 48px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-size: 14px;
}

.error {
  color: #dc2626;
  font-weight: 500;
}

.content-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.requirement-section, .testcase-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

h2 {
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  padding: 20px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.detail-card {
  padding: 24px;
}

.detail-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.detail-value {
  color: #1f2937;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.placeholder-card {
  padding: 48px;
  text-align: center;
  color: #6b7280;
}

.placeholder-card p {
  margin: 0;
  font-size: 14px;
}

.testcase-table-container {
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

.testcase-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.testcase-table th {
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

.testcase-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
  color: #1f2937;
  line-height: 1.6;
}

.testcase-table tbody tr {
  transition: background-color 0.15s ease;
}

.testcase-table tbody tr:hover {
  background: #f3f4f6;
}

.testcase-table td.test-item,
.testcase-table td.precondition,
.testcase-table td.criteria {
  min-width: 200px;
  max-width: 400px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* Responsive design */
@media (max-width: 768px) {
  .melco-detail-page {
    padding: 16px;
  }

  .detail-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .melco-title {
    font-size: 20px;
  }

  h2 {
    font-size: 16px;
    padding: 16px 20px;
  }

  .testcase-table {
    font-size: 12px;
  }

  .testcase-table th,
  .testcase-table td {
    padding: 10px 12px;
  }
}
</style>
