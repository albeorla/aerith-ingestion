# Project Roadmap

## Incomplete Tasks (Reverse Order)

1. **[Performance]** Implement dynamic batching based on API latency
   * **[Performance - Subtask]** Implement API Latency Monitoring in `gemini_service.py` **[COMPLETED]**
   * **[Performance - Subtask]** Integrate Latency Data into `RequestManager` for Dynamic Batching **[IN PROGRESS]**
   * **[Performance - Subtask]** Test and Validate Dynamic Batching
2. **[Refactoring]** Complete transition from legacy methods
3. **[Testing]** Add comprehensive integration tests
4. **[Cleanup]** Investigate and remove unused or placeholder code
5. **[Concurrency]** Validate concurrency boundaries (max batching size, resource usage)
6. **[Monitoring]** Implement alerting thresholds for key metrics

---

## Completed Tasks by Initiative

### GTD System Integration (Phase 3)
✓ Gemini service integration
• Implement GTD workflow engine [IN PROGRESS]
• Develop context-aware processing [IN PROGRESS]
• Build task prioritization system [PENDING]

### Concurrency
- **Implement serious concurrency and parallel processing from the outset**
- **Add basic concurrency monitoring**
- **Implement dynamic concurrency scaling**

### Best Practices / Resiliency

- **Skip detailed input validation for now**
- **Re-use existing backoff and circuit breaker patterns**

### Request Management / Refactoring

- **Refactor GeminiService to integrate with RequestManager**
- **Implement enhanced request deduplication**

### Pipeline Integrity

- **Validate core pipeline integrity**
- **Implement main logic sanity checks**

### Monitoring

- **Add monitoring infrastructure**
- **Add monitoring to all service entry points**

---

**Completed**: 14/18 (per original count)
**Remaining**: 4 critical items (plus additional refinements), with further focus on monitoring and performance.

**Note**: Actual tallies may need updating if the counts in the original list do not fully match recent changes.
