# open-food-data-pipeline
A simple ETL pipeline that ingests an Open Food Data CSV into BigQuery. Uses Python, Docker, and GCP.

### Change log:

25/11/2026 - Added check_url_response function.

04/10/2026 - Added a fix that forced non-float values in float columns to convert to NaN/null. All records now upload to GBQ.

19/09/2026 - Updated Dockerfile for the app to run inside a container.

14/09/2026 - Majority of records uploaded to GBQ.

13/09/2026 - Added Conversion Error exception to let upload into Google BigQuery.

12/09/2026 - Initial creation.