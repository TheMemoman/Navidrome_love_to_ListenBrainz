import sqlite3
import requests
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
DB_PATH = "navidrome.db"            # Path to your Navidrome database file
LISTENBRAINZ_TOKEN = "xxxxxxxxxxxxxxx"             # <-- Put your ListenBrainz token here
# Limit dates for starred_at (both inclusive)
START_DATE = "2006-01-01"
END_DATE = "2026-01-15"

FEEDBACK_URL = "https://api.listenbrainz.org/1/feedback/recording-feedback"
REQUEST_DELAY = 0.25                  # Seconds between API calls
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds between retries

# --------------------------------------------------
# QUERY STARRED TRACKS FROM NAVIDROME
# --------------------------------------------------
def query_loved_tracks(db_path, start_date, end_date):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT
        mf.mbz_recording_id,
        mf.artist,
        mf.title,
        mf.album,
        a.starred_at
    FROM media_file mf
    JOIN annotation a ON a.item_id = mf.id
    WHERE a.starred = TRUE
      AND (
            (a.starred_at IS NOT NULL AND a.starred_at BETWEEN ? AND ?)
            OR a.starred_at IS NULL
          )
    ORDER BY mf.artist, mf.title
    """

    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --------------------------------------------------
# SUBMIT LOVED FEEDBACK TO LISTENBRAINZ
# --------------------------------------------------
def submit_loved_tracks(rows, token):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    loved = 0
    skipped = 0
    failed = 0
    skippedSongs = ""
    failedSongs = ""

    for recording_mbid, artist, title, album, starred_at in rows:

        # Skip tracks without valid MusicBrainz Recording MBID
        if not recording_mbid or not recording_mbid.strip():
            skipped += 1
            skippedSongs += f"⏭ Skipped: {skipped} - {artist} – {title} – {album}\n"
            print(f"⏭ Skipped (no MBID): {artist} – {title} – {album}")
            continue

        payload = {
            "recording_mbid": recording_mbid,
            "score": 1  # ❤️ Loved
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    FEEDBACK_URL,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    loved += 1
                    print(f"❤️ Loved: {artist} – {title}")
                    break  # success, exit retry loop
                else:
                    failed += 1
                    failedSongs += (
                        f"❌ Failed: {failed} - {artist} – {title} – {album} | "
                        f"Status: {response.status_code}, Response: {response.text}\n"
                    )
                    print(f"❌ Failed: {artist} – {title} | Status: {response.status_code}")
                    break  # don't retry for HTTP errors, only for exceptions

            except Exception as e:
                if attempt < MAX_RETRIES:
                    print(f"⚠️ Attempt {attempt} failed for {artist} – {title} – {album}, retrying in {RETRY_DELAY}s... | {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    failed += 1
                    print(f"❌ Error: {artist} – {title} | {e}")
                    failedSongs += f"❌ Error: {failed} - {artist} – {title} – {album} | {e}\n"

        time.sleep(REQUEST_DELAY)

    print("\n---------------- SUMMARY ----------------")
    print(f"❤️ Loved submitted : {loved}")
    print(f"⏭ Skipped (no MBID): {skipped}")
    print(f"❌ Failed          : {failed}")
    if skipped > 0:
        print(f"\n⏭ Skipped (no MBID): \n{skippedSongs}")
    if failed > 0:
        print(f"❌ Failed          : \n{failedSongs}")

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    rows = query_loved_tracks(DB_PATH, START_DATE, END_DATE)
    print(f"Found {len(rows)} starred tracks in Navidrome.")

    if not rows:
        print("No tracks to submit. Exiting.")
        return

    submit_loved_tracks(rows, LISTENBRAINZ_TOKEN)

if __name__ == "__main__":
    main()
