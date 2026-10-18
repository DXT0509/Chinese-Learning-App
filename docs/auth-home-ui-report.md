# Báo cáo xác thực và giao diện Android — 2026-10-18

## Nguyên nhân mật khẩu 6 ký tự bị từ chối

Đã kiểm tra schema Pydantic, service đăng ký, ViewModel, form, resource và đường gọi API.
Mã nguồn backend và Android đều đã dùng 6–128; service không có điều kiện 12 ký tự khác.
Tuy nhiên, GET `http://127.0.0.1:8000/openapi.json` tại thời điểm bắt đầu vẫn trả
`Credentials.password.minLength=12`. Tiến trình được xác định là backend của chính dự án,
chạy qua `.venv\Scripts\python.exe -m app`, không bật reload. Đây là **mã backend cũ
còn trong tiến trình đang chạy**, không phải một rule 12 ký tự còn sót trong source.
Không suy đoán rằng mọi bản APK từng cài đều đã được cập nhật; APK mới đã được build/cài
trong lần thực hiện này.

Đã khởi động lại đúng backend dự án tại cổng 8000 bằng Uvicorn `--reload`, giữ cấu hình
database trong `.env`. OpenAPI trực tiếp sau restart xác nhận minLength=6, maxLength=128.
Không sửa hashing Argon2id, token, refresh, service auth, database schema hay migration.
Backend chỉ bổ sung test password boundaries và đăng ký/đăng nhập trên PostgreSQL.

Android dùng AuthValidation chung, đếm Unicode code point như Pydantic/Python. Lỗi email,
độ dài mật khẩu và xác nhận được hiển thị dưới từng trường. Lỗi backend 401/409/422/429,
sự cố máy chủ và lỗi kết nối dùng banner riêng; không hiện nội dung response thô.

## Giao diện và điều hướng

LoginScreen và RegistrationScreen có nhận diện trắng–mint, card/shape bo tròn, typography
chung, form email/mật khẩu, hiện/ẩn mật khẩu, xác nhận khi đăng ký, gợi ý 6–128 ký tự,
loading, xử lý keyboard Next/Done, focus và cuộn theo IME. Mọi thông báo dùng resource
tiếng Việt. Mật khẩu không vào SavedState/rememberSaveable; email có thể khôi phục.

HomeScreen có tên/email thật từ `/auth/me`, lời chào, Bắt đầu học, phiên xem đã lưu,
entry lộ trình và card Từ vựng/Ôn tập/Hồ sơ ghi Sắp ra mắt. Bài học/phiên xem lấy từ API;
không có XP, streak, mastery hay completion giả. Trạng thái trống và lỗi tải được phân biệt.
PreviewLessonsScreen giữ consent, phiên bản đã pin và checkpoint của Slice 2; không thêm
Scene Engine hoặc hoàn thành bài học. Health demo vẫn có qua Lộ trình.

SessionNavigation dùng hai graph độc lập cho SignedOut/SignedIn, keyed theo UUID người dùng.
Restoring và RestoreFailed được render riêng trước graph đăng nhập. Đăng nhập/đăng ký
thành công bỏ auth graph và mở Home. Logout thành công bỏ protected graph và trạng thái
riêng của tài khoản, rồi mở Login. Back không phục hồi nhóm màn hình cũ. Lỗi mạng khi
restore giữ token để thử lại; lỗi catalog không làm mất trạng thái đăng nhập thành công.
Token refresh/revocation vẫn dùng repository hiện có.

Palette light/dark được chỉ định trong MaterialTheme, không phụ thuộc màu động của máy.
Shared components đặt màu chữ mặc định theo theme kể cả dưới Scaffold trong suốt; gradient
dark là màu đục để không lộ nền sáng của window. Form và Home cuộn, không bố trí pixel cố
định; nút chính tối thiểu 56dp, toggle mật khẩu dùng IconButton theo Material. Animation
chuyển trang nhẹ. Chưa thực hiện đánh giá TalkBack đầy đủ hay kiểm tra mọi cấu hình thiết bị.

## Kiểm tra đã thực hiện

- Backend với PostgreSQL test riêng: **74 passed**, gồm 5/6/128/129 ký tự ở schema và
  đăng ký thật, login với password được chấp nhận, các kiểm thử session và Slice 1 hiện có.
- Android JVM: **18 passed**, gồm boundaries, Unicode, confirmation, backend errors,
  session restoration/retry, content failure, request idempotency, refresh và logout.
- Android `assembleDebug`, `lintDebug`, `assembleDebugAndroidTest`: đạt. Lint cuối cùng
  có 37 warning (resource không dùng và thông báo dependency mới), không có error.
- Đã xem ảnh Login, Registration và Home chế độ sáng từ thiết bị; Login chế độ tối
  cũng được xem trực tiếp để phát hiện/sửa màu chữ và gradient. Ảnh nằm trong
  `android/app/build/reports/ui-review/` (ignored). Home trong ảnh chế độ sáng dùng
  fixture kiểm thử, không phải dữ liệu cá nhân hay bằng chứng tiến độ học thật.
- Samsung SM-A225F, Android 12: **4 instrumentation tests passed** sau khi mở khóa màn hình.
  Ba ca kiểm tra restore/navigation/Back và lỗi dark mode. Một ca chạy registration với
  password **6 ký tự**, logout, login lại và logout qua FastAPI/PostgreSQL thật.
- Ca tích hợp thiết bị dùng API tạm cổng 8001, database test riêng và token store trong RAM;
  test không đọc hay ghi session vault thật. Không tạo tài khoản thử trong database phát triển.
- Đợt test đầu khi điện thoại khóa không tìm được Compose hierarchy; đã chạy lại sau mở khóa.
- Migrations không đổi nên không chạy lại nonempty migration rehearsal trong tác vụ UI này.
  Không tuyên bố đã kiểm tra toàn bộ trải nghiệm trên mọi máy, rotation hay process death.

Test database là `slice2_test` trong cluster test riêng, loopback 55432. Test API tạm và
cluster test được dừng khi hoàn tất; fixture test được giữ, không reset database. Backend
phát triển cổng 8000 với reload được giữ để sử dụng ứng dụng. Log/test build/screenshot
trong thư mục ignored, không đưa token/password vào báo cáo.

Android instrumentation runner có thể gỡ APK khi cleanup; dùng property
`-Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true` khi muốn giữ APK sau test,
hoặc chạy `installDebug` sau đó. Không dùng toàn bộ suite SessionVaultTest trên session cá
nhân cần giữ. Bản app cập nhật được cài lại để sử dụng sau kiểm thử.

## Tệp thay đổi

Tệp mới (đường dẫn Android Java dưới `android/app/src/main/java/com/example/chineselearningapp/`):

- `domain/model/AuthValidation.kt`
- `core/designsystem/FreshComponents.kt`
- `core/navigation/SessionNavigation.kt`
- `feature/auth/AuthScreens.kt`
- `feature/home/HomeScreen.kt`
- `feature/lesson/PreviewLessonsScreen.kt`
- `android/app/src/main/res/values/auth_home_strings.xml`
- `android/app/src/main/res/drawable/ic_visibility.xml`, `ic_visibility_off.xml`, `ic_arrow.xml`, `ic_book.xml`, `ic_path.xml`
- `android/app/src/test/java/com/example/chineselearningapp/AuthValidationTest.kt`
- `android/app/src/androidTest/java/com/example/chineselearningapp/SessionNavigationTest.kt`
- `android/app/src/androidTest/java/com/example/chineselearningapp/AuthenticationIntegrationTest.kt`
- `docs/android-usb-development.md`, `docs/auth-home-ui-report.md`

Tệp sửa:

- `feature/auth/SessionViewModel.kt`, `feature/auth/data/RemoteSessionRepository.kt`, `feature/auth/README.md`
- `domain/repository/SessionRepository.kt`, `core/network/SessionApi.kt`
- `ui/theme/Color.kt`, `ui/theme/Theme.kt`, `ui/theme/Type.kt`
- `android/app/src/main/AndroidManifest.xml`, `android/app/src/main/res/values/strings.xml`
- `android/app/src/test/java/com/example/chineselearningapp/SessionViewModelTest.kt`, `SessionRepositoryTest.kt`
- `backend/tests/test_sessions.py`
- `README.md`, `docs/architecture.md`, `docs/authentication.md`, `docs/development-guide.md`, `docs/slice2-verification.md`

Tệp cũ được thay bằng các component tách riêng: `core/navigation/AppNavigation.kt` và
`feature/auth/SessionScreen.kt`. Không thêm dependency UI, provider, migration hay schema.
Workspace không có Git metadata, nên không thể cung cấp Git diff/commit; không tạo commit.

## Chạy và giới hạn còn lại

Xem [hướng dẫn Windows/PostgreSQL/USB](android-usb-development.md) để có lệnh đầy đủ cho
backend, ADB reverse, build/cài Android, restart/reload, Alembic và kiểm tra OpenAPI.
Google Sign-In, xác minh email, khôi phục mật khẩu và các chức năng học đầy đủ vẫn nằm
ngoài phạm vi. Email chưa xác minh không chứng minh quyền sở hữu. Rate limiting backend
vẫn chỉ dành cho phát triển một process như đã ghi ở tài liệu Slice 2.

Tham chiếu Android chính thức: [focus và IME](https://developer.android.com/develop/ui/compose/touch-input/focus/focus-in-text-fields),
[window insets](https://developer.android.com/develop/ui/compose/system/insets-ui),
[conditional navigation](https://developer.android.com/guide/navigation/use-graph/conditional).
