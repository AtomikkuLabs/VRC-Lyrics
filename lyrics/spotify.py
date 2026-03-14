import asyncio
import logging
import requests
from pyppeteer import launch

class SpotifyAuthError(Exception):
    """Raised when we fail to fetch or parse a Spotify access token."""
    pass

class Spotify:
    def __init__(self, sp_dc, handlers):
        self.sp_dc = sp_dc
        self.handlers = handlers
        self.bearer_token = None
        asyncio.run(self._get_bearer_token())

    async def _get_bearer_token(self):
        logging.info("Launching browser to fetch bearer token...")
        self.handlers.info("Fetching bearer token...")
        browser = await launch(
            headless=True,
            executablePath=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            args=['--no-first-run',  '--no-default-browser-check'],
            handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False
        )

        page = await browser.newPage()

        await page.setCookie({
            'name': 'sp_dc',
            'value': self.sp_dc,
            'domain': '.spotify.com',
            'path': '/',
            'httpOnly': True,
            'secure': True
        })

        token_future = asyncio.get_event_loop().create_future()

        def _on_request(request):
            auth = request.headers.get('authorization', '')
            if auth.startswith('Bearer ') and not token_future.done():
                token_future.set_result(auth)

        page.on('request', _on_request)

        await page.goto('https://open.spotify.com/', waitUntil='networkidle2')

        try:
            bearer = await asyncio.wait_for(token_future, timeout=10)
        except asyncio.TimeoutError:
            await browser.close()
            raise SpotifyAuthError("Timed out waiting for Spotify bearer token")

        await browser.close()
        logging.info("Bearer token acquired, browser closed.")
        self.handlers.info("Bearer token acquired")
        self.handlers.dismiss()
        self.bearer_token = bearer
        response = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": self.bearer_token})

        if response.status_code == 401:
            raise SpotifyAuthError(f"Invalid sp_dc cookie")

    def get_lyrics(self, track_id, _retry=False):
        headers = {
            "Authorization": self.bearer_token,
            "User-Agent": "Mozilla/5.0",
            "App-Platform": "WebPlayer"
        }
        params = {"format": "json", "market": "from_token"}
        url = f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            if _retry:
                raise SpotifyAuthError("Token refresh failed, still getting 401")
            asyncio.run(self._get_bearer_token())
            return self.get_lyrics(track_id, _retry=True)
        elif response.status_code == 404:
            return None
        else:
            raise SpotifyAuthError(f"Unexpected status {response.status_code}: {response.text}")


class SpotifyLyrics:
    def __init__(self, sp_dc, handlers):
        self.Spotify = Spotify(sp_dc, handlers=handlers)

    def get_lyrics(self, playback):
        lyrics_data = self.Spotify.get_lyrics(playback.id)

        if not lyrics_data:
            return False

        lines = lyrics_data['lyrics']['lines']
        return {int(line['startTimeMs']): line['words'] for line in lines}
