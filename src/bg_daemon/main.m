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

    // ghetto way to check if help is on or not
    if ([[[NSProcessInfo processInfo] arguments] containsObject:@"-h"] ||
        [[[NSProcessInfo processInfo] arguments] containsObject:@"--help"]){
      fprintf(stdout, "quack: update your main screen's desktop background\n");
      fprintf(stdout, "\nUsage:\n");
      fprintf(stdout, "quack <filename> [-h/--help]\n");
      fprintf(stdout, "\nOptions:\n");
      fprintf(stdout, "-h (--help)  - print help text and exit\n");
      return ret;
    }

    if (argc > 1){
      backgroundPicture = [[NSString alloc] initWithCString:argv[1]
                                                   encoding:NSUTF8StringEncoding];
    }
    else{
      fprintf(stderr, "No image passed, not changing the desktop background\n");
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

