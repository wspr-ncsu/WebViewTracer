# WebView Build Instructions

This document outlines the steps to build a custom WebView provider, incorporating VisibleV8 patches.

---

### 1. Install Depot Tools

**Chromium Android Build:** [Link](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/android_build_instructions.md#Install-depot_tools)

1.  **Clone the `depot_tools` repository:**
    ```bash
    git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
    ```

2.  **Add `depot_tools` to your system's PATH:**
    ```bash
    export PATH="$PATH:/path/to/depot_tools"
    ```

---

### 2. Get the Chromium Code

1.  **Create a directory for Chromium and navigate into it:**
    ```bash
    mkdir ~/chromium && cd ~/chromium
    ```

2.  **Fetch the Android-specific Chromium code:**
    ```bash
    fetch --nohooks android
    ```

3.  **Navigate into the `src/` directory:**
    ```bash
    cd src
    ```

---

### 3. Install Additional Build Dependencies

1.  **Run the build dependencies script for Android:**
    ```bash
    build/install-build-deps.sh --android
    ```

---

### 4. Run Hooks

1.  **Execute the `gclient runhooks` command to synchronize dependencies:**
    ```bash
    gclient runhooks
    ```

**Reference:** [Webview Quick Start](https://chromium.googlesource.com/chromium/src/+/HEAD/android_webview/docs/quick-start.md)

---

### 5. Checking Out a Specific Chromium Branch

To ensure compatibility with your patches, you'll need to check out the corresponding Chromium branch.

**Reference:** [Working with Release Branches](https://www.chromium.org/developers/how-tos/get-the-code/working-with-release-branches/)

**Example (Chromium 138):**

Suppose you want to apply a patch set for Chromium 138, such as the one found in the `./138` subdirectory

1.  **Synchronize with branch heads and tags:**
    ```bash
    gclient sync --with_branch_heads --with_tags
    ```

2.  **Fetch the latest changes:**
    ```bash
    git fetch
    ```

3.  **Checkout the desired branch:**
    Replace `$BRANCH` with the appropriate branch ID (e.g., `5672` for Chromium 113). You can find specific branch IDs at [Chromium Dash Branches](https://chromiumdash.appspot.com/branches).
    ```bash
    git checkout -b branch_$BRANCH branch-heads/$BRANCH
    ```

4.  **Synchronize again after checking out the branch:**
    ```bash
    gclient sync --with_branch_heads --with_tags
    ```

---

### 6. Applying the Patches

To build a VisibleV8 WebView, you will need specific patches for your Chromium version (e.g., Chromium 138). This typically includes a `trace-apis.patch` and a `chrome-sandbox.patch`.

**Patch Files (Example for Chromium 138):**
*   [Chromium 138 Trace APIs Patch](./patches/138/trace-apis.patch)
*   [Chromium 138 Sandbox Patch](./patches/138/chrome-sandbox.patch)

1.  **Apply `trace-apis.patch`:**
    *   Navigate to the `src/v8/` directory:
        ```bash
        cd src/v8
        ```
    *   Apply the patch (a dry run is recommended first):
        ```bash
        patch -p1 <$CURRENT_REPO/patches/138/trace-apis.patch
        ```
    *   Return to the `src/` directory:
        ```bash
        cd ../
        ```

2.  **Apply `chrome-sandbox.patch`:**
    *   Ensure you are in the `src/` directory.
    *   Apply the patch:
        ```bash
        patch -p1 <$CURRENT_REPO/patches/138/chrome-sandbox.patch
        ```

---

### 7. Setting Up the Build (GN Arguments)

Configure your build arguments using `gn args out/Default`. Add or modify the following lines:

```gn
# Set build arguments here. See `gn help buildargs`.
target_os = "android"

# See "Figuring out target_cpu" below
target_cpu = "arm64"

# Not always necessary, see "Changing package name" below
system_webview_package_name = "com.google.android.webview.beta"

dcheck_always_on=false
is_debug=false
disable_fieldtrial_testing_config=true
is_official_build=true
is_component_build = false
use_thin_lto=false
is_cfi=false
chrome_pgo_phase=0
v8_use_external_startup_data=true
```

---

### 8. Build, Install, and Switch WebView Provider

1.  **Build the WebView APK:**
    ```bash
    autoninja -C out/Default system_webview_apk
    ```

2.  **Install the generated APK:** Use Android terminal systemizer on a rooted install to systemize the APK into the `/system/priv-app` directory

3.  **Disable multi-process WebViews:**
    This allows V8 to dump files to disk. Multi-process is a security feature that isolates WebViews from the rest of the app and has negligible overhead on crawling speed.
    ```bash
    adb shell cmd webviewupdate disable-multiprocess
    ```

4.  **Tell the Android platform to load your custom WebView implementation:**
    ```bash
    out/Default/bin/system_webview_apk set-webview-provider
    ```
