<p align="center">
   <img src="https://github.com/user-attachments/assets/91024f40-60e3-4a60-80e5-3b2ec1b4d0e4" alt="Banner" />
</p>

<p align="center">
   <a href="https://github.com/BigAtomikku/VRC-Lyrics/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
   <a href="https://github.com/BigAtomikku/VRC-Lyrics/releases/latest"><img src="https://img.shields.io/github/downloads/BigAtomikku/VRC-Lyrics/total?style=for-the-badge&logo=github" alt="Repo Downloads"></a>
   <a href="https://github.com/BigAtomikku/VRC-Lyrics/releases/latest"><img src="https://img.shields.io/github/v/release/BigAtomikku/VRC-Lyrics?style=for-the-badge&label=Latest&logo=github" alt="Latest Release"></a>
   <a href="https://www.virustotal.com/gui/file/f17a53eea0a69b5295043fc10f80221108a1dce9469f7bc7adc7f700a60e22a8?nocache=1"><img src="https://custom-icon-badges.herokuapp.com/badge/-Scan%20at%20VirusTotal-blue?style=for-the-badge&logo=virustotal&logoColor=white" alt="Virus Total Scan"></a>
   <a href="https://ko-fi.com/bigatomikku"><img alt="Ko-Fi" src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-fi"></a>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/6d673fc7-d85e-49de-997d-b101650360c7" width="45%" alt="Home Screen" />
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/e9ab95e4-802b-4b92-8e05-bebef4443307" width="37%" alt="Settings Screen" />
</p>

# VRC Lyrics

**Display your currently playing song and synchronized lyrics in the VRChat chatbox.**  
Integrates with TTS Voice Wizard! (requires pre-release v1.6.8.5+).

<p align="center">
   <img src="https://github.com/user-attachments/assets/ee597119-ca1c-4f62-9e4f-fb4bfba87b94" width="33%" alt="Chatbox Example" />
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/2cbb0a0b-2ff3-4ca1-8b1b-5bae44540fef" width="26%" alt="TTSVoiceWizard Example" />
</p>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [OSC](#osc)
  - [Playback Providers](#playback-providers)
  - [Lyric Providers](#lyric-providers)
- [Usage](#usage)
- [Known Issues](#known-issues)
- [License](#license)

## Features

- 🎵 Shows current Spotify or Windows‐detected track
- 📝 Synchronized lyrics display in VRChat Chatbox
- 🔊 TTS Voice Wizard integration (pre-release v1.6.8.5+)
- 🔌 Supports multiple lyric backends (Spotify, LRCLib)

## Installation

1. **Download** the [latest release](https://github.com/BigAtomikku/VRC-Lyrics/releases/latest).
2. **Extract** and **run** `VRC Lyrics.exe`.
3. **Open** the Settings window (⚙️ icon) to begin configuring.
4. **Close** the Settings window (⚙️ icon again) to refresh the app with your changes.

## Configuration

### OSC
#### IP Address:
- Default: `127.0.0.1`
#### Port:
- `9000` → VRChat Chatbox (default)  
- `4026` → TTS Voice Wizard
  - Requires [TTS Voice Wizard v1.6.8.5](https://github.com/VRCWizard/TTS-Voice-Wizard/releases/v1.6.8.5) or later
  - See [setup instructions](https://ttsvoicewizard.com/docs/MediaIntegration/VRCLyrics)
#### Chatbox Output Format (Port `9000` only)
 - Sends formatted output to the VRChat chatbox.
 - You can customize the output using the following placeholders:
   - `{status}` - Current playback icon (▶️ for playing, ⏸️ for paused)
   - `{name}` - Track name
   - `{artist}` - Main artist (may add `{artists}` in the future if requested)
   - `{mic}` - Microphone emoji for added flair (only shows when lyrics are displayed)
   - `{lyrics}` - Current line of lyrics
 - All text is available and inserted according to your selected output format.
 - Default: `{status} {name} - {artist}\n{mic} {lyrics}`

### Playback Providers
#### Windows
   - Uses the Windows Media Session API to detect any playing audio.
   - Limitations:
     - Only syncs from the beginning of a changed track.
     - Scrubbing is not supported.
#### Spotify
   - Connects via Spotify Web API.
   - **Requires** a Spotify Developer Application:
     1. Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
     2. Create a new app
     3. Add `http://127.0.0.1:5000/callback` as a **Redirect URI**
     4. Copy the **Client ID** into the corresponding field
     5. Once the program starts (by clicking the **⚙️ icon** again to exit settings), approve Spotify request in browser

### Lyric Providers
#### Spotify
  - Fetches lyrics directly from Spotify’s internal endpoint.
  - Only compatible with Spotify playback.
  - **Requires** your `sp_dc` cookie (see [Syrics Wiki](https://github.com/akashrchandran/syrics/wiki/Finding-sp_dc)).
  - **Requires** Microsoft edge to be downloaded and located at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`.
     - Most windows computers will already have this installed by default.
     - I may also add Chromium as a secondary option if there are those who do not wish to have Microsoft Edge installed.
  - **It will take a few seconds** once starting the program to get spotify lyrics initially. Be patient.
#### LRCLib
  - Uses the LRCLib open database for lyrics.

## Usage

1. Make sure VRChat (or TTS Voice Wizard) is running.
2. Launch `VRC Lyrics.exe`.
3. If needed, update settings by clicking the **⚙️ icon**, then click it again to refresh the app.
4. Lyrics will automatically display in your VRChat chatbox while music plays.

## Known Issues

- **Fast‐paced lyrics** may time out the VRChat chatbox.
  - Check for time-out by opening the VRChat launchpad.

## License

This project is licensed under the [MIT License](LICENSE).
> **Note:** Versions prior to **2.0.0** included GPLv3-licensed code; all dependencies are MIT as of **v2.0.0**.
