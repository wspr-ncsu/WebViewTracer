pii_regexes = [
    ( "[0-9]+\\.com\\.android\\.vending", "Play store package version"),
    ("dcfc4516-e5d8-48b0-a2bf-e9ae4906594b|ZGNmYzQ1MTYtZTVkOC00OGIwLWEyYmYtZTlhZTQ5MDY1OTRi|ec977e0e35d3ad049822e21b2a863e4be355561430314d555f1221a44396df07" 
     + "|f6297254-70a4-4ee7-814a-3d18afc9f32d|ZjYyOTcyNTQtNzBhNC00ZWU3LTgxNGEtM2QxOGFmYzlmMzJk|a22ae4a8f1578c012c9337591e9481eaaa591d1319ea217f372f6415205fd348" 
     + "|fc8fd85e-5baf-49d3-990b-7d5b223651f3|ZmM4ZmQ4NWUtNWJhZi00OWQzLTk5MGItN2Q1YjIyMzY1MWYz|027c12fa7eea6eade91d35bb858c0450a5d4bde6d25edc02f319d871b7512e1d" 
     + "|0657c8d0-bf92-4d62-ab5c-1dcbc3c3549c|MDY1N2M4ZDAtYmY5Mi00ZDYyLWFiNWMtMWRjYmMzYzM1NDlj|7cbf21e01226aca6b57f104a72367c0c4528f4bd54939b25c4299f9902dff146", "Advertising ID"),
    ("abfarm-release-rbe-64-2004-0093|YWJmYXJtLXJlbGVhc2UtcmJlLTY0LTIwMDQtMDA5Mw|4451a071126e0f0928f52e0c83ac43a668b19ca08c9f00045868a6980f7d7926", "Kernel build version"),
    ("b5-0.5-9825706|YjUtMC41LTk4MjU3MDY|9b16fe4332fd89b46ef57bff04f7496bc704461e221b9af1c6b142678804d3a2","Bootloader version"),
    ("Pixel 4a|pixel4a|UGl4ZWwgNGE|cGl4ZWw0YQ|6e16ca4e4cd0c660a56e991c62151392ff5f79254f526290dc448a99471c1b2f","Device model"),
    ("bramble|YnJhbWJsZQ|8f564af39fab12a40644275ed6ac20d772908228e9c667ad420dee1a54264b47","Device code name"),
    ("TQ3A\\.230901\\.001|VFEzQS4yMzA5MDEuMDAx|b74ef2dbb937a4507932dff897f9759fde769df401d1ba509f531ffa6cc07df6"," Build ID"),
    ("[bB]attery|YmF0dGVyeQ|QmF0dGVyeQ","Battery level"),
    ("[pP]artition|cGFydGl0aW9u|UGFydGl0aW9u","Partition space"),
    ("[mM]emory|bWVtb3J5Cg|TWVtb3J5","Memory space"),
    ("192\\.58\\.122\\.|100\\.84\\.104\\.89|100\\.108\\.84\\.3|100\\.115\\.113\\.14|100\\.126\\.4\\.61","Internal IP-related info"),
    ("latitude|longitude|lat=|lon=","Location"),
    ("North\\+Carolina\\+State\\+University|North%20Carolina%20State%20University|Tm9ydGggQ2Fyb2xpbmEgU3RhdGUgVW5pdmVyc2l0eQ","Network Provider"),
    ("[rR]aleigh|UmFsZWlnaA","City"),
    ("Sodium Chromium|Sodium%20Chromium|SodiumChloride|chloride|U29kaXVt|c29kaXVt","Name"),
    ("afma-sdk-a-v|YWZtYS1zZGstYS12", "AdMob SDK version"),
    ("27606|27607|Mjc2MDY|Mjc2MDc","Zip code")
]