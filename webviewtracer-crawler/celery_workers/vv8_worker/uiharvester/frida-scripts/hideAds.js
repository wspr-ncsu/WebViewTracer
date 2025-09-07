Java.performNow(function(){ 
    // Java.deoptimizeEverything();

    var webView = Java.use("android.webkit.WebView");
    var webSettings = Java.use("android.webkit.WebSettings");
    var WebViewClient = Java.use("android.webkit.WebViewClient");
    var WebChromeClient = Java.use("android.webkit.WebChromeClient");
    var Thread = Java.use('java.lang.Thread');
    var Log = Java.use("android.util.Log"); 
    const View = Java.use("android.view.View");

    let overloadCount_1691770814 = webView['$init'].overloads.length;
    for (let i = 0; i < overloadCount_1691770814; i++) {
      webView['$init'].overloads[i].implementation = function() {
        this.setWebContentsDebuggingEnabled(true);
        console.log('Enabling setWebContentsDebuggingEnabled');
        if (arguments.length) console.log();
        
        let retval = this['$init'].apply(this, arguments);

        // init webChrome/WebView clients
        //View.GONE == 8, View.INVISIBLE == 4,
        // this.setVisibility(8);
        // this.destroy()

        console.log(this.getUrl());

        this.setWebViewClient(WebViewClient.$new());
        this.setWebChromeClient(WebChromeClient.$new());

        return retval;
      }
    }


     webView.setWebChromeClient.implementation = function(client){

        WebChromeClient.onProgressChanged.implementation = function(webView, newProgress){
            console.log(webView.getUrl())
            if (webView.getUrl().includes("https://googleads.g.doubleclick.net") || webView.getUrl().includes("about:blank"))
            {
                webView.destroy()
                console.log("webView.destroy()")
            }

            this.onProgressChanged(webView, newProgress)

            var retval = this.onProgressChanged.apply(this, arguments);
            return retval;


        }
        var retval = this.setWebChromeClient.apply(this, arguments)
        return retval;  
    }

    webView.setWebViewClient.implementation = function(client){

        WebViewClient.onPageStarted.implementation = function(webView, url, favicon) {
            
            console.log(webView.getUrl(), url)
            if (url.includes("https://googleads.g.doubleclick.net") || url.includes("about:blank"))
            {
                webView.destroy()
                console.log("webView.destroy()")
            }

            var retval = this.onPageStarted.apply(this, arguments);
            return retval;

        }


        // onPageFinished is called twice --> https://issuetracker.google.com/issues/36983315
        WebViewClient.onPageFinished.implementation = function(webView, url) {
                
            console.log(webView.getUrl(), url)
            if (url.includes("https://googleads.g.doubleclick.net") || url.includes("about:blank")){
                webView.destroy()
                console.log("webView.destroy()")
            }

            var retval = this.onPageFinished.apply(this, arguments);
            return retval;

        }

        this.setWebViewClient(client);// an to balw trexei h kanonikh onPageFinished pou sto app mou exei to evalJS, an den to balw trexei i dikia mou
        
        var retval = this.setWebViewClient.apply(this, arguments);
        return retval;  
    }
});