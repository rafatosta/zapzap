// Public macOS notification bridge, loaded inside the existing ZapZap bundle.
#import <AppKit/AppKit.h>
#import <UserNotifications/UserNotifications.h>
#import <Intents/Intents.h>
#import <UniformTypeIdentifiers/UniformTypeIdentifiers.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>

// Events: accepted=1, clicked=2, withdrawn=3, failed=4, foreground=5,
// communication decoration=6 (0=success), explicit attachment fallback=7.
// Error values are numeric only. Never return text, paths, images or user IDs.
typedef void (*ZNCallback)(const char *, int, int, int, int);
static ZNCallback zn_callback;
static NSMutableDictionary<NSString *, id> *zn_entries;

@interface ZNEntry : NSObject
@property(nonatomic, copy) NSString *identifier;
@property(nonatomic, copy) NSString *directory;
@end
@implementation ZNEntry
@end

static void zn_event(NSString *identifier, int event, int error, int attachments, int authorization) {
    if (zn_callback) zn_callback(identifier.UTF8String, event, error, attachments, authorization);
}

static void zn_cleanup(ZNEntry *entry) {
    if (entry.directory) {
        [[NSFileManager defaultManager] removeItemAtPath:entry.directory error:nil];
        entry.directory = nil;
    }
}

static UNNotificationAttachment *zn_attachment(NSData *data, ZNEntry *entry, NSError **error) {
    if (!data.length || data.length > 10 * 1024 * 1024) return nil;
    // mkdtemp creates a fresh 0700 directory. No image pathname comes from web data.
    NSString *template = [NSTemporaryDirectory() stringByAppendingPathComponent:@"zapzap-avatar-XXXXXX"];
    char *buffer = strdup(template.fileSystemRepresentation);
    char *created = mkdtemp(buffer);
    if (!created) { free(buffer); return nil; }
    entry.directory = [[NSFileManager defaultManager] stringWithFileSystemRepresentation:created length:strlen(created)];
    free(buffer);
    NSString *path = [entry.directory stringByAppendingPathComponent:@"avatar.png"];
    // Exclusive owner-only creation, followed by a complete write.
    int fd = open(path.fileSystemRepresentation, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (fd < 0) { zn_cleanup(entry); return nil; }
    const unsigned char *bytes = data.bytes;
    size_t remaining = data.length;
    while (remaining) {
        ssize_t wrote = write(fd, bytes, remaining);
        if (wrote <= 0) { close(fd); zn_cleanup(entry); return nil; }
        bytes += wrote; remaining -= wrote;
    }
    close(fd);
    UNNotificationAttachment *attachment = [UNNotificationAttachment attachmentWithIdentifier:@"avatar"
        URL:[NSURL fileURLWithPath:path] options:@{UNNotificationAttachmentOptionsTypeHintKey: UTTypePNG.identifier} error:error];
    if (!attachment) zn_cleanup(entry);
    return attachment;
}

@interface ZNDelegate : NSObject <UNUserNotificationCenterDelegate>
@end
@implementation ZNDelegate
- (void)userNotificationCenter:(UNUserNotificationCenter *)center willPresentNotification:(UNNotification *)notification
        withCompletionHandler:(void (^)(UNNotificationPresentationOptions))completionHandler {
    NSString *identifier = notification.request.identifier;
    dispatch_async(dispatch_get_main_queue(), ^{
        if (zn_entries[identifier]) zn_event(identifier, 5, 0, (int)notification.request.content.attachments.count, -1);
    });
    completionHandler(UNNotificationPresentationOptionBanner | UNNotificationPresentationOptionList);
}
- (void)userNotificationCenter:(UNUserNotificationCenter *)center didReceiveNotificationResponse:(UNNotificationResponse *)response
        withCompletionHandler:(void (^)(void))completionHandler {
    NSString *identifier = response.notification.request.identifier;
    BOOL clicked = [response.actionIdentifier isEqualToString:UNNotificationDefaultActionIdentifier];
    dispatch_async(dispatch_get_main_queue(), ^{
        ZNEntry *entry = zn_entries[identifier];
        if (!entry) return;
        [center removeDeliveredNotificationsWithIdentifiers:@[identifier]];
        [zn_entries removeObjectForKey:identifier];
        zn_cleanup(entry);
        zn_event(identifier, clicked ? 2 : 3, 0, 0, -1);
    });
    completionHandler();
}
@end
static ZNDelegate *zn_delegate;

static UNNotificationContent *zn_decorate(UNNotificationContent *content, NSData *data,
        NSString *requestID, NSString *conversation, NSString *senderName,
        NSString *groupName, NSData *groupData, NSError **error) {
    if (!data.length) return nil;
    // App-local unknown handles, never phone numbers/contact IDs. No donation.
    INPersonHandle *handle = [[INPersonHandle alloc] initWithValue:requestID type:INPersonHandleTypeUnknown];
    INPerson *sender = [[INPerson alloc] initWithPersonHandle:handle nameComponents:nil displayName:senderName
        image:[INImage imageWithImageData:data] contactIdentifier:nil customIdentifier:nil
        isMe:NO suggestionType:INPersonSuggestionTypeNone];
    INSpeakableString *group = groupName.length ? [[INSpeakableString alloc] initWithSpokenPhrase:groupName] : nil;
    INSendMessageIntent *intent = [[INSendMessageIntent alloc] initWithRecipients:nil
        outgoingMessageType:INOutgoingMessageTypeOutgoingMessageText content:content.body
        speakableGroupName:group conversationIdentifier:conversation ?: requestID
        serviceName:nil sender:sender attachments:nil];
    if (group && groupData.length) {
        [intent setImage:[INImage imageWithImageData:groupData] forParameterNamed:@"speakableGroupName"];
    }
    @try {
        // The returned content is immutable and is submitted without mutation.
        return [content contentByUpdatingWithProvider:intent error:error];
    } @catch (NSException *exception) {
        if (error) *error = [NSError errorWithDomain:UNErrorDomain code:UNErrorCodeContentProvidingInvalid userInfo:nil];
        return nil;
    }
}

static UNNotificationContent *zn_fallback_content(ZNEntry *entry, NSString *title,
        NSString *body, NSData *data, NSError **error) {
    if (error) *error = nil;
    UNMutableNotificationContent *content = [UNMutableNotificationContent new];
    content.title = title; content.body = body;
    // WhatsApp supplies existing sound; do not add native sound or Focus override.
    UNNotificationAttachment *attachment = zn_attachment(data, entry, error);
    if (data.length && !attachment) return nil;
    content.attachments = attachment ? @[attachment] : @[];
    return content;
}

static void zn_submit(ZNEntry *entry, UNNotificationContent *content, int auth,
        BOOL allowAttachmentFallback, NSString *title, NSString *body, NSData *data) {
    NSString *requestID = entry.identifier;
    if (zn_entries[requestID] != entry) return;
    UNNotificationRequest *request = [UNNotificationRequest requestWithIdentifier:requestID content:content trigger:nil];
    [[UNUserNotificationCenter currentNotificationCenter] addNotificationRequest:request withCompletionHandler:^(NSError *error) {
        dispatch_async(dispatch_get_main_queue(), ^{
            NSError *deliveryError = error;
            zn_cleanup(entry);
            if (zn_entries[requestID] != entry) {
                UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
                [center removePendingNotificationRequestsWithIdentifiers:@[requestID]];
                [center removeDeliveredNotificationsWithIdentifiers:@[requestID]];
                return;
            }
            if (deliveryError && allowAttachmentFallback && deliveryError.code != UNErrorCodeNotificationsNotAllowed) {
                // One visible diagnostic outcome and one attempt, never a loop.
                zn_event(requestID, 7, (int)deliveryError.code, 0, auth);
                NSError *attachmentError = nil;
                UNNotificationContent *fallback = zn_fallback_content(entry, title, body, data, &attachmentError);
                if (fallback) {
                    zn_submit(entry, fallback, auth, NO, title, body, data);
                    return;
                }
                deliveryError = attachmentError ?: [NSError errorWithDomain:UNErrorDomain code:100 userInfo:nil];
            }
            if (deliveryError) {
                [zn_entries removeObjectForKey:requestID];
                zn_cleanup(entry);
            }
            zn_event(requestID, deliveryError ? 4 : 1, deliveryError ? (int)deliveryError.code : 0, (int)content.attachments.count, auth);
        });
    }];
}

__attribute__((visibility("default"))) int zn_install(ZNCallback callback) {
    // No helper identity or fallback fabricated bundle identifier.
    if (![NSBundle mainBundle].bundleIdentifier.length || ![NSThread isMainThread]) return 0;
    zn_callback = callback;
    if (!zn_entries) zn_entries = [NSMutableDictionary dictionary];
    if (!zn_delegate) zn_delegate = [ZNDelegate new];
    [UNUserNotificationCenter currentNotificationCenter].delegate = zn_delegate;
    return 1;
}

static int zn_send_internal(const char *identifier, const char *title, const char *body,
        const unsigned char *png, size_t length, BOOL decorate, const char *conversationID,
        const char *senderName, const char *groupName, const unsigned char *groupPNG, size_t groupLength) {
    if (!zn_delegate || ![NSThread isMainThread] || !identifier || !title || !body
            || length > 10 * 1024 * 1024 || groupLength > 10 * 1024 * 1024) return 0;
    NSString *requestID = [NSString stringWithUTF8String:identifier];
    NSString *requestTitle = [NSString stringWithUTF8String:title];
    NSString *requestBody = [NSString stringWithUTF8String:body];
    NSData *data = png && length ? [NSData dataWithBytes:png length:length] : nil;
    NSData *groupData = groupPNG && groupLength ? [NSData dataWithBytes:groupPNG length:groupLength] : nil;
    NSString *conversation = conversationID ? [NSString stringWithUTF8String:conversationID] : nil;
    NSString *sender = senderName ? [NSString stringWithUTF8String:senderName] : requestTitle;
    NSString *group = groupName ? [NSString stringWithUTF8String:groupName] : nil;
    if (!requestID || !requestTitle || !requestBody) return 0;
    void (^send)(void) = ^{
        ZNEntry *entry = [ZNEntry new]; entry.identifier = requestID;
        zn_entries[requestID] = entry;
        UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
        [center getNotificationSettingsWithCompletionHandler:^(UNNotificationSettings *settings) {
            dispatch_async(dispatch_get_main_queue(), ^{
                if (zn_entries[requestID] != entry) return;
                int auth = (int)settings.authorizationStatus;
                if (auth != UNAuthorizationStatusAuthorized && auth != UNAuthorizationStatusProvisional) {
                    [zn_entries removeObjectForKey:requestID];
                    zn_event(requestID, 4, UNErrorCodeNotificationsNotAllowed, 0, auth);
                    return;
                }
                UNMutableNotificationContent *base = [UNMutableNotificationContent new];
                base.title = requestTitle; base.body = requestBody;
                NSError *contentError = nil;
                UNNotificationContent *content = nil;
                BOOL decorated = NO;
                if (decorate && data.length) {
                    content = zn_decorate(base, data, requestID, conversation, sender, group, groupData, &contentError);
                    decorated = content != nil;
                    zn_event(requestID, 6, decorated ? 0 : (contentError ? (int)contentError.code : -1), 0, auth);
                }
                if (!content) {
                    if (decorate && data.length) zn_event(requestID, 7, contentError ? (int)contentError.code : -1, 0, auth);
                    content = zn_fallback_content(entry, requestTitle, requestBody, data, &contentError);
                }
                if (!content) {
                    [zn_entries removeObjectForKey:requestID];
                    zn_cleanup(entry);
                    zn_event(requestID, 4, contentError ? (int)contentError.code : 100, 0, auth);
                    return;
                }
                zn_submit(entry, content, auth, decorated, requestTitle, requestBody, data);
            });
        }];
    };
    // Register before returning to Qt, so an immediate close cannot be lost
    // ahead of a queued creation. Native send requires the main-thread boundary.
    send();
    return 1;
}

__attribute__((visibility("default"))) int zn_send(const char *identifier, const char *title, const char *body,
        const unsigned char *png, size_t length) {
    return zn_send_internal(identifier, title, body, png, length, NO, NULL, NULL, NULL, NULL, 0);
}

__attribute__((visibility("default"))) int zn_send_message(const char *identifier, const char *title, const char *body,
        const unsigned char *png, size_t length, const char *conversationID, const char *senderName,
        const char *groupName, const unsigned char *groupPNG, size_t groupLength) {
    return zn_send_internal(identifier, title, body, png, length, YES, conversationID, senderName, groupName, groupPNG, groupLength);
}

__attribute__((visibility("default"))) void zn_remove(const char *identifier) {
    if (!zn_delegate || !identifier) return;
    NSString *requestID = [NSString stringWithUTF8String:identifier];
    if (!requestID) return;
    void (^remove)(void) = ^{
        ZNEntry *entry = zn_entries[requestID];
        if (!entry) return;
        [zn_entries removeObjectForKey:requestID];
        UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
        [center removePendingNotificationRequestsWithIdentifiers:@[requestID]];
        [center removeDeliveredNotificationsWithIdentifiers:@[requestID]];
        zn_cleanup(entry);
    };
    // aboutToQuit already runs on the main thread. Do not defer its cleanup
    // until a future event-loop iteration that may never occur.
    if ([NSThread isMainThread]) remove();
    else dispatch_async(dispatch_get_main_queue(), remove);
}
