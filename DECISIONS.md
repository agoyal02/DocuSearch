# Decision Log

This document records key architectural and design decisions made during the development of DocuSearch, particularly focusing on the observability implementation and UI improvements.

## 2025-01-17: Observability Implementation

### Decision: Custom Metrics Collector vs External Monitoring Library

**Context**: Need to implement comprehensive metrics collection for job processing, document processing, and system performance.

**Decision**: Implemented custom `MetricsCollector` class instead of using external libraries like Prometheus client or StatsD.

**Tradeoffs**:
- ✅ **Pros**: 
  - Zero external dependencies
  - Full control over data structure and persistence
  - Lightweight and fast
  - Easy to customize for specific use cases
  - No additional infrastructure requirements
- ❌ **Cons**:
  - More code to maintain
  - Need to implement percentiles and statistics manually
  - No built-in alerting capabilities
  - Limited integration with existing monitoring ecosystems

**Alternatives Considered**:
- Prometheus Python client library
- StatsD with custom metrics
- Custom database-based metrics storage

---

### Decision: In-Memory + File Persistence vs Database Storage

**Context**: Need to persist metrics data across application restarts while maintaining fast access.

**Decision**: Used in-memory storage with JSON file persistence instead of database storage.

**Tradeoffs**:
- ✅ **Pros**:
  - Fast in-memory access for real-time metrics
  - Simple file-based persistence
  - No database dependencies
  - Easy to backup and restore
  - Automatic loading on startup
- ❌ **Cons**:
  - Limited scalability for high-volume metrics
  - Potential data loss if application crashes before file write
  - No concurrent access from multiple instances
  - File I/O overhead for frequent updates

**Alternatives Considered**:
- SQLite database
- PostgreSQL/MySQL for production
- Redis for caching with database persistence

---

### Decision: Rolling Window vs Full History for Latency Tracking

**Context**: Need to calculate P50/P95 percentiles for job and document processing times.

**Decision**: Implemented rolling windows (1000 jobs, 10000 documents) instead of storing full history.

**Tradeoffs**:
- ✅ **Pros**:
  - Constant memory usage regardless of history length
  - Fast percentile calculations
  - Recent data is more relevant for performance monitoring
  - Prevents memory leaks in long-running applications
- ❌ **Cons**:
  - Loss of historical data beyond window size
  - Percentiles may not be accurate for very small datasets
  - No long-term trend analysis

**Alternatives Considered**:
- Store all historical data
- Time-based windows (e.g., last 24 hours)
- Hybrid approach with sampling

---

### Decision: Prometheus Format vs Custom JSON API

**Context**: Need to provide metrics in both human-readable and machine-readable formats.

**Decision**: Implemented both `/metrics` (JSON) and `/metrics/prometheus` (Prometheus format) endpoints.

**Tradeoffs**:
- ✅ **Pros**:
  - JSON format is easy to consume by web dashboards
  - Prometheus format enables integration with monitoring tools
  - Both formats serve different use cases
  - No need to choose between formats
- ❌ **Cons**:
  - Duplicate code for formatting metrics
  - Slightly more maintenance overhead
  - Two different data representations to keep in sync

**Alternatives Considered**:
- JSON only with custom Prometheus exporter
- Prometheus only with custom JSON parser
- Single endpoint with format parameter

---

## 2025-01-17: UI/UX Improvements

### Decision: Collapsible Sections vs Always Visible

**Context**: Need to reduce visual clutter while keeping important information accessible.

**Decision**: Made both Job History and System Metrics sections collapsible with click-to-expand functionality.

**Tradeoffs**:
- ✅ **Pros**:
  - Cleaner, less overwhelming interface
  - Users can focus on current tasks
  - Important information still accessible
  - Better mobile experience
  - Consistent UI pattern
- ❌ **Cons**:
  - Additional click required to access information
  - Users might not discover collapsible content
  - Slightly more complex JavaScript

**Alternatives Considered**:
- Accordion-style with multiple sections
- Tabbed interface
- Sidebar navigation
- Always visible with scroll

---

### Decision: Bottom Placement for Metrics Section

**Context**: Need to position the System Metrics section appropriately in the page layout.

**Decision**: Moved metrics section to the bottom of the page, after Job History.

**Tradeoffs**:
- ✅ **Pros**:
  - Metrics don't interfere with primary workflow
  - Natural reading order (upload → search → history → metrics)
  - Metrics are still easily accessible
  - Follows common dashboard patterns
- ❌ **Cons**:
  - Metrics might be overlooked at bottom
  - Requires scrolling to access
  - Less prominent than top placement

**Alternatives Considered**:
- Top of page after upload section
- Sidebar placement
- Floating metrics widget
- Dedicated metrics page

---

### Decision: Inline Event Handlers vs Event Listeners

**Context**: Need to handle click events for collapsible sections and clear history button.

**Decision**: Used inline `onclick` handlers for collapsible sections but kept event listeners for other functionality.

**Tradeoffs**:
- ✅ **Pros**:
  - Simple and direct for basic functionality
  - No need to wait for DOM ready
  - Clear association between HTML and JavaScript
  - Easy to understand and maintain
- ❌ **Cons**:
  - Mixed patterns in codebase
  - Inline handlers are harder to test
  - Less separation of concerns
  - Potential security concerns with user input

**Alternatives Considered**:
- All event listeners (consistent but more complex)
- All inline handlers (simpler but less flexible)
- Event delegation for dynamic content

---

## 2025-01-17: Metrics Collection Strategy

### Decision: Synchronous vs Asynchronous Metrics Collection

**Context**: Need to collect metrics during job and document processing without impacting performance.

**Decision**: Implemented synchronous metrics collection with thread-safe operations.

**Tradeoffs**:
- ✅ **Pros**:
  - Simple implementation
  - No additional complexity
  - Immediate data availability
  - No risk of data loss
- ❌ **Cons**:
  - Slight performance overhead during processing
  - Blocking operations during file I/O
  - Potential bottleneck under high load

**Alternatives Considered**:
- Asynchronous collection with queues
- Background thread for metrics processing
- Sampling-based collection

---

### Decision: File-based vs Memory-only Metrics Storage

**Context**: Need to persist metrics data for analysis and monitoring.

**Decision**: Used hybrid approach with in-memory storage and periodic file persistence.

**Tradeoffs**:
- ✅ **Pros**:
  - Fast access for real-time metrics
  - Data persistence across restarts
  - Simple backup and restore
  - No external dependencies
- ❌ **Cons**:
  - Potential data loss on crash
  - File I/O overhead
  - Not suitable for distributed systems

**Alternatives Considered**:
- Memory-only (fast but no persistence)
- Database-only (persistent but slower)
- External metrics service (scalable but complex)

---

## 2025-01-17: Error Handling and Resilience

### Decision: Graceful Degradation vs Fail-Fast for Metrics

**Context**: Need to handle metrics collection failures without breaking core functionality.

**Decision**: Implemented graceful degradation where metrics failures don't affect document processing.

**Tradeoffs**:
- ✅ **Pros**:
  - Core functionality always works
  - Better user experience
  - Easier debugging
  - No cascading failures
- ❌ **Cons**:
  - Silent failures might go unnoticed
  - Metrics data might be incomplete
  - Harder to detect metrics issues

**Alternatives Considered**:
- Fail-fast (metrics failure stops processing)
- Retry mechanisms
- Circuit breaker pattern

---

## Future Considerations

### Potential Improvements
- **Database Integration**: Consider PostgreSQL for production metrics storage
- **Real-time Updates**: WebSocket-based live metrics updates
- **Advanced Analytics**: Trend analysis and anomaly detection
- **Alerting**: Integration with notification systems
- **Distributed Metrics**: Support for multiple application instances
- **Metrics Export**: Additional export formats (CSV, Graphite, etc.)

### Technical Debt
- **Code Duplication**: Metrics formatting logic could be refactored
- **Error Handling**: More comprehensive error handling for edge cases
- **Testing**: Unit tests for metrics collection logic
- **Documentation**: API documentation for metrics endpoints
