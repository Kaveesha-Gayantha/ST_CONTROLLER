[app]

title = Edge Light Focus
package.name = edgelightfocus
package.domain = org.focus
source.dir = .
source.exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,pyjnius

orientation = portrait

fullscreen = 0

android.permissions = PACKAGE_USAGE_STATS,SYSTEM_ALERT_WINDOW

android.api = 31
android.minapi = 21

# මෙතැන SDK එක API එකට සමානව 31 ලෙස සකසන්න
android.sdk = 31
android.ndk = 25b

android.services = EdgeService:service.py

[buildozer]

log_level = 2
warn_on_root = 1
