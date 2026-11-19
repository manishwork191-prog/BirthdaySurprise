[app]
title = Birthday Surprise
package.name = birthdaysurprise
package.domain = org.love
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,mp3
source.exclude_dirs = .github,bin
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 24
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
