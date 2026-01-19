# Call History Excel Upload Feature

## Overview
This feature allows you to upload Excel files containing call history data and automatically match phone numbers with existing CRM leads. All matched call data is then stored against the corresponding leads in your CRM system.

## How to Access
1. Navigate to **Calling** → **Call History Upload** in the sidebar
2. Or go directly to `/call-history/upload/`

## Excel File Requirements

### Required Column
- **Phone Number** - The phone number column (must be named exactly "Phone Number")

### Optional Columns (will be stored if present)
- ID, Type, Agent, Version, Call Date, Call Time
- Disposition, Call Duration, Call Recording, Try Count
- Call Transcript, Hangup Reason, Cost, source
- campaign_type, conversion_status, disposition_reason
- x_model_used, Client_name, BOT_name, bot_name
- client_area, client_name, scheduled_time, visit_day
- visit_time, followup_day, Agent_name, name, city
- budget, form_name, lead_id, Client Name, Area_Name
- Day, project_name, time, Time, project, lead_source
- XYZ_Project, email, first_name, last_name, phone
- Bot_Name, x-callback-time, company_name, customer_name
- event_name, referrer_name, variable_name, interested_or_not
- And any other columns in your Excel file

## Phone Number Matching Logic

The system uses exact 10-digit matching:

### Exact 10-Digit Match Only
- Compares the last 10 digits of phone numbers
- Must match exactly - no partial matching
- Handles Excel float format (e.g., 9876543210.0)
- Works with different formats: +91-9876-543-210 matches 9876543210

### Examples
- `+91 9876543210` matches `9876543210` → **Match Found**
- `9876543210.0` matches `9876543210` → **Match Found** (Excel float format)
- `9876543210` vs `1234563210` → **No Match** (different numbers)
- `1234567890` vs `9876543210` → **No Match**

## Upload Process

1. **Upload Excel File**
   - Select your Excel file (.xlsx or .xls)
   - Click "Upload & Process"

2. **Review Results**
   - View matched and unmatched records
   - See match confidence scores
   - Review all Excel data that will be stored

3. **Save to CRM**
   - Click "Save All Matches" to store data
   - All matched records are saved to your CRM
   - View saved data in the Call History Dashboard

## Features

### Match Statistics
- Total records processed
- Number of matches found
- Number of unmatched records
- Overall match percentage

### Data Storage
- All Excel columns are preserved
- Call recordings and transcripts are linked
- Agent information is stored
- Disposition and call outcomes tracked

### Dashboard
- View all previous uploads
- Track upload history and statistics
- Drill down into specific upload details
- Search and filter call records

## Navigation

- **Upload New File**: `/call-history/upload/`
- **View Dashboard**: `/call-history/dashboard/`
- **View Upload Details**: `/call-history/{upload_id}/`

## Technical Details

### Dependencies Added
- `pandas==2.1.4` - For Excel file processing
- `openpyxl==3.1.2` - For .xlsx file support

### Database Models
- Uses existing `CallReportUpload` and `CallReportRecord` models
- Stores raw Excel data in JSON format
- Links to existing Lead records when matches found

### Phone Number Normalization
- Removes all non-digit characters
- Handles international formats (+91, etc.)
- Works with dashes, spaces, parentheses

## Usage Tips

1. **Prepare Your Excel File**
   - Ensure "Phone Number" column exists
   - Clean up phone number formats if needed
   - Include all relevant call data columns

2. **Review Before Saving**
   - Check match accuracy in the results page
   - Verify unmatched records
   - Ensure data looks correct

3. **Monitor Performance**
   - Use the dashboard to track uploads
   - Review match rates over time
   - Identify data quality issues

## Troubleshooting

### Common Issues
- **No matches found**: Check phone number format in Excel
- **Upload fails**: Ensure Excel file has "Phone Number" column
- **Encoding errors**: Save Excel file in UTF-8 format

### Support
- Check the upload dashboard for error messages
- Review the match results before saving
- Contact admin if persistent issues occur