# Social Feed Mobile (Expo)

This is a minimal Expo React Native app that implements a Feed screen consuming the Laravel backend at `/api/feed` and `/api/search`.

Quick setup

1. Install Expo CLI (if not installed):

```bash
npm install -g expo-cli
```

2. From this folder:

```bash
cd mobile_app
npm install
npm start
```

3. In `src/screens/FeedScreen.js` set `BASE_URL` to your backend URL. If running the Android emulator, you may need to set `http://10.0.2.2:8000` or your machine LAN IP like `http://192.168.1.100:8000`.

What it implements

- Single screen: `FeedScreen` with search bar
- Fetches `GET /api/feed` (paginated with `?page=` param if supported) and displays posts in a `FlatList`
- Infinite scroll: loads next page on end reached
- Inline search: calls `GET /api/search?q=` and shows results inline
- Each post shows avatar placeholder, username, text, time, and a reaction button which calls `POST /api/interactions`
- Handles loading, empty and error states

Note
- Adjust the `BASE_URL` in `src/screens/FeedScreen.js` to match your environment.
