// Native updater presentation; status is plain text written by the installer.
ObjC.import('AppKit');

function run(argv) {
    var statusPath = argv[0];
    var app = $.NSApplication.sharedApplication;
    app.setActivationPolicy($.NSApplicationActivationPolicyAccessory);
    app.finishLaunching;
    var icon = $.NSImage.alloc.initWithContentsOfFile(argv[1]);
    app.applicationIconImage = icon;

    var window = $.NSWindow.alloc.initWithContentRectStyleMaskBackingDefer(
        $.NSMakeRect(0, 0, 480, 200), $.NSWindowStyleMaskTitled,
        $.NSBackingStoreBuffered, false);
    window.title = 'Updating Nanolathe';
    window.releasedWhenClosed = false;

    var image = $.NSImageView.alloc.initWithFrame($.NSMakeRect(24, 124, 52, 52));
    image.image = icon;
    window.contentView.addSubview(image);

    function label(text, rect, size) {
        var field = $.NSTextField.labelWithString(text);
        field.frame = rect;
        field.font = $.NSFont.systemFontOfSize(size);
        window.contentView.addSubview(field);
        return field;
    }
    var title = label('Updating Nanolathe', $.NSMakeRect(92, 150, 364, 24), 17);
    title.font = $.NSFont.boldSystemFontOfSize(17);
    label('The game will open when the update is ready.',
        $.NSMakeRect(92, 124, 364, 22), 12);
    var status = label('Downloading the updater…', $.NSMakeRect(24, 78, 432, 24), 13);
    var bar = $.NSProgressIndicator.alloc.initWithFrame($.NSMakeRect(24, 54, 432, 16));
    bar.indeterminate = true;
    bar.usesThreadedAnimation = true;
    window.contentView.addSubview(bar);
    bar.startAnimation(null);
    var hint = label('Building may take several minutes.', $.NSMakeRect(24, 20, 432, 20), 11);
    hint.textColor = $.NSColor.secondaryLabelColor;

    window.center;
    window.makeKeyAndOrderFront(null);
    app.activateIgnoringOtherApps(true);
    var files = $.NSFileManager.defaultManager;
    while (files.fileExistsAtPath(statusPath)) {
        var text = $.NSString.stringWithContentsOfFileEncodingError(
            statusPath, $.NSUTF8StringEncoding, null);
        if (text && ObjC.unwrap(text).length) status.stringValue = text;
        var event = app.nextEventMatchingMaskUntilDateInModeDequeue(
            $.NSEventMaskAny, $.NSDate.dateWithTimeIntervalSinceNow(0.2),
            $.NSDefaultRunLoopMode, true);
        if (event) app.sendEvent(event);
        app.updateWindows;
    }
    bar.stopAnimation(null);
    window.close;
}
