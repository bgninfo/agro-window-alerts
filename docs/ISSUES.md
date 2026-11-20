# Planned issues

Copy each block into a GitHub issue. They are written to be small, testable tasks.

## 1. Implement Agritec planting-window fetching and parsing
Replace the stub in `sources/embrapa.py`. Use `agro-alerts probe` with a real token to capture the Agritec response, add a redacted copy under `tests/fixtures/`, implement `planting_windows` and `parse_agritec_windows`, and cover them with tests that use that fixture.
**Done when:** `agro-alerts check` returns real windows for a configured municipality and crop.

## 2. Implement ClimAPI forecast fetching and parsing
Call `/ncep-gfs/{variable}/{date}/{longitude}/{latitude}` for precipitation and temperature, confirm the date format and variable names with a real token, aggregate the 6-hour values into `ForecastDay` objects, and add fixture-based tests.
**Done when:** the engine receives a real 5-day forecast.

## 3. Keep the "already sent" state in S3 or DynamoDB
Lambda's `/tmp` is not persistent. Add a `SentStore` backend for AWS and select it by configuration.

## 4. Add a Lambda deployment guide (and optionally infrastructure as code)
Document packaging, environment variables and an EventBridge schedule. A small Terraform or AWS SAM template is a welcome addition.

## 5. Per-crop rule profiles
Different crops need different dry-spell and heavy-rain thresholds. Add named profiles for soybean and corn (first and second crop) with sources for the values, ideally reviewed by an agronomist.

## 6. Cache API responses
Free and entry-level AgroAPI plans have small request limits. Cache Agritec results (they change rarely) and forecasts (they update every six hours).

## 7. Send a periodic summary instead of single alerts
Optional weekly digest per watch.

## 8. English and Spanish message templates
Messages are currently in Brazilian Portuguese only.
