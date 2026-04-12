# Test Scenarios Document

## Overview
This document covers test scenarios for the GCFB Operational Intelligence Dashboard, including happy path flows, error cases, and edge cases.

---

## Module 1: Demand Heatmap Testing

### Happy Path Scenarios

#### TC-1.1: View Today's Forecast
**Steps:**
1. Navigate to the dashboard home page
2. Verify the map loads with ZIP code boundaries
3. Verify ZIP codes are color-coded (green, yellow, red)
4. Verify the date toggle shows "Today" as selected

**Expected Result:**
- Map displays 6-county area with colored ZIP codes
- Legend shows demand levels correctly
- No errors in console

#### TC-1.2: Switch to Tomorrow's Forecast
**Steps:**
1. Click "Tomorrow" in date toggle
2. Verify map updates with new forecast data
3. Verify colors may change based on new predictions

**Expected Result:**
- Map refreshes with tomorrow's forecast
- Loading indicator appears briefly
- ZIP colors update to reflect new data

#### TC-1.3: View ZIP Code Details
**Steps:**
1. Click on any colored ZIP code on map
2. Verify side panel opens on the right
3. Check that predicted headcount is displayed
4. Verify % change vs last week is shown
5. Check top 3 contributing factors are listed
6. Verify partner sites in that ZIP are displayed

**Expected Result:**
- Side panel slides in from right
- All forecast details displayed correctly
- Partner sites show with program types and capacities
- Close button works to dismiss panel

### Error Cases

#### TC-1.4: API Failure - Forecast Data
**Steps:**
1. Stop backend server
2. Try to switch date toggle
3. Observe error handling

**Expected Result:**
- Error notification appears
- Map shows last successful data or empty state
- No application crash

#### TC-1.5: Invalid ZIP Code Selection
**Steps:**
1. Click on ZIP code with no data
2. Verify error handling

**Expected Result:**
- Side panel shows "No data available" message
- Application continues to function

### Edge Cases

#### TC-1.6: Slow Network Connection
**Steps:**
1. Throttle network to slow 3G
2. Switch between date options
3. Verify loading states

**Expected Result:**
- Loading indicators display
- No duplicate requests
- Data eventually loads

---

## Module 2: Dispatch Planner Testing

### Happy Path Scenarios

#### TC-2.1: Generate Dispatch Plan
**Steps:**
1. Navigate to Dispatch Planner tab
2. Set truck count to 3
3. Set volunteer count to 100
4. Click "Generate Today's Plan"
5. Wait for optimization to complete

**Expected Result:**
- Loading indicator displays
- Plan summary shows total sites, distance, and headcount
- Truck routes listed with stops
- Map shows colored routes for each truck
- Routes start and end at warehouse

#### TC-2.2: View Truck Route Details
**Steps:**
1. Generate a dispatch plan
2. Review each truck's route in the left panel
3. Hover over route lines on map

**Expected Result:**
- Each truck shows stop order, site names, and quantities
- Distance and estimated time displayed
- Total load in lbs shown per truck
- Map routes visually distinguishable by color

#### TC-2.3: Print Dispatch Plan
**Steps:**
1. Generate a dispatch plan
2. Click "Print" button
3. Review print preview

**Expected Result:**
- Print-friendly layout displays
- Navigation and buttons hidden
- Route details preserved
- Readable format

### Error Cases

#### TC-2.4: Invalid Truck Count
**Steps:**
1. Set truck count to 0
2. Try to generate plan

**Expected Result:**
- Generate button disabled
- Validation message displayed

#### TC-2.5: OR-Tools Optimization Failure
**Steps:**
1. Set truck count to 1 with very small capacity
2. Generate plan with many high-demand sites

**Expected Result:**
- Error message displays
- Suggests adjusting parameters
- No application crash

### Edge Cases

#### TC-2.6: No Active Trucks Available
**Steps:**
1. Set all trucks to maintenance status in database
2. Try to generate plan

**Expected Result:**
- Error: "No active trucks available"
- Graceful degradation

---

## Module 3: Expiration Alert Testing

### Happy Path Scenarios

#### TC-3.1: View Expiring Items
**Steps:**
1. Navigate to Expiration Alerts tab
2. Review list of expiring items
3. Verify urgency color coding

**Expected Result:**
- Items listed with urgency (red < 24hrs, orange < 72hrs)
- Item details: name, quantity, category, days left
- "Find Sites" button visible for each item

#### TC-3.2: Find Suggested Sites for Item
**Steps:**
1. Click "Find Sites" for an expiring item
2. Wait for site matching to complete
3. Review top 3 suggested sites

**Expected Result:**
- Loading indicator displays
- Top 3 sites listed with:
  - Site name and address
  - Distance from warehouse
  - Predicted demand
  - Match score and explanation
- "Assign" button visible for each site

#### TC-3.3: Assign Item to Site
**Steps:**
1. Find sites for an expiring item
2. Click "Assign" for top suggested site
3. Navigate to Dispatch Planner

**Expected Result:**
- Success message: "Successfully assigned to [site name]"
- Item assignment appears in Dispatch Planner sidebar
- Assignment count incremented

### Error Cases

#### TC-3.4: No Expiring Items
**Steps:**
1. Ensure no items expiring within 72 hours
2. Navigate to Expiration Alerts tab

**Expected Result:**
- Empty state message: "No items expiring within 72 hours"
- Checkmark icon displayed
- No errors

#### TC-3.5: Site Matching Failure
**Steps:**
1. Disconnect from API
2. Try to find sites for item

**Expected Result:**
- Error message displayed
- "Find Sites" button remains enabled for retry
- No crash

### Edge Cases

#### TC-3.6: Multiple Assignments in Same Session
**Steps:**
1. Assign 3 different items to different sites
2. Navigate to Dispatch Planner
3. Verify all assignments appear

**Expected Result:**
- All assignments tracked in state
- Dispatch Planner shows all 3 assignments
- No duplicate assignments

---

## Integration Testing

### TC-INT-1: End-to-End Demo Flow
**Steps:**
1. Start on Demand Heatmap
2. Click high-demand ZIP code
3. Review forecast details
4. Navigate to Expiration Alerts
5. Find sites for expiring item
6. Assign item to suggested site
7. Navigate to Dispatch Planner
8. Verify assignment appears
9. Generate dispatch plan
10. Review complete plan with routes

**Expected Result:**
- Seamless flow between modules
- Data consistency maintained
- Assignment integrated into plan
- All visualizations work

### TC-INT-2: State Synchronization
**Steps:**
1. Make assignment in Expiration Alerts
2. Switch to Dispatch Planner
3. Verify assignment visible
4. Generate plan
5. Switch back to Expiration Alerts
6. Verify item no longer shows as needing assignment

**Expected Result:**
- Global state synchronized across modules
- No stale data
- UI updates reflect changes

---

## Performance Testing

### TC-PERF-1: Forecast API Response Time
**Test:** Measure response time for /api/forecast endpoint

**Acceptance Criteria:**
- Response time < 2 seconds for all ZIPs
- No timeout errors

### TC-PERF-2: Dispatch Optimization Time
**Test:** Measure time to generate dispatch plan with 5 trucks and 50 sites

**Acceptance Criteria:**
- Optimization completes in < 10 seconds
- Progress indicator displays during wait

### TC-PERF-3: Map Rendering Performance
**Test:** Load map with 60 ZIP boundaries and 50 site markers

**Acceptance Criteria:**
- Initial map load < 3 seconds
- Smooth zoom and pan interactions
- No lag when clicking ZIP codes

---

## Cross-Browser Testing

### Browsers to Test
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)

### Test Cases
- [ ] All features work in each browser
- [ ] Map renders correctly
- [ ] Routes display properly
- [ ] CSS styling consistent
- [ ] No console errors

---

## Mobile Responsiveness

### TC-MOBILE-1: Tablet View (768px - 1024px)
**Steps:**
1. Resize browser to tablet dimensions
2. Test all three modules

**Expected Result:**
- Layout adapts to smaller screen
- All functionality accessible
- Touch interactions work
- No horizontal scroll

### TC-MOBILE-2: Desktop View (1280px+)
**Steps:**
1. View on standard desktop resolution
2. Verify optimal layout

**Expected Result:**
- Full feature set visible
- Proper spacing and alignment
- Map takes appropriate space

---

## Accessibility Testing

### TC-A11Y-1: Keyboard Navigation
**Steps:**
1. Navigate entire app using only keyboard
2. Tab through all interactive elements
3. Verify focus indicators visible

**Expected Result:**
- All buttons and links accessible via Tab
- Enter/Space activate buttons
- Focus outlines visible
- Logical tab order

### TC-A11Y-2: Screen Reader Compatibility
**Steps:**
1. Use screen reader to navigate app
2. Verify labels announced correctly

**Expected Result:**
- Form labels read correctly
- Button purposes clear
- Map regions described
- Alerts announced

### TC-A11Y-3: Color Contrast
**Test:** Verify all text meets WCAG 2.1 Level AA contrast requirements

**Expected Result:**
- Text contrast ratio ≥ 4.5:1 for normal text
- Text contrast ratio ≥ 3:1 for large text
- Color not sole means of conveying information

---

## Known Issues and Limitations

### Issue 1: Weather API Rate Limiting
**Description:** OpenWeatherMap API has rate limits
**Workaround:** Fallback to default weather values
**Severity:** Low

### Issue 2: Large Dataset Performance
**Description:** Map may slow down with 100+ partner sites
**Workaround:** Limit visible markers or implement clustering
**Severity:** Low (not expected in POC)

### Issue 3: Print Layout on Firefox
**Description:** Print styles may differ slightly in Firefox
**Workaround:** Use Chrome for optimal print output
**Severity:** Low

---

## Test Results Summary

| Module | Total Tests | Passed | Failed | Pending |
|--------|-------------|--------|--------|---------|
| Demand Heatmap | 6 | - | - | - |
| Dispatch Planner | 6 | - | - | - |
| Expiration Alerts | 6 | - | - | - |
| Integration | 2 | - | - | - |
| Performance | 3 | - | - | - |
| Cross-Browser | 3 | - | - | - |
| Mobile | 2 | - | - | - |
| Accessibility | 3 | - | - | - |
| **Total** | **31** | **-** | **-** | **-** |

---

## Test Execution Instructions

### Prerequisites
1. Backend server running on http://localhost:8000
2. Database seeded with test data
3. Frontend dev server running on http://localhost:5173

### Running Tests
1. Start backend: `cd backend && python -m uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Execute test scenarios manually following steps above
4. Document results in summary table
5. Report any failures with screenshots and console logs

### Automated Testing (Future Enhancement)
- Consider adding Playwright or Cypress for E2E tests
- Jest for unit tests on React components
- pytest for backend API tests

---

## Sign-Off

**Tester:** _________________________  
**Date:** _________________________  
**Status:** ☐ All Tests Pass  ☐ Issues Found (see above)  
**Approved for Demo:** ☐ Yes  ☐ No (reason: _____________)
