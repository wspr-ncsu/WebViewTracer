# WebViewTracer

![WebViewTracer](./wordmark.svg)

This repository contains the artifact for our paper:

**_Cross-Boundary Mobile Tracking: Exploring Java-to-JavaScript Information Diffusion in WebViews_**

The artifact is divided into three main components:

## Quick Start

### Build VisibleV8 for WebViews
```sh
cd patches && bash ./build.sh
````

You may also use prebuilt binaries from the [upstream VisibleV8 project](https://github.com/wspr-ncsu/visiblev8).

### Run the crawler system
To run a small-scale experiment on an emulator with a known set of apps run:

```sh
cd webviewtracer-crawler && bash ./setup.sh
```

### Access execution traces

You can access the execution traces collected during the experiment [on DataDryad](http://datadryad.org/share/aGfKK8cTsp7uDGu3tjkcPX5cGwqGngJH9ekPTIj8qn4).

For detailed instructions, see the [artifact appendix](./artifact.pdf).

## System Requirements

* **Operating System:** Linux (tested on Ubuntu 24.04; other modern Linux distributions should work).
* **Hardware:**

  * Minimum: 8 CPU cores, 16 GB RAM, 200 GB free disk space (from Chromium builds)
  * Recommended: 16+ CPU cores, 32+ GB RAM, 1TB free disk space
* **Dependencies:**

  * [Python 3.10+](https://www.python.org/)
  * [Docker](https://docs.docker.com/) (for  crawling).
  * Standard build tools: `git`, `make`, `unzip`, `curl`

Please make sure you are able to docker without `sudo` privileges by following the [instructions documented here](https://docs.docker.com/engine/install/linux-postinstall/).

## Mobile requirements

If you plan on conducting a large-scale crawl, we recommend setting up a phone with the following specifications:
- A phone (preferably a Pixel) that has higher specs than a [Pixel 4a](https://en.wikipedia.org/wiki/Pixel_4a) and is an unlocked bootloader.
- Storage size of more than 5 GB
- Android 13 that has been rooted using [Magisk](https://topjohnwu.github.io/Magisk/install.html)
- Has the [UIHaversterService.apk](webviewtracer-crawler/celery_workers/vv8_worker/uiharvester/Services/UIHarvesterService.apk) app installed
- Screen locking is explicitly set to "None"
- Has the VisibleV8 Webview version Systemized on top of the [Android Beta WebViews](https://play.google.com/store/apps/details?id=com.google.android.webview.beta&hl=en_US) app which should be set as the default webview provider.

## Repository Structure

* **`VisibleV8WebView`**
  Located in `./patches`. Contains the modified VisibleV8 patches and build instructions for instrumented WebViews (based on Chromium v138).

* **`WebViewTracerCrawler`**
  Located in `./webviewtracer-crawler`. Contains the crawler system used to run experiments across our app dataset.

* **`Dataset`**
  Located in `./dataset`. Includes a JSON file with app metadata (hashes, versions, names) and a description of the app collection process.

## Research paper

If you use any component of WebViewTracer in your research, please cite:

```bibtex
@inproceedings{datta2025webviewtracer,
  title={Cross-Boundary Mobile Tracking: Exploring Java-to-JavaScript Information Diffusion in WebViews},
  author={Datta, Sohom and Diamantaris, Michalis and Zafar, Ahsan and Su, Junhua and Das, Anupam and Polakis, Jason and Kapravelos, Alexandros},
  booktitle={Proceedings of the Network and Distributed System Security Symposium (NDSS)},
  year={2026},
}
```
