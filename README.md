# Web Screenshooter API 
Flask-based API-REST solution for performing screenshoots of webpages remotely, within an API-REST. 

# Requirements
Requires a debian-based system with Python3.4, Flask and Selenium.

# Example usage

### start the server
From the root folder of the project, start the API-REST solution
```bash
python3 -m main.bin.entry
```

### capture a webpage screen
All the API-REST calls are wrapped within a single CLI located at `/cli` floder, which simplifies its usage.
Once started, invoke as many screenshots requests as required:

```bash
cd cli/
bash webscreenshot capture https://www.google.com -o google-screenshot.png
```
## Massive capture of screens from webpages: batching

If a batch of URLs are required, Web-Screenshooter supports it. First create a JSON file with a content that looks like:

```json
{
    'urls': [
         "https://www.google.com/",
         "https://www.facebook.com/"
    ]
}
```

Now pass it to the CLI script as follows:
```bash
cd cli/
bash webscreenshot batch urls.json -o capture.zip
```

It will download the web screenshots captures zipped from the backend.

# Characteristics

 * It is multithreaded, supporting a configurable set of workers for performing the screenshots. Take a look at the file `main/etc/config.json` for configuring those parameters.
 * Accepts a batch of URLs in an asynchronous way. Once requested, the CLI only polls the backend for its state and finally downloads the results zipped.
