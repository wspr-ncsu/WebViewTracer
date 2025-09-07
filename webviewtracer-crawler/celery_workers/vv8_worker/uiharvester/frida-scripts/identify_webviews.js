// https://hackernoon.com/using-javascript-to-create-and-generate-uuids
// DO NOT USE THIS IN PRODUCTION CODE!!
function uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
}


Java.performNow(function(){ 
    // Java.deoptimizeEverything();
    var webView = Java.use("android.webkit.WebView");
    var WebViewClient = Java.use("android.webkit.WebViewClient");
    var Thread = Java.use('java.lang.Thread');
    var Log = Java.use("android.util.Log");
    var debug_flag = 0; 

    Log.d("UI-LoadedWebviews","Init");   

    var Color = {
      RESET: "\x1b[39;49;00m", Black: "0;01", Blue: "4;01", Cyan: "6;01", Gray: "7;11", Green: "2;01", Purple: "5;01", Red: "1;01", Yellow: "3;01",
      Light: {Black: "0;11", Blue: "4;11", Cyan: "6;11", Gray: "7;01", Green: "2;11", Purple: "5;11", Red: "1;11", Yellow: "3;11"
      }
    };

    class WebviewLogger {
        constructor() {
            this.allWebview = {};
            this.id = uuid();
            this.webviewInjectionLog = new File(`/sdcard/Documents/webview-frida-log-${this.id}.txt`, 'w+');
        }

        getStackTrace() {
            const threadInstance = Thread.$new();
            const stack = threadInstance.currentThread().getStackTrace()
            let fullCallStack = "";
            for(var i = 0; i < stack.length; i++){
                fullCallStack += stack[i].toString() + "\n";
            }
            return fullCallStack;
        }

        logWebviewInstanceIfRequired(wv) {
            if ( this.allWebview[wv.hashCode()] ) {
                return;
            }

            this.webviewInjectionLog.write(`${JSON.stringify({type: 'INIT', hashcode: wv.hashCode(), className: wv.$className})}\n`);
            this.webviewInjectionLog.flush();
            this.allWebview[wv.hashCode()] = true;
            
        }

        log(wv, val) {
            this.logWebviewInstanceIfRequired(wv);
            this.webviewInjectionLog.write(JSON.stringify({
                data: val,
                stacktrace: this.getStackTrace(),
            }));
            this.webviewInjectionLog.write('\n');
            this.webviewInjectionLog.flush();
        }
    }

    const logger = new WebviewLogger();

    var colorLog = function (input, kwargs) {
      kwargs = kwargs || {};
      var logLevel = kwargs['l'] || 'log', colorPrefix = '\x1b[3', colorSuffix = 'm';
      if (typeof input === 'object')
          input = JSON.stringify(input, null, kwargs['i'] ? 2 : null);
      if (kwargs['c'])
          input = colorPrefix + kwargs['c'] + colorSuffix + input + Color.RESET;
      console[logLevel](input);
    };

    let overloadCount_1691770814 = webView['$init'].overloads.length;
      colorLog('\\nTracing ' +'$init' + ' [' + overloadCount_1691770814 + 'overload(s)]',{ c: Color.Green });

        for (let i = 0; i < overloadCount_1691770814; i++) {
          webView['$init'].overloads[i].implementation = function() {
          colorLog('[i] Entering Webview.' +'$init',{ c: Color.Green });
            this.setWebContentsDebuggingEnabled(true);
            console.log('Enabling setWebContentsDebuggingEnabled');
            if (arguments.length) console.log();
            
            let retval = this['$init'].apply(this, arguments);
            

            this.setWebViewClient(WebViewClient.$new());
            logger.logWebviewInstanceIfRequired(this);

            colorLog('[i] exiting Webview.' + '$init',{ c: Color.Green });

            getstacktrace("$init()");

            return retval;
      }
    }

    function highlight(tag, flag){
    if(flag)
        colorLog(tag + flag,{c:Color.Red});
    else 
        console.log(tag+flag);

    }

    function dumpWebview(wv){
        colorLog('[i] ---------------- Dumping webview settings -------------------:',{c:Color.Yellow});
        colorLog('=====> Class Name: '+wv.$className,{c:Color.Gray});
        colorLog('=====> WebView Client: '+wv.getWebViewClient()+ " " +wv.hashCode(),{c:Color.Gray});
        highlight('     Allows Content Access: ',wv.getSettings().getAllowContentAccess());
        highlight('     Allows Javascript execution: ',wv.getSettings().getJavaScriptEnabled());
        highlight('     Allows File Access: ',wv.getSettings().getAllowFileAccess());
        highlight('     Allows File Access From File URLs: ',wv.getSettings().getAllowFileAccessFromFileURLs());
        highlight('     Allows Universal Access from File URLs: ',wv.getSettings().getAllowUniversalAccessFromFileURLs());
        colorLog('[i] ---------------- Dumping webview settings EOF ---------------].',{c:Color.Yellow});

    }

    function getstacktrace(func_name){
        if (debug_flag==1){return;} 
        var threadinstance = Thread.$new();
        var stack = threadinstance.currentThread().getStackTrace()
        var full_call_stack = "";
        for(var i = 0; i < stack.length; i++){
            full_call_stack += stack[i].toString() + "\n";
        }
        colorLog("\n---------------- Stack Trace {"+func_name+"} ----------------", {c:Color.Gray})
        colorLog(full_call_stack, {c:Color.Gray})
        colorLog("----------------------- Stack Trace End -----------------------", {c:Color.Gray})
    }

    webView.getUrl.implementation = function(){
        dumpWebview(this);
        const url = this.getUrl();
        colorLog('[i] Current Loaded url:' + url,{c:Color.Blue});
        logger.log(this, { action: 'ACCESS', hashcode: this.hashCode(), func: 'getUrl', params: [JSON.stringify(url)] });
        return url;
    }

    webView.evaluateJavascript.implementation = function(script, resultCallback){
        colorLog('WebView Client: '+this.getWebViewClient()+" "+this.hashCode(),{c:Color.Blue});
        colorLog('[i] evaluateJavascript called with the following script: '+script,{c:Color.White});
        logger.log(this, { action: 'INJECT-JS', hashcode: this.hashCode(), func: 'evaluateJavascript', params: [JSON.stringify(script)] });
        this.evaluateJavascript(script,resultCallback);
    }

    webView.getOriginalUrl.implementation = function(){
        console.log('[i] Original URL: ' + this.getOriginalUrl());
        logger.log(this, {
            action: 'ACCESS',
            hashcode: this.hashCode(),
            func: 'getOriginalUrl',
            params: [JSON.stringify(url)]
        });
        return this.getOriginalUrl();
    }

    webView.addJavascriptInterface.implementation = function(object, name){
        colorLog('[i] Javascript interface detected:' + object.$className + ' instatiated as: ' + name,{c:Color.Red});
        logger.log(this, { action: 'INJECT-INTERFACE', hashcode: this.hashCode(), func: 'addJavascriptInterface', params: [JSON.stringify(object.$className), JSON.stringify(name)] });
        this.addJavascriptInterface(object,name);
    }



    webView.loadData.implementation = function(data, mimeType, encoding){
        dumpWebview(this);
        console.log('[i] Load data called with the following parameters {'+this.hashCode()+'}:\\n' + 'Data:' + data + '\\nMime type: '+mimeType+'\\nEncoding: '+ encoding);
        logger.log(this, { action: 'INJECT-LOAD', hashcode: this.hashCode(), func: 'loadData', params: [JSON.stringify(data), JSON.stringify(mimeType), JSON.stringify(encoding)] });
        getstacktrace("loadData(String, String, String)");

        this.loadData(data,mimeType,encoding);
        
    }

    webView.loadDataWithBaseURL.implementation = function(baseUrl,  data,  mimeType,  encoding,  historyUrl){
        dumpWebview(this);
        console.log('[i] loadDataWithBaseURL call detected, having the following parameters {'+this.hashCode()+'}:'+
        '\\nBaseUrl: ' + baseUrl +
        '\\nData: ' + data+
        '\\nmimeType: ' + mimeType+
        '\\nhistory URL' + historyUrl);

        logger.log(this, { action: 'INJECT-LOAD', hashcode: this.hashCode(), func: 'loadDataWithBaseURL', params: [JSON.stringify(baseUrl), JSON.stringify(data), JSON.stringify(mimeType), JSON.stringify(encoding), JSON.stringify(historyUrl)] });

        getstacktrace("loadDataWithBaseURL(String, String, String, String, String)");

        this.loadDataWithBaseURL(baseUrl,data,mimeType,encoding,historyUrl);
        
    }

    webView.loadUrl.overload('java.lang.String', 'java.util.Map').implementation = function(url,additionalHttpHeaders){
        dumpWebview(this);
        const headers = {};
        if (additionalHttpHeaders != null) {
            var iterator = additionalHttpHeaders.entrySet().iterator();
            console.log('=======Aditional headers contents:=========');
            while(iterator.hasNext()) {
                var entry = Java.cast(iterator.next(), Java.use('java.util.Map$Entry'));
                console.log(entry.getKey() + ': ' + entry.getValue());
                headers[entry.getKey()] = entry.getValue();
            }
            console.log('[i] Loading URL {'+this.hashCode()+'}: ' + url);
            console.log('===========================================');
        }
        logger.log(this, { action: 'INJECT-LOAD', hashcode: this.hashCode(), func: 'loadUrlWithHeaders', params: [JSON.stringify(url), JSON.stringify(headers)] });

        getstacktrace("loadUrl(String, Map)")
        

        this.loadUrl(url,additionalHttpHeaders);
    }

    webView.loadUrl.overload('java.lang.String').implementation = function(url){
        dumpWebview(this);
        console.log('[i] Loading URL {'+this.hashCode()+'}:' + url);
        colorLog('webView: ' +this + "webView.$className: " + this.$className );
        // addWebView(this,url);printMap();
        logger.log(this, { action: 'INJECT-LOAD', hashcode: this.hashCode(), func: 'loadUrl', params: [JSON.stringify(url)] });
 
        getstacktrace("loadUrl(String)");

        this.loadUrl(url);
        
    }

    webView.reload.overload().implementation = function(){
        dumpWebview(this);
        console.log('[i] Reloading URL {'+this.hashCode()+'}:' + this.getUrl());
        colorLog('webView: ' +this + "webView.$className: " + this.$className );
        logger.log(this, { action: 'ACTION', hashcode: this.hashCode(), func: 'reload' });
        getstacktrace("reload()");
        this.reload();
    }

    webView.postUrl.implementation = function(url, postData){
        dumpWebview(this);
        console.log('[i] Posting URL {'+this.hashCode()+'}:' + url);
        logger.log(this, { action: 'INJECT-POST', hashcode: this.hashCode(), func: 'postUrl', params: [JSON.stringify(url), JSON.stringify(postData)] });
        getstacktrace("postUrl(String, byte[])");
        this.postUrl(url, postData);
    }

    webView.postWebMessage.implementation = function(message, targetOrigin){
        dumpWebview(this);
        console.log('[i] Posting Web Message {'+this.hashCode()+'}:' + message);
        logger.log(this, { action: 'INJECT-POST', hashcode: this.hashCode(), func: 'postWebMessage', params: [JSON.stringify(message.getData()), JSON.stringify(targetOrigin.toString())] });
        getstacktrace("postWebMessage(WebMessage)");
        this.postWebMessage(message,targetOrigin);
    }
    
    webView.destroy.implementation = function (){
        console.log('[i] Destroy {'+this.hashCode()+'}');
        logger.log(this, { action: 'ACTION', hashcode: this.hashCode(), func: 'destroy' });
        this.destroy();
    };
    webView.disableWebView.implementation = function (){
        console.log('[i] disableWebView() {'+this.hashCode()+'}');
        logger.log(this, { action: 'ACTION', hashcode: this.hashCode(), func: 'disableWebView' });
        this.disableWebView();
    }
});