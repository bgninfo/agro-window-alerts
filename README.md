# agro-window-alerts

Proactive **planting-window and weather alerts** for Brazilian soybean and corn growers, built on Embrapa's [AgroAPI](https://www.embrapa.br/agroapi).

Official planting windows (the Zarc, Brazil's agricultural climate-risk zoning) exist as data, but a grower has to go and look them up. This project flips that: you describe a crop and a municipality once, and it tells you when a window is about to open, is open, or is about to close, and warns about heavy rain or a dry spell in the next days.

> **Status: early development (v0.1).** The alert engine, configuration, deduplication, WhatsApp delivery and a runnable demo are done and tested. **Fetching live data from Embrapa is not implemented yet** (see [What is not done yet](#what-is-not-done-yet)).

## What works today

- **Planting-window logic** on ten-day periods (*decêndios*), including windows that cross New Year.
- **Alert rules**: window opening soon, window open, window closing soon, heavy-rain forecast, and dry spell while a window is open. Thresholds are configurable.
- **No duplicate alerts**: each occurrence is sent once, tracked in a small local file.
- **Delivery** through the official WhatsApp Business Cloud API, or to the terminal.
- **Demo mode** with made-up data, so you can try everything without any account.
- **AWS Lambda** entry point to run it on a daily schedule.
- 44 automated tests, standard library only (no runtime dependencies).

## Quick start

Requires Python 3.11 or newer.

```bash
git clone https://github.com/bgninfo/agro-window-alerts.git
cd agro-window-alerts
pip install -e ".[dev]"

cp examples/config.example.toml config.toml
agro-alerts check --config config.toml --demo --today 2026-10-12
```

Expected output (messages are in Brazilian Portuguese, since that is the audience):

```
[to console] Janela de plantio ABERTA para Example farm, Sorriso/MT (soybean): de 01/10/2026 a 30/11/2026 (risco de perda de 20%).
[to console] Previsão de chuva forte em Example farm, Sorriso/MT (soybean) no dia 15/10/2026: 55 mm.
...
4 new alert(s) on 2026-10-12.
```

Run the tests with `pytest`.

## Configuration

Copy `examples/config.example.toml` to `config.toml` (git-ignored). Each `[[watch]]` is one crop in one municipality:

| Setting | Meaning |
| --- | --- |
| `risk_level` | Follow the 20%, 30% or 40% production-loss-risk window |
| `lead_days` | Days of notice before a window opens or closes |
| `forecast_days` | How many days ahead to check the weather |
| `dry_spell_mm` / `heavy_rain_mm` | Rain thresholds for the weather alerts |
| `notifier` | `console` or `whatsapp` |

The default thresholds are conservative examples, **not agronomic advice**. Tune them with a qualified agronomist.

Secrets (API tokens, phone-number ids) go in environment variables, never in the repository. See `.env.example`.

## What is not done yet

Embrapa's public documentation does not publish the Agritec endpoint or the JSON returned by Agritec and ClimAPI, so the live adapters in `sources/embrapa.py` are stubs that raise a clear error. To finish them you need your own AgroAPI token:

1. Create an account and an application in the [AgroAPI store](https://www.agroapi.cnptia.embrapa.br/store/) and subscribe to Agritec and ClimAPI.
2. Put the token and base URLs in `.env`.
3. Use `agro-alerts probe <url>` to print the real JSON, then implement `planting_windows`, `forecast`, `parse_agritec_windows` and `parse_climapi_forecast`.

This is the main open task. See [docs/ISSUES.md](docs/ISSUES.md) for the list of planned issues.

## WhatsApp delivery

Messages that a business starts must use a template approved by Meta. Create a template with a single `{{1}}` body variable, then set `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` and `WHATSAPP_TEMPLATE_NAME`, and `notifier = "whatsapp"` in the config. List recipients per watch. WhatsApp usage is billed by Meta.

## Running on AWS

`agro_window_alerts.lambda_handler.handler` is a Lambda entry point. Package the code with your `config.toml`, set the environment variables, and trigger it daily with an Amazon EventBridge schedule. The "already sent" file lives in `/tmp`, which Lambda does not keep between cold starts; moving it to S3 or DynamoDB is a planned improvement.

## Costs and terms of data

- AgroAPI plans change over time. At the time of writing, Embrapa's public datasheets list a small free tier (1,000 requests for one month) and paid plans for both Agritec and ClimAPI. Check the store for current prices before planning production use.
- ClimAPI data comes from NOAA's Global Forecast System. Its terms ask you not to claim ownership of NOAA/NWS information, not to imply NOAA endorsement, and not to present modified content as official government material. This project is **not affiliated with or endorsed by Embrapa or NOAA**.

## Privacy

The repository contains no personal data. Recipient phone numbers live only in your local, git-ignored `config.toml`. If you run this as a service for other people, you are responsible for complying with Brazil's LGPD.

## Contributing

Issues and pull requests are welcome, especially for the live adapters, more crops, and agronomic review of the default rules.

## Disclaimer

This tool provides informational alerts only. It does not replace professional agronomic advice, and the authors accept no liability for decisions made from its output.

## License

[MIT](LICENSE)
