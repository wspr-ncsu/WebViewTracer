Java.perform(function() {
    var surface_view = Java.use('android.view.SurfaceView');

    var set_secure = surface_view.setSecure.overload('boolean');

    var TAG = "[disableSecureFlag]"

    set_secure.implementation = function(flag){
        console.log(TAG+" setSecure() flag called with args: " + flag); 
        set_secure.call(false);
    };

    var window = Java.use('android.view.Window');
    var set_flags = window.setFlags.overload('int', 'int');

    var window_manager = Java.use('android.view.WindowManager');
    var layout_params = Java.use('android.view.WindowManager$LayoutParams');

    set_flags.implementation = function(flags, mask){
        console.log(TAG+" flag secure: " + layout_params.FLAG_SECURE.value);

        console.log(TAG+" before setflags called  flags:  "+ flags);
        flags =(flags.value & ~layout_params.FLAG_SECURE.value);
        console.log(TAG+" after setflags called  flags:  "+ flags);

        set_flags.call(this, flags, mask);
    };
});
