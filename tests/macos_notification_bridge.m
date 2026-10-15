// Exercise the real bridge against an in-memory center. No OS request is sent.
#import <objc/runtime.h>
#include <assert.h>
#include "../zapzap/features/notifications/macos_notifications.m"

@interface ZNFakeCenter : NSObject
@property(nonatomic) int pendingRemovals;
@property(nonatomic) int deliveredRemovals;
@property(nonatomic) int submissions;
@property(nonatomic, copy) void (^settingsCallback)(UNNotificationSettings *);
@end
@implementation ZNFakeCenter
- (void)getNotificationSettingsWithCompletionHandler:(void (^)(UNNotificationSettings *))callback {
    self.settingsCallback = callback;
}
- (void)removePendingNotificationRequestsWithIdentifiers:(NSArray<NSString *> *)identifiers {
    assert(identifiers.count == 1);
    self.pendingRemovals++;
}
- (void)removeDeliveredNotificationsWithIdentifiers:(NSArray<NSString *> *)identifiers {
    assert(identifiers.count == 1);
    self.deliveredRemovals++;
}
- (void)addNotificationRequest:(UNNotificationRequest *)request withCompletionHandler:(void (^)(NSError *))callback {
    (void)request;
    (void)callback;
    self.submissions++;
}
@end

static ZNFakeCenter *test_center;
static id test_current_center(id object, SEL selector) {
    (void)object;
    (void)selector;
    return test_center;
}

int main(void) {
    @autoreleasepool {
        test_center = [ZNFakeCenter new];
        Method method = class_getClassMethod([UNUserNotificationCenter class],
            @selector(currentNotificationCenter));
        IMP previous = method_setImplementation(method, (IMP)test_current_center);
        zn_delegate = [ZNDelegate new];
        zn_entries = [NSMutableDictionary dictionary];

        // Registration must exist before native send returns to a closing Qt
        // page. Original queued registration fails this assertion.
        assert(zn_send("synthetic-request", "Synthetic title", "Synthetic body", NULL, 0) == 1);
        assert(zn_entries[@"synthetic-request"] != nil);
        zn_remove("synthetic-request");
        // aboutToQuit cannot depend on a later main-loop iteration.
        assert(zn_entries[@"synthetic-request"] == nil);
        assert(test_center.pendingRemovals == 1);
        assert(test_center.deliveredRemovals == 1);

        // A response arriving after cancellation must not recreate a request.
        test_center.settingsCallback(nil);
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.02, false);
        assert(zn_entries.count == 0);
        assert(test_center.submissions == 0);
        zn_remove("synthetic-request");
        assert(test_center.pendingRemovals == 1);

        __block int backgroundResult = -1;
        dispatch_semaphore_t finished = dispatch_semaphore_create(0);
        // dispatch_sync may execute inline on the caller, so use a real thread
        // to verify the main-thread API boundary.
        [NSThread detachNewThreadWithBlock:^{
            @autoreleasepool {
                backgroundResult = zn_send("background-request", "Title", "Body", NULL, 0);
                dispatch_semaphore_signal(finished);
            }
        }];
        assert(dispatch_semaphore_wait(finished,
            dispatch_time(DISPATCH_TIME_NOW, 2 * NSEC_PER_SEC)) == 0);
        assert(backgroundResult == 0);
        assert(zn_entries.count == 0);
        method_setImplementation(method, previous);
        puts("native notification lifecycle: PASS");
    }
    return 0;
}
