# Cash Operations Dashboard

A comprehensive Flask-based dashboard for cash operations teams to monitor payment processing, automation efficiency, exceptions, and remittance insights.

## Features

### 1. Daily / Weekly Overview
- Total payments received with value
- Percentage processed automatically
- Unassigned / manual workload
- Total value assigned
- Average time to assign (automation vs manual)
- Toggle for Today / Week / Month / Quarter
- Line chart showing automation % over time with trendline

### 2. Automation Efficiency & Impact
- Automation success rate with trend
- Manual interventions saved
- Estimated time and cost saved
- Breakdown by rule (bank account, reference, name match)
- Reprocessing success metrics
- Pie chart for match type distribution
- Bar chart for cost/time saved

### 3. Exceptions / Attention Points
- Top 5 customers with recurring payment exceptions
- High-value unassigned payments
- Delays in SAP posting or remittance ingestion
- Stacked bar chart showing errors by reason

### 4. Remittance Insights
- Total remittances received
- Percentage successfully parsed vs manual review
- Average processing time
- Top 5 customers by remittance volume
- Donut chart showing processing status
- Bar chart by customer volume

### 5. Month-End Summary (CFO Snapshot)
- Total payments processed (value + count)
- Automation rate vs previous month
- Average assignment delay
- Total time saved (in FTE and €)
- Top-performing rules
- Comparative metrics with previous month

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/overview?period=today|week|month|quarter` - Overview metrics
- `GET /api/automation-trend?period=today|week|month|quarter` - Automation trend data
- `GET /api/automation-efficiency` - Automation efficiency metrics
- `GET /api/exceptions` - Exceptions and attention points
- `GET /api/remittance-insights` - Remittance processing insights
- `GET /api/month-end-summary` - Month-end CFO snapshot

## Technology Stack

- **Backend**: Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js 4.4.0
- **Styling**: Custom CSS with gradients and animations

## Features

- Responsive design for desktop, tablet, and mobile
- Auto-refresh every 5 minutes
- Period selector (Today, Week, Month, Quarter)
- Real-time data updates
- Interactive charts and visualizations
- Print-friendly layout

## Data

Currently uses mock data generation for demonstration purposes. In production, replace the data generation functions in `app.py` with actual database queries or API calls to your cash operations system.

## Customization

### Updating Colors
Edit `static/css/style.css` and modify the CSS variables in `:root`:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
}
```

### Adding New Metrics
1. Add new route in `app.py`
2. Create data generation function
3. Add HTML elements in `templates/dashboard.html`
4. Add JavaScript fetch and display logic in `static/js/dashboard.js`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Internal use only - Cash Operations Team
