# Navidrome_love_to_ListenBrainz
A Python script to synchronize your loved songs from your Navidrome database to your ListenBrainz.org profile.

## Description

The script connects to your Navidrome database and retrieves all tracks you’ve marked as “loved” within the specified date range (`START_DATE` to `END_DATE`). It loops through each track, extracting essential metadata such as the recording MBID, artist name, track title, and album. Tracks without a valid MusicBrainz Recording MBID are skipped to ensure that only recognized recordings are submitted to ListenBrainz.

For each valid track, the script sends a POST request to the ListenBrainz API with your user token, marking the track as “loved” on your ListenBrainz profile. To handle network issues or temporary API failures, the script includes a retry mechanism, attempting each request up to three times with a short delay between attempts. Progress and errors are logged to the console, and a summary is maintained for skipped or failed tracks, allowing users to review and troubleshoot any issues.

## How It Works

1. **Retrieve Loved Tracks**  
   The script queries your Navidrome database for tracks marked as “loved” within the specified `START_DATE` and `END_DATE`. Each track’s metadata—recording MBID, artist, title, and album—is extracted for submission.

2. **Validate Tracks**  
   Tracks without a valid MusicBrainz Recording MBID are skipped, ensuring that only recognized recordings are sent to ListenBrainz.

3. **Submit to ListenBrainz**  
   Each valid track is sent to the ListenBrainz API via a POST request with your user token. A retry mechanism attempts each request up to three times in case of temporary network or API failures, with a short delay between attempts.

4. **Logging and Summary**  
   Successful submissions are logged as “Loved,” while skipped or failed tracks are tracked in a summary for review. This provides transparency and allows troubleshooting of any issues.

## Configure the following variables

| Name                 | Description                                                                                                     | Suggested Value                     |
|----------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------|
| `DB_PATH`            | Path to your Navidrome database file                                                                            | `/path/to/navidrome.db`            |
| `LISTENBRAINZ_TOKEN` | Your ListenBrainz API token (see [ListenBrainz API docs](https://listenbrainz.readthedocs.io/en/latest/users/api/index.html)) | `YOUR_TOKEN_HERE`                  |
| `START_DATE`         | Starting date limit to avoid uploading all likes every time. Can be the date of the latest execution           | `"2025-01-01"`                     |
| `END_DATE`           | Ending date limit. Can be the date of the current execution                                                    | `"2026-01-15"`                     |

## Execute the script

```bash
python3 love_tracks_listenbrainz.py
