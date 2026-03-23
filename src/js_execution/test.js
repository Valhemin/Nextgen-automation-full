const dataProfile = [
  {
    id: 'e3d84964-1ad8-4224-8d8e-85ecaa9cb19a',
    name: 'Tele 022',
    raw_proxy: None,
    profile_path: 'jbgIXRuVYT-14082024',
    browser_type: 'Chrome',
    browser_version: '124.0.6367.29',
    note: None,
    group_id: 2,
    created_at: '2024-08-14T14:59:12',
  },
  {
    id: '64efb1f8-2ec7-4dc6-9d64-f5f9db84ffc7',
    name: 'Tele 311',
    raw_proxy: '',
    profile_path: 'bcabYjdDyO-15082024',
    browser_type: 'Chrome',
    browser_version: '124.0.6367.29',
    note: None,
    group_id: 2,
    created_at: '2024-08-15T07:31:07',
  },
  {
    id: '36a06e51-1c2d-4c5b-8cb4-91f19434ca79',
    name: 'Tele 389',
    raw_proxy: '',
    profile_path: '2EUOyeIVnH-15082024',
    browser_type: 'Chrome',
    browser_version: '124.0.6367.29',
    note: None,
    group_id: 2,
    created_at: '2024-08-15T07:31:07',
  },
  {
    id: '61efb23e-19c9-4f1c-b553-1264dc7a8043',
    name: 'Tele 504',
    raw_proxy: '',
    profile_path: 'VmqJbvbTEy-15082024',
    browser_type: 'Chrome',
    browser_version: '124.0.6367.29',
    note: None,
    group_id: 2,
    created_at: '2024-08-15T07:31:07',
  },
  {
    id: 'e64af7b2-2a32-4cf6-9e13-5b03218d88f5',
    name: 'Tele 557',
    raw_proxy: '',
    profile_path: 'Qp38fk7AJy-15082024',
    browser_type: 'Chrome',
    browser_version: '124.0.6367.29',
    note: None,
    group_id: 2,
    created_at: '2024-08-15T07:31:07',
  },
];

const group = [
  {
    id: 1,
    name: 'All',
    sort: 1,
    created_by: -1,
    created_at: '2024-09-01T16:53:11.8977181+07:00',
    updated_at: '2024-09-01T16:53:11.8977181+07:00',
  },
  {
    id: 2,
    name: 'Tele',
    sort: 2,
    created_by: 0,
    created_at: '2024-08-14T15:01:26',
    updated_at: '2024-08-15T09:15:15',
  },
];

https://t.me/Tomarket_ai_bot/app?startapp=00002jTB
https://t.me/blum/app?startapp=ref_LHzHt1atQz
https://t.me/MatchQuestBot/start?startapp=13355ed93cf9f7b657440d19f66949fb
https://t.me/TimeFarmCryptoBot?start=qFUvABmfdvjXjwuE
https://t.me/cexio_tap_bot?start=1718627624760836
https://t.me/OfficialBananaBot/banana?startapp=referral=46SVN86
https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_92118134
https://t.me/catsgang_bot/join?startapp=UoTY0KAZLFM3Mzi24z6ua
https://t.me/major/start?startapp=6736048324
https://t.me/memefi_coin_bot/main?startapp=r_bffb6cd3ac
https://t.me/pokequest_bot/app?startapp=mekb6seXSv
https://t.me/tontap_app_bot?start=dcebb556
https://t.me/fintopio/wallet?startapp=reflink-reflink_KSR9sEeQgRwhOTpC-
https://t.me/seed_coin_bot/app?startapp=6736048324
https://t.me/Agent301Bot/app?startapp=onetime6736048324
https://t.me/cryptorank_app_bot/points?startapp=ref_6736048324_

 const iframe = document.querySelector("iframe");
 if (iframe) {
   const url = new URL(iframe.src);
   const params = new URLSearchParams(url.hash.substring(1)); // Get parameters from hash
   const tgWebAppData = params.get("tgWebAppData");
   if (tgWebAppData) {
     console.log(tgWebAppData);
   } else {
     console.log("tgWebAppData not found.");
     console.log("");
   }
 } else {
   console.log("Iframe not found.");
   console.log("");
 }