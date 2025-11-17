# Feature Specification: Demo Code Consolidation

**Feature Branch**: `005-consolidate-11-redundant-demo`  
**Created**: 2025-11-17  
**Status**: Ready for Planning  
**Priority**: HIGH  
**Effort**: 8 hours  
**Impact**: 7/10 (Major code quality improvement)

## Executive Summary

Consolidate 11 redundant demo files (demo_clear.py, demo_final.py, demo_simple.py, etc.) totaling 2,500+ lines of duplicated code into a single, unified demonstration system with feature flags for different visualization modes. This transforms GRAPHMAIL from a prototype with scattered, overlapping demos into a professional system with a single, well-tested demo interface.

**Code Quality Context**: Current code duplication is 27.5%. This feature reduces it to under 5% by eliminating the largest source of duplication (demo files).

## Constitutional Alignment

This specification adheres to the GRAPHMAIL constitution:

- **Article VI: Test-Driven Development** - Consolidated code is easier to test (one test suite vs 11)
- **Article IX: Performance Budgets** - Single codebase reduces maintenance overhead
- **Article VII: API-First Design** - Unified demo demonstrates API capabilities consistently

## User Scenarios & Testing

### Primary User Story

**As a** user evaluating GRAPHMAIL for the first time  
**I want** a single, comprehensive demo that showcases all capabilities  
**So that** I can understand what the system can do without navigating 11 different demo files

### Secondary User Story

**As a** developer maintaining GRAPHMAIL  
**I want** a single demo codebase with clear separation of concerns  
**So that** fixing bugs or adding features doesn't require updating 11 files

### Acceptance Scenarios

**Scenario 1: Unified Demo Launch (Happy Path)**
- **Given** a user wants to see GRAPHMAIL capabilities
- **When** they run `python demo.py --mode all` (or `streamlit run demo.py`)
- **Then** the unified demo displays all visualization modes in tabs
- **And** modes include: Complete Graph, Collaboration Graph, People Profiles, Timeline Analysis
- **And** each mode is fully functional (no degraded features)
- **And** switching modes is instant (no file reloads)

**Scenario 2: Selective Mode Visualization**
- **Given** a user wants to see only collaboration analysis
- **When** they run `python demo.py --mode collaboration`
- **Then** only the collaboration graph is displayed
- **And** UI is simplified (no unnecessary tabs)
- **And** performance is equivalent to dedicated demo_collaboration_graph.py

**Scenario 3: Developer Adds New Visualization**
- **Given** a developer wants to add "temporal evolution" visualization
- **When** they implement it in the unified demo
- **Then** new visualization appears in the tab selector
- **And** no other demo files need updating
- **And** existing visualizations continue working

**Scenario 4: Bug Fix Propagation**
- **Given** a bug is found in graph rendering logic
- **When** developer fixes it in the unified demo
- **Then** fix applies to all visualization modes
- **And** no duplicate fixes needed (unlike current 11-file setup)

**Scenario 5: Feature Flag Configuration**
- **Given** an environment where only basic visualizations are enabled
- **When** ENABLE_ADVANCED_VIZ=false
- **Then** advanced modes (temporal, collaboration) are hidden
- **And** basic modes (simple graph, people profiles) remain visible
- **And** user isn't confused by disabled features

### Edge Cases and Error Conditions

- **Invalid Mode**: `--mode invalid` shows error with list of valid modes
- **Missing Data**: Demo gracefully handles missing output files with clear messages
- **Large Datasets**: Demo handles 1000+ nodes/edges without crashing (pagination or sampling)
- **Conflicting Flags**: `--mode simple --mode complete` uses last specified mode
- **No Data Generated**: Demo detects empty/missing output and suggests running pipeline first

## Requirements

### Functional Requirements

- **FR-001**: System MUST consolidate 11 demo files into single demo.py with feature flags for different modes
- **FR-002**: System MUST support 6 visualization modes: simple, complete, collaboration, human, timeline, all (tabs)
- **FR-003**: System MUST preserve ALL unique functionality from existing demos (no feature loss)
- **FR-004**: System MUST allow mode selection via command-line flags (--mode) or UI controls (tabs)
- **FR-005**: System MUST share common code (graph loading, data parsing, Plotly helpers) across all modes
- **FR-006**: System MUST provide clear error messages when data files are missing or corrupted
- **FR-007**: System MUST support feature flags to enable/disable advanced visualizations per environment
- **FR-008**: System MUST maintain performance equivalence to original dedicated demo files
- **FR-009**: System MUST include unit tests for each visualization mode and shared utilities
- **FR-010**: System MUST delete original 11 demo files after consolidation (no residual duplication)

### Non-Functional Requirements

- **NFR-001**: **Maintainability** - Code duplication reduced from 27.5% to <5% (measured by similarity analysis)
- **NFR-002**: **Usability** - Single entry point (demo.py) is more discoverable than 11 scattered files
- **NFR-003**: **Performance** - Mode switching takes <1 second (perceived as instant)
- **NFR-004**: **Testability** - Single test suite covers all modes (vs 11 separate test files)
- **NFR-005**: **Documentation** - README updated with demo usage examples for each mode

### Business Rules

- **BR-001**: Default mode is "all" (tabbed interface showing all visualizations)
- **BR-002**: Command-line flag `--mode` overrides default mode selection
- **BR-003**: Shared utilities are extracted to src/utils/demo_helpers.py (no duplication)
- **BR-004**: Feature flags in configuration control visibility of advanced modes
- **BR-005**: Original demo files deleted after consolidation (prevents divergence)

### Key Entities

- **DemoMode**: Enum of visualization modes
  - `SIMPLE`: Basic knowledge graph (nodes + edges)
  - `COMPLETE`: Full graph with all node types (projects, topics, challenges, resolutions)
  - `COLLABORATION`: Collaboration network (people, email frequency, roles)
  - `HUMAN`: People profiles with timeline (roles, topics, communication patterns)
  - `TIMELINE`: Temporal evolution of projects (phases, milestones, bottlenecks)
  - `ALL`: Tabbed interface with all modes

- **DemoConfig**: Configuration for demo behavior
  - `mode`: Selected DemoMode
  - `data_directory`: Path to output_hackathon/ (default: "./output_hackathon")
  - `enable_advanced_viz`: Feature flag for advanced modes (default: True)
  - `max_nodes_display`: Limit for large graphs (default: 500)
  - `color_scheme`: Graph color palette (default: "viridis")

- **SharedHelpers**: Common utilities (no duplication)
  - `load_knowledge_graph()`: Load JSON graph from output
  - `load_project_intelligence()`: Load extracted project data
  - `load_people_profiles()`: Load people/org data
  - `create_plotly_figure()`: Generate Plotly graph with consistent styling
  - `format_metadata()`: Format node/edge metadata for display

### Integration Points

- **Output Files**: Reads from output_hackathon/ (knowledge_graph.json, project_intelligence.json, etc.)
- **Streamlit**: UI framework for interactive demo
- **Plotly**: Visualization library for graphs
- **Configuration System**: Feature flags from settings.enable_advanced_viz

## Success Criteria

### Definition of Done

- [ ] Single demo.py file with 6 visualization modes implemented
- [ ] All unique functionality from 11 original demos preserved (feature parity testing)
- [ ] Shared utilities extracted to src/utils/demo_helpers.py (no code duplication)
- [ ] Command-line interface supports --mode flag with validation
- [ ] Streamlit UI supports tabbed mode selection
- [ ] Feature flags control visibility of advanced visualizations
- [ ] Unit tests for each mode and shared utilities (50+ test cases)
- [ ] Performance tests show mode switching <1s
- [ ] Documentation updated with demo usage examples
- [ ] Original 11 demo files deleted (code duplication measured <5%)

### Measurable Outcomes

| Metric | Current | Target | Success? |
|--------|---------|--------|----------|
| Demo Files | 11 | 1 | ✅ File count validates |
| Code Duplication | 27.5% | <5% | ✅ Similarity analysis validates |
| Lines of Code (Demos) | ~3,000 | ~500 | ✅ 83% reduction |
| Maintenance Overhead | 11 files to update | 1 file | ✅ Measured by commit history |
| Mode Switching Time | N/A (file reload) | <1s | ✅ Benchmark validates |
| Test Coverage | Untested | 80%+ | ✅ pytest coverage validates |

### Acceptance Tests

**Test Suite 1: Feature Parity**
```
Given: All 11 original demo files
When: Each unique feature is identified (complete graph, collaboration, timeline, etc.)
Then: Unified demo provides equivalent functionality for each feature
And: Visual output matches original demos (manual QA)
And: No features are lost in consolidation
```

**Test Suite 2: Mode Selection**
```
Given: Unified demo with 6 modes
When: User selects each mode via --mode flag or UI tab
Then: Correct visualization is displayed
And: Mode selection is validated (invalid mode shows error)
And: Default mode (all) works without flags
```

**Test Suite 3: Code Duplication Elimination**
```
Given: Original codebase with 27.5% duplication
When: Consolidation is complete
Then: Code similarity analysis shows <5% duplication
And: Shared utilities are extracted (no copy-paste code)
And: Original 11 demo files are deleted
```

**Test Suite 4: Error Handling**
```
Given: Missing or corrupted output files
When: User runs demo
Then: Clear error messages explain what's missing
And: Demo suggests running pipeline first
And: System never crashes (graceful degradation)
```

**Test Suite 5: Performance**
```
Given: Large dataset (500+ nodes, 1000+ edges)
When: User switches between modes
Then: Mode switching completes in <1 second
And: Graph rendering is smooth (60fps)
And: Memory usage is reasonable (<500MB)
```

## Scope

### In Scope
- Consolidate all 11 demo files into single demo.py
- Extract shared utilities to src/utils/demo_helpers.py
- Implement 6 visualization modes (simple, complete, collaboration, human, timeline, all)
- Command-line interface (--mode flag)
- Streamlit tabbed UI
- Feature flags for advanced visualizations
- Unit tests for all modes
- Delete original demo files

### Out of Scope (Future Enhancements)
- Real-time data updates (Phase 2 - currently static visualization)
- Export visualizations to PDF/PNG (Phase 2)
- Custom visualization themes (Phase 3)
- 3D graph visualization (Phase 3)
- Interactive graph editing (Phase 4)

## Dependencies

- **Required Before**: Configuration Management (for feature flags)
- **Blocks**: None
- **Integrates With**: Output files (output_hackathon/), Streamlit, Plotly

## Assumptions

1. Streamlit provides sufficient functionality for tabbed interface
2. Plotly performance is acceptable for 500+ node graphs
3. Feature parity can be achieved without degrading performance
4. Users prefer unified demo over 11 separate files
5. Mode switching <1s is achievable with current Streamlit architecture

## Performance Considerations

- **Mode Switching**: Must complete in <1s (measured by benchmark)
- **Large Graphs**: Pagination or sampling for >500 nodes to maintain responsiveness
- **Memory**: Lazy loading of data (only load what's needed for current mode)
- **Rendering**: Plotly optimization for smooth graph rendering (60fps)

## Refactoring Strategy

1. **Phase 1: Extract Shared Code** (2 hours)
   - Identify common patterns across 11 demos
   - Extract to src/utils/demo_helpers.py
   - Test shared utilities in isolation

2. **Phase 2: Implement Unified Demo** (4 hours)
   - Create demo.py with mode selection logic
   - Implement each visualization mode using shared utilities
   - Add command-line interface and Streamlit UI

3. **Phase 3: Testing & Validation** (1 hour)
   - Unit tests for each mode
   - Feature parity validation (compare outputs)
   - Performance benchmarks

4. **Phase 4: Cleanup** (1 hour)
   - Delete original 11 demo files
   - Update documentation
   - Verify code duplication <5%

## Success Metrics

- **Code Quality**: <5% duplication (from 27.5%)
- **Maintainability**: 1 file to maintain (from 11)
- **Feature Parity**: 100% of original functionality preserved
- **Performance**: <1s mode switching
- **Test Coverage**: 80%+ for demo code

---

## Review & Acceptance Checklist

### Constitutional Compliance
- [x] Aligns with Article VI (Test-Driven Development)
- [x] Supports Article IX (Performance Budgets)
- [x] Follows Article VII (API-First Design)

### Content Quality
- [x] No implementation details (Streamlit, Plotly mentioned as examples only)
- [x] Focused on code quality outcomes
- [x] Written for stakeholders (explains WHY consolidation matters)
- [x] All mandatory sections completed

### Requirement Quality
- [x] All 10 functional requirements testable and measurable
- [x] 5 non-functional requirements cover key quality attributes
- [x] Success criteria clearly defined with metrics
- [x] 5 acceptance scenarios cover modes, errors, performance

### Specification Completeness
- [x] Refactoring strategy documented (4-phase approach)
- [x] Performance considerations addressed (<1s switching)
- [x] Integration points identified (output files, Streamlit, Plotly)
- [x] Edge cases addressed (missing data, large graphs, invalid modes)
- [x] Success criteria measurable (duplication %, file count, switching time)

### Clarification Assessment
- [x] No [NEEDS CLARIFICATION] markers
- [x] Ready for planning phase
- [x] All requirements unambiguous
- [x] Scope clearly bounded (in/out scope documented)

---

## Next Phase Readiness

**Status**: ✅ **READY FOR PLANNING PHASE**

This specification is complete, unambiguous, and ready for technical planning. All requirements are testable, success criteria are measurable, and constitutional alignment is verified.

**Recommended Next Step**: Run `/speckit.plan` to generate implementation plan

---

*This specification follows spec-kit methodology with GRAPHMAIL constitution-driven development. Priority: HIGH (reduces code duplication from 27.5% to <5%).*
