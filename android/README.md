# 📱 How to Build the Dedicated Android APK

You can turn **Avii's YT Grabber** into an installable Android `.apk` using either of the two methods below.

---

## ⚡ Method 1: 1-Minute Online APK Generator (No Coding Needed)

Once your website is hosted on **Vercel** (`https://your-app.vercel.app`):

1. Go to **[WebIntoApp.com](https://www.webintoapp.com)** or **[PWABuilder.com](https://www.pwabuilder.com)**.
2. Enter your URL: `https://your-app.vercel.app`
3. Enter App Name: `Avii's YT Grabber`
4. Set App Icon (choose an arcade/retro icon).
5. Enable **"Download Listener / Save to Device"**.
6. Click **"Make APK"** and download the `.apk` file directly onto your phone!
7. Tap the file on your phone to install.

---

## 🛠️ Method 2: Native Android Studio WebView (Professional)

If you have **Android Studio** installed, you can build a lightweight (2 MB) native APK:

### 1. `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.avii.ytgrabber">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="YT Grabber"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.NoActionBar"
        android:usesCleartextTraffic="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### 2. `MainActivity.kt`

```kotlin
package com.avii.ytgrabber

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.webkit.CookieManager
import android.webkit.URLUtil
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView

    // Replace with your Vercel URL
    private val APP_URL = "https://your-app.vercel.app"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            loadWithOverviewMode = true
            useWideViewPort = true
        }

        webView.webViewClient = WebViewClient()

        // Intercept downloads and route directly into Android Downloads & Gallery
        webView.setDownloadListener { url, userAgent, contentDisposition, mimetype, _ ->
            val request = DownloadManager.Request(Uri.parse(url)).apply {
                setMimeType(mimetype)
                addRequestHeader("cookie", CookieManager.getInstance().getCookie(url))
                addRequestHeader("User-Agent", userAgent)
                setDescription("Downloading media stream...")
                
                val filename = URLUtil.guessFileName(url, contentDisposition, mimetype)
                setTitle(filename)
                setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
            }

            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            Toast.makeText(applicationContext, "Downloading to Gallery...", Toast.LENGTH_SHORT).show()
        }

        webView.loadUrl(APP_URL)
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
```

---

### 3. How Downloads Appear in Gallery Automatically
Because the download uses Android's native `DownloadManager` targeting `Environment.DIRECTORY_DOWNLOADS`, Android automatically indexes completed MP4 video files straight into **Google Photos**, **Samsung Gallery**, and **VLC**!
