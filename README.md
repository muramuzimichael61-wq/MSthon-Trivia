# Myk Quiz

Myk is an installable programming quiz web app with solo play and live host-led rooms. Hosts share a six-character code or invite link; players answer on their own devices, and see whether each answer passed. The host gets the live answer tally and leaderboard and chooses when to advance questions. Each hosted question has a 15-second timer. The server and question bank use only the Python standard library.

## Run it on your computer

You need Python 3.9 or later.

```powershell
python main.py
```

Open [http://localhost:8000](http://localhost:8000). This address works on the computer running the server; it is not yet a public website. The question bank is created in `data/questions.json` the first time the server runs. Changes made through the admin editor are saved there and remain after a restart.

## Host a quiz or join one

1. Open the app and choose **Host / Join**.
2. As host, pick a topic and round length, then create a room. Share the six-character code or copy the invite link for your players.
3. Players open the same app, choose **Host / Join → Join a quiz**, enter the room code and a display name, then wait in the lobby.
4. Start the quiz when everyone is ready. Players get 15 seconds per question. The host sees who answered correctly, who did not pass, and each player's score, then advances the round.

The host can add custom questions before creating a room: choose **Admin**, sign in, and use the **Question Studio** form. Newly saved questions are available when creating the next room. Question choices and the correct answer are managed by the server; players do not receive the answer key before they answer or the timer expires.

Rooms are temporary and held in the running server's memory; the question bank is saved on disk. A room expires after six hours without activity, and the host controls the question changes. If the server restarts, active rooms end and players need a new code.

For people on the **same Wi-Fi network**, start the app with:

```powershell
python main.py --host 0.0.0.0 --port 8000
```

Share the host computer's local network address, for example `http://192.168.1.20:8000`, with players on that network. The host may need to allow Python through the computer's firewall. `localhost` only works on the computer running the server.

## Use the admin editor

Set an admin password before starting the server. Without it, the admin login stays disabled.

```powershell
$env:MYK_ADMIN_PASSWORD = "choose-a-long-unique-password"
python main.py
```

Select **Admin** in the app to sign in and add questions. Each question has four choices, a topic, difficulty and an optional explanation. Questions are added to the shared bank and become available in later rounds. The session token expires after eight hours or when the server restarts.

## Publish on Render

`render.yaml` configures a Render web service with HTTPS, persistent storage for administrator-added questions, and a generated admin password. To publish:

1. Push this repository and branch to GitHub.
2. Sign in to [Render](https://render.com), choose **New → Blueprint**, and connect this GitHub repository.
3. Review the Blueprint resources and pricing before confirming. The included persistent disk and always-on Starter web service are paid Render resources; this setup does not use a free ephemeral filesystem because added questions need durable storage.
4. After the first deploy completes, open the service's `onrender.com` HTTPS address. Select **Admin** in Myk and use the value of `MYK_ADMIN_PASSWORD` from the service's Render environment settings. Change or rotate the generated secret in Render if needed, then redeploy.
5. Share the HTTPS address with players. Choose **Host / Join** to create a room and send them the displayed room code or invite link.

The app is publicly reachable at its Render URL once deployment succeeds. Being public does not guarantee it immediately appears in Google or another search engine: submit the deployed URL to the search engine's webmaster tools and allow time for crawling. A custom domain is optional; configure it in Render after deployment.

The Render configuration mounts its persistent disk at `/var/data`, which Myk uses for `questions.json`. Live game rooms are stored in server memory, so restarting the service ends active games; keep one running service instance to coordinate rooms. Do not scale this configuration to multiple instances without adding shared room storage.

For a **local Wi-Fi** game instead, start the app with `python main.py --host 0.0.0.0 --port 8000` and share the host computer's LAN address. Players must be on that network. The service worker caches the app interface; quiz, admin and room APIs require a live server connection.

## Install the app

Visit the deployed HTTPS address in a supported browser and use its **Install app** action or browser menu. On desktop Chrome/Edge, the app also offers an install button when the browser supports it. On iOS, use Safari's **Share → Add to Home Screen**.

## Project files

```text
main.py              Python HTTP server and quiz/admin API
web/index.html       Responsive quiz interface
web/styles.css       Interface styling
web/app.js           Quiz, timer, installation, and admin interactions
web/manifest.json    Progressive web app installation metadata
web/sw.js            Offline app-shell cache
data/questions.json  Persistent question bank, created on first run
render.yaml          Render web-service deployment and persistent disk
```

## Repository and source

[Myk Quiz on GitHub](https://github.com/muramuzimichael61-wq/MSthon-Trivia)
