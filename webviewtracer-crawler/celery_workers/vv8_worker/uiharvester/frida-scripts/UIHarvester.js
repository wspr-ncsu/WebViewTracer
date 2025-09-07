Java.perform(function () {
    const AccessibilityServiceWrapper = Java.use("android.accessibilityservice.AccessibilityService$IAccessibilityServiceClientWrapper");
    const AccessibilityService = Java.use("android.accessibilityservice.AccessibilityService")
    const AccessibilityEvent = Java.use("android.view.accessibility.AccessibilityEvent");
    const AccessibilityNodeInfo= Java.use("android.view.accessibility.AccessibilityNodeInfo");
    const View = Java.use("android.view.View");
    const Point = Java.use("android.graphics.Point");
    const ListView = Java.use("android.widget.ListView");
    const ScrollView = Java.use("android.widget.ScrollView");
    const GridView = Java.use("android.widget.GridView");
    const HorizontalScrollView = Java.use("android.widget.HorizontalScrollView");
    const ColorDrawable = Java.use("android.graphics.drawable.ColorDrawable");
    const Build_VERSION = Java.use("android.os.Build$VERSION");
    const Build_VERSION_CODES = Java.use("android.os.Build$VERSION_CODES");
    const Toast = Java.use("android.widget.Toast")
    const Log = Java.use("android.util.Log");
    const TagBase64 = "UIHarvester";
    const TagFrida = "Frida-Bridge";
    const Tag = "";
    const webTagJson = "UIWebHarvester";
    const webTag = "";
    var methods = View.class.getMethods();
    var cacheHash = {};
    var Base64 = {_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9+/=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/rn/g,"n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}

    function toBase64(tmp){
        var base64String = Base64.encode(tmp);
        return base64String.replace("\n", "");
    }

    function printing(args, do_base64=true) {
        var nl = "\n";
        var complete = "";
        for (let i in args) {
            if (args[i] != null) {
                complete += (args[i]);
                complete += (nl);
            }
        }
        if (complete!="") {

            if (do_base64)
            {
                Log.d(TagFrida, TagBase64+toBase64(complete));
            }
            else
            {
                Log.d(TagFrida, complete);
            }
        }
    }

    function getToastArray(context, arg2, arg3){
        var tmp = [];
        tmp.push(Tag + "Object getClass: " + "android.widget.Toast");
        tmp.push(Tag + "currentPackageName: " + context.getApplicationContext().getPackageName());

        tmp.push(Tag + "isClickable: " + "null");
        tmp.push(Tag + "isContextClickable: " + 0);
        tmp.push(Tag + "hasOnClickListeners: " + "null");
        tmp.push(Tag + "isLongClickable: " + "null");
        tmp.push(Tag + "isPressed: " + "null");
        tmp.push(Tag + "isFocusable: " + "null");
        tmp.push(Tag + "isEnabled: " + "null");
        tmp.push(Tag + "getImportantForAccessibility: " + "null");
        tmp.push(Tag + "isShown: " + "null");
        tmp.push(Tag + "hasWindowFocus: " + "null");
        //Coordinates and Location
        tmp.push(Tag + "DisplaySize: " + getDisplaySize(context).x.value + " " + getDisplaySize(context).y.value);
        tmp.push(Tag + "Coords: 0  0");
        tmp.push(Tag + "Location: " + "null");
        //XML Resources
        tmp.push(Tag + "getTag: " + "null");
        tmp.push(Tag + "ResourceId: " + "null");
        //more features
        tmp.push(Tag + "getWidth: " + "null");
        tmp.push(Tag + "getHeight: " + "null");
        tmp.push(Tag + "getColor: " + "null");

        try {
            tmp.push(Tag + "TextAlt: " + arg2);
            var getText = context.getText(arg2);
            tmp.push(Tag + "Text: " + getText);
            tmp.push(Tag + "TextLength: " + (getText.toString().replace("\n", "").replace("\r", "").length));
        } catch (error) {}

        try {
            var text = Java.cast(arg2, Java.use("java.lang.CharSequence"));
            tmp.push(Tag + "Text: " + text);
            tmp.push(Tag + "TextLength: " + (text.toString().replace("\n", "").replace("\r", "").length));
        } catch (error) {}

        return tmp;
    }

    function getDisplaySize(context){
        var ws = Java.use("android.content.Context").WINDOW_SERVICE.value;
        var wm = Java.cast(context.getSystemService(ws), Java.use("android.view.WindowManager"));
        var display = wm.getDefaultDisplay();
        var size = Point.$new()
        display.getSize(size);
        return size;
    }

    function ScreenCoords(view) {
        // var location = IntArr.$new();
        var location = Java.array('int', [0, 0]);
        view.getLocationOnScreen(location);
        var point = Point.$new(location[0], location[1])
        return point
    }

    function boolToInt(tmp) {
        return tmp ? 1 : 0;;
    }

    function checkParentClickable(view){
        var clickable=0;
        while(view != null){
            //If view.getParent() is not instanceof View -> catch error 
            try {
                view = Java.cast(view.getParent(), View);
            }
            catch (error) {
                view = null;
            }

            if (view!=null)
            {
                if (Build_VERSION.SDK_INT.value >= Build_VERSION_CODES.M.value && view.isContextClickable()==true)
                {
                    clickable=1;
                    break;
                }
                if ( view.hasOnClickListeners()==true ||
                        view.isClickable()==true ||
                        view.isLongClickable()==true ||
                        view.isFocusable()==true ||
                        view.isPressed()==true )
                {
                    clickable=1;
                    break;
                }
            }
        }
        return clickable;
    }

    function checkIfScrollable(view){
        var tmp = []
        var i = 0;
        var Spoint = ScreenCoords(view);

        while(view != null){
            //If view.getParent() is not instanceof View -> catch error 
            try {
                view = Java.cast(view.getParent(), View);
            }
            catch (error) {
                view = null;
                break;
            }

            try {
                var test = Java.cast(view, ListView);
                tmp.push(Tag+"Parent is: ListView");
                break;
            }catch (error) {}
            

            try {
                var test = Java.cast(view, ScrollView);
                tmp.push(Tag+"Parent is: ScrollView");
                break;
            }catch (error) {}

            try {
                var test = Java.cast(view, GridView);
                tmp.push(Tag+"Parent is: GridView");
                break;
            }catch (error) {}

            try {
                var test = Java.cast(view, HorizontalScrollView);
                tmp.push(Tag+"Parent is: HorizontalScrollView");
                break;
            }catch (error) {}
        }

        if (view != null) {
            tmp.push(Tag+"Parent ScrollHorizLeft: " + (view.canScrollHorizontally(-1)));
            tmp.push(Tag+"Parent ScrollHorizRight: " + (view.canScrollHorizontally(1)));
            tmp.push(Tag+"Parent ScrollVerticallyUp: " + (view.canScrollVertically(-1)));
            tmp.push(Tag+"Parent ScrollVerticallyDown: " + (view.canScrollVertically(1)));
            tmp.push(Tag+"Parent ScrollHorizLeftCoords: " + Spoint.x.value+" "+Spoint.y.value );
            tmp.push(Tag+"Parent ScrollHorizRightCoords: " + Spoint.x.value+" "+Spoint.y.value );
            tmp.push(Tag+"Parent ScrollVerticallyUpCoords: " + Spoint.x.value+" "+Spoint.y.value );
            tmp.push(Tag+"Parent ScrollVerticallyDownCoords: " + Spoint.x.value+" "+Spoint.y.value );
        }
        return tmp;
    }

    function getAxis(view){
        var Spoint = Java.cast(ScreenCoords(view), Java.use("android.graphics.Point"));

        if (Spoint.x.value < 0) {
            Spoint.x.value = Spoint.x.value * -1;
        }
        if (Spoint.y.value < 0) {
            Spoint.y.value = Spoint.y.value * -1;
        }

        var Xcoord = Spoint.x.value + 1;
        var Ycoord = Spoint.y.value + 1;

        return {"X":Xcoord, "Y":Ycoord};
    }

    function getChildTextAndAxis(view){
        var text="";
        var queue = [];

        queue.push(view)

        while(queue.length>0){
            
            try {
                var view = Java.cast(queue[0], Java.use("android.view.ViewGroup"));
            }
            catch (error) {
                try{
                    var txtView = Java.cast(queue[0], Java.use("android.widget.TextView"));
                    text = txtView.getText().toString().replace("\n", "").replace("\r", "");
                    if (text.trim() != "")
                        var axis = getAxis(view);
                        return {"Text": text, "X":axis["X"], "Y":axis["Y"]};
                }catch (error) {}
                view = null;
            }

            if (view!=null)
            {
                for (var i = 0; i < view.getChildCount(); i++) {
                    var childView = view.getChildAt(i);
                    queue.push(childView);
                    try{
                        var txtView = Java.cast(childView, Java.use("android.widget.TextView"));
                        text = txtView.getText().toString().replace("\n", "").replace("\r", "");
                        if (text.trim() != "")
                            var axis = getAxis(childView);
                            return {"Text": text, "X":axis["X"], "Y":axis["Y"]};
                    }catch (error) {}
                }
                
            }

            queue.shift();
        }
        return {"Text": "null", "X":"-1", "Y":"-1"};
    }

    function GetApproximateLocation(tmp, splitGrid, dim){
        if (tmp / splitGrid  < 1){
            if (dim=="X")return "Left";else if (dim=="Y")return "Up";
        }
        else if ( (tmp / splitGrid >= 1) && ( tmp/splitGrid < 2) ) {
            return "Center";
        }
        else if ( (tmp/splitGrid >= 2)){
            if (dim=="X")return "Right";else if (dim=="Y")return "Down";
        }
        return "ERROR";
    }

    function getLocation(x, y, context) {
        var location;
        var locationX;
        var locationY;
        //Get Display Size
        var size = getDisplaySize(context);
        var displayX = size.x.value;
        var displayY = size.y.value;

        locationX=GetApproximateLocation(x,displayX/3,"X");
        locationY=GetApproximateLocation(y,displayY/3,"Y");
        location=locationY+locationX;
        return location;
    }

    var outerState = -1
    function changeGlobal(newVal) {
        outerState = newVal; // updating the value of the global variable
    }
    function checkForState(){
        if (outerState==1){
            return true
        }
        else{
            return false
        }
    }

    try{
        Java.use("androidx.recyclerview.widget.RecyclerView$ViewFlinger").smoothScrollBy.overload('int', 'int', 'int', 'android.view.animation.Interpolator').implementation = function(a,b,c,d){
            Java.use("androidx.recyclerview.widget.RecyclerView").setScrollState.implementation = function(state){
                changeGlobal(state)
                this.setScrollState(state)
            }
            
            var is_state = checkForState()
            if (is_state)
                this.smoothScrollBy(a,b,c,d)
            else
                return
        }
    }catch(error){
        Log.d("", "Error: java.lang.ClassNotFoundException [Handled]");
    }


    
    // const service = Java.array("android.accessibilityservice.AccessibilityService", []);

    // AccessibilityService.$init.overload().implementation = function() {
    //     console.log("AccessibilityService")        
    //     return this.$init();
    // }

    // AccessibilityService.onKeyEvent.implementation = function(arg1){
    //     console.log("onKeyEvent")
    //     return this.onKeyEvent(arg1);
    // }

    // AccessibilityServiceWrapper.onKeyEvent.implementation = function(arg1, arg2){
    //     console.log("onKeyEvent- AccessibilityServiceWrapper")
    //     return this.onKeyEvent(arg1, arg2);
    // }

    // AccessibilityServiceWrapper.clearAccessibilityCache.implementation = function(){
    //     console.log("clearAccessibilityCache- AccessibilityServiceWrapper")
    //     return this.clearAccessibilityCache();
    // }

    // AccessibilityServiceWrapper.$init.overload('android.content.Context', 'android.os.Looper', 'android.accessibilityservice.AccessibilityService$Callbacks').implementation = function(arg1,arg2,arg3) {
    //     service[0] = Java.cast(arg1, AccessibilityService);
    //     console.log("IAccessibilityServiceClientWrapper")
    //     return this.$init(arg1,arg2,arg3);
    // }

    // AccessibilityServiceWrapper.onAccessibilityEvent.overload('android.view.accessibility.AccessibilityEvent', 'boolean').implementation = function (event, bool) {
    //     console.log("aaaaaaaaaaaaaaaaaa")

    //     var tmpEvent = Java.cast(event, AccessibilityEvent);
    //     var thisNode = null;

    //     //event.getPackageName().toString()

    //     // try{
    //     //     thisNode = tmpEvent.getSource();
    //     // }catch(error){
    //     //     Log.d("Exception[thisNode]");
    //     // }

    //     // if (thisNode != null){
    //     //     if (Build_VERSION.SDK_INT.value >= Build_VERSION_CODES.LOLLIPOP.value){
    //     //         Log.d(thisNode)
    //     //     }
    //     // }

    //     return this.onAccessibilityEvent(event, bool);
    // }

    // View.draw.overload('android.graphics.Canvas').implementation = function (arg1) {
    //     // this.draw.overload('android.graphics.Canvas').call(this, arg1);
    //     this.draw(arg1);
    //     // this.draw.overload('android.graphics.Canvas').call(this, arg1);
    //     // this.onDraw(arg1);
    //     //View

    //     var tmpView = Java.cast(this, Java.use("android.view.View"));

    //     //getContext
    //     var ctx = View.class.getDeclaredField("mContext");
    //     ctx.setAccessible(true);
    //     var context = Java.cast(ctx.get(tmpView), Java.use("android.content.Context"));

    //     //UIHarvester Stuff
    //     var tmp = [];
    //     var i = 0;

    //     var Spoint = Java.cast(ScreenCoords(tmpView), Java.use("android.graphics.Point"));

    //     if (Spoint.x.value < 0) {
    //         Spoint.x.value = Spoint.x.value * -1;
    //     }
    //     if (Spoint.y.value < 0) {
    //         Spoint.y.value = Spoint.y.value * -1;
    //     }

    //     var Xcoord = Spoint.x.value + 1;
    //     var Ycoord = Spoint.y.value + 1;
    //     var tmpArray = Java.array('int', [Spoint.x.value + (tmpView.getWidth() / 2), Spoint.y.value + (tmpView.getHeight() / 2)]);
    //     var Cpoint = Point.$new(tmpArray[0], tmpArray[1]);

    //     // var objectHash = "Obj" + tmpView.hashCode()+Xcoord+Ycoord

    //     // if (tmpView.hasWindowFocus()){ //&& !(objectHash in cacheHash)){

    //         // cacheHash[objectHash] = '1';

    //         var isClickable = boolToInt(tmpView.isClickable())
    //         var isContextClickable = 0
    //         var hasOnClickListeners = boolToInt(tmpView.hasOnClickListeners())
    //         var isLongClickable = boolToInt(tmpView.isLongClickable())
    //         var isPressed = boolToInt(tmpView.isPressed())
    //         var isFocusable = boolToInt(tmpView.isFocusable())

    //         tmp.push(Tag + "Object getClass: " + (tmpView.getClass().toString()));
    //         tmp.push(Tag + "currentPackageName: " + context.getApplicationContext().getPackageName());
    //         tmp.push(Tag + "Object hashCode: " + (tmpView.hashCode()));
    //         //True or False
    //         tmp.push(Tag + "isClickable: " + isClickable);
    //         if (Build_VERSION.SDK_INT.value >= Build_VERSION_CODES.M.value) {
    //             isContextClickable = boolToInt(tmpView.isContextClickable())
    //             tmp.push(Tag + "isContextClickable: " + isContextClickable);
    //         } else {
    //             tmp.push(Tag + "isContextClickable: " + 0);
    //         }
    //         tmp.push(Tag + "hasOnClickListeners: " + hasOnClickListeners);
    //         tmp.push(Tag + "isLongClickable: " + isLongClickable);
    //         tmp.push(Tag + "isPressed: " + isPressed);
    //         tmp.push(Tag + "isFocusable: " + isFocusable);
    //         tmp.push(Tag + "isEnabled: " + boolToInt(tmpView.isEnabled()));
    //         tmp.push(Tag + "hasWindowFocus: " + boolToInt(tmpView.hasWindowFocus()));
    //         // tmp.push(Tag + "parentClickable: " + checkParentClickable(Java.cast(this, View)));

    //         var IS_CLICKABLE = isClickable | isContextClickable | hasOnClickListeners | isLongClickable | isPressed

    //         // try {
    //         //     //isScrollContainer --- dokimase kai auto
    //         //     var parent = null;
    //         //     parent = Java.cast(tmpView.getParent(), View);
    //         //     tmp = tmp.concat(checkIfScrollable(tmpView));
    //         // } catch (error) {}

    //         //Coordinates and Location
    //         tmp.push(Tag + "DisplaySize: " + getDisplaySize(context).x.value + " " + getDisplaySize(context).y.value);
    //         tmp.push(Tag + "Coords: " + Xcoord + " " + Ycoord);
    //         tmp.push(Tag + "Location: " + getLocation(Spoint.x.value, Spoint.y.value, context));

    //         //XML Resources
    //         try {
    //             tmp.push(Tag + "getTag: " + tmpView.getTag());
    //         } catch (error) {
    //             tmp.push(Tag + "getTag: " + "null");
    //         }
    //         try {
    //             tmp.push(Tag + "ResourceId: " + tmpView.getResources().getResourceEntryName(tmpView.getId()));
    //         } catch (error) {
    //             tmp.push(Tag + "ResourceId: " + "null");
    //         }

    //         // var methods = tmpView.getClass().getMethods()
    //         var text = 0;

    //         // for (var i = 0; i < methods.length; i++) {
    //         //     var str = methods[i].toString()

    //             // if (str.includes(".getText(")){
    //             try{
    //                 var txtView = Java.cast(tmpView, Java.use("android.widget.TextView"))

    //                 tmp.push(Tag + "getContentDescription: " + txtView.getContentDescription());
    //                 tmp.push(Tag + "getTransitionName: " +txtView.getTransitionName());

    //                 tmp.push(Tag + "Text: " + txtView.getText().toString().replace("\n", "").replace("\r", ""));

    //                 //more features
    //                 tmp.push(Tag + "getTextSize: " + txtView.getTextSize());
    //                 if(txtView.getTypeface()!=null)
    //                     tmp.push(Tag + "getTypeface: " + txtView.getTypeface().getStyle());
    //                 else
    //                     tmp.push(Tag + "getTypeface: null");
    //                 tmp.push(Tag + "TextLength: " + txtView.getText().toString().replace("\n", "").replace("\r", "").length);

    //                 var hexColor = "#" + (0xFFFFFF & txtView.getCurrentTextColor()).toString(16);
    //                 tmp.push(Tag + "getCurrentTextColor: " + hexColor);
    //                 text = 1;
    //                 // break;
    //             }catch (error){
    //                 tmp.push(Tag + "Text: " + "null");
    //                 tmp.push(Tag + "getContentDescription: " + "null");
    //             }

    //         // }
            
    //         if (text == 0 && IS_CLICKABLE == 1) {
    //             var child = getChildTextAndAxis(Java.cast(this, View));
    //             tmp.push(Tag + "getChildText: " + child["Text"]);
    //             tmp.push(Tag + "childX: " + child["X"]);
    //             tmp.push(Tag + "childY: " + child["Y"]);
    //             tmp.push(Tag + "getImportantForAccessibility: 1"); //vale allo label
    //             tmp.push(Tag + "isShown: 1"); //vale allo label
    //         }
    //         else{
    //             tmp.push(Tag + "getImportantForAccessibility: " + tmpView.getImportantForAccessibility());
    //             tmp.push(Tag + "isShown: " + boolToInt(tmpView.isShown()));
    //             tmp.push(Tag + "getChildText: null");
    //             tmp.push(Tag + "childX: 0");
    //             tmp.push(Tag + "childY: 0");
    //         }

    //         tmp.push(Tag + "getWidth: " + tmpView.getWidth());
    //         tmp.push(Tag + "getHeight: " + tmpView.getHeight());
    //         try{
    //             var tmpColor = Java.cast(tmpView.getBackground(), ColorDrawable);
    //             var color = tmpColor.getColor();
    //             var hexColor = "#" + color.toString(16);
    //             tmp.push(Tag + "getColor: " + hexColor);
    //         }catch(error){}
                
    //         //End Features
    //         // printing(tmp);
    //         // console.log(tmp)
    //         printing(tmp)
    //     // }


    //     // this.draw(arg1,arg2,arg3)
    // }

    Toast.makeText.overload('android.content.Context', 'int', 'int').implementation = function (arg1, arg2, arg3) {
        var context = Java.cast(arg1, Java.use("android.content.Context"));
        //UIHarvester Stuff
        var tmp = getToastArray(context, arg2, arg3);

        printing(tmp);
        return this.makeText(arg1, arg2, arg3);
    }

    Toast.makeText.overload('android.content.Context', 'java.lang.CharSequence', 'int').implementation = function (arg1, arg2, arg3) {
        var context = Java.cast(arg1, Java.use("android.content.Context"));
        //UIHarvester Stuff
        var tmp = getToastArray(context, arg2, arg3);

        printing(tmp);
        return this.makeText(arg1, arg2, arg3);
    }

    Toast.makeText.overload('android.content.Context', 'android.os.Looper', 'java.lang.CharSequence', 'int').implementation = function (arg1, arg2, arg3, arg4) {
        var context = Java.cast(arg1, Java.use("android.content.Context"));
        //UIHarvester Stuff
        var tmp = getToastArray(context, arg3, arg4);

        printing(tmp);
        return this.makeText(arg1, arg2, arg3, arg4);
    }
});