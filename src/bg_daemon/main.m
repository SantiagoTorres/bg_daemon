#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>

int main(int argc, const char * argv[]) {
  int ret = 0;

  @autoreleasepool {
    NSUserDefaults *args = [NSUserDefaults standardUserDefaults];

    NSError *error=nil;
    NSString *backgroundPicture = nil;
    NSWorkspace *workspace = [NSWorkspace sharedWorkspace];
    BOOL backgroundChanged = NO;

    backgroundPicture = [args stringForKey:@"i"] ? [args stringForKey:@"i"] : [args stringForKey:@"-input"];

    // ghetto way to check if help is on or not
    if ([[[NSProcessInfo processInfo] arguments] containsObject:@"-h"] ||
        [[[NSProcessInfo processInfo] arguments] containsObject:@"--help"]){
      fprintf(stdout, "quack: update your desktop background\n");
      fprintf(stdout, "-i (--input) - input filepath to list of frames "\
                      "and durations\n");
      fprintf(stdout, "-h (--help)  - print help text and exit\n");
      return ret;
    }

    // do not execute a thing if the file input is not passed in
    if (backgroundPicture == nil) {
        fprintf(stderr, "The -i (--input) argument is required, pass in a "
                "background picture.\n");
        exit(1);
    }

    backgroundChanged = [workspace setDesktopImageURL:[NSURL fileURLWithPath:backgroundPicture]
                                            forScreen:[NSScreen mainScreen]
                                              options:nil
                                                error:&error];

    if (!backgroundChanged){
      fprintf(stderr, "Cannot change background image.\n");
      ret ++;
    }
    if (error){
      fprintf(stderr, "%s\n", [[error localizedDescription] UTF8String]);
      ret ++;
    }
  }
  return ret;
}

