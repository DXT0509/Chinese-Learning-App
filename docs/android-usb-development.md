# Chạy ứng dụng qua USB trên Windows

Ứng dụng dùng FastAPI cổng 8000, PostgreSQL cài trực tiếp trên Windows và điện thoại
Android nối USB. Không cần Docker. Debug mặc định dùng `http://127.0.0.1:8000/`;
`adb reverse` chuyển cổng này trên điện thoại về máy tính. Không dùng địa chỉ emulator
`10.0.2.2` cho kết nối USB này. Bản release vẫn bắt buộc HTTPS.

## 1. PostgreSQL và cấu hình backend

Mở PowerShell tại thư mục gốc `ChineseLearningApp`. Đảm bảo dịch vụ PostgreSQL đã chạy.
Ví dụ kiểm tra PostgreSQL 18 cài tại đường dẫn mặc định:

```powershell
$pgBin = 'C:\Program Files\PostgreSQL\18\bin'
& "$pgBin\pg_isready.exe" -h 127.0.0.1 -p 5432
cd backend
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Chỉnh `backend/.env` để `DATABASE_URL` trỏ đến database phát triển hiện có, với đúng
tên người dùng, mật khẩu và cổng PostgreSQL. Không ghi thông tin thật vào tài liệu/Git.
Không tạo lại, reset hay xóa database đang dùng. Với database mới, tạo riêng bằng pgAdmin
hoặc `createdb` rồi cấu hình URL trước khi chạy migration.

Lần đầu cài backend hoặc khi cập nhật dependency:

```powershell
python -m venv .venv # chỉ khi chưa có .venv
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m pip install --no-deps -e .
```

Chỉ cần Alembic khi khởi tạo database hoặc có revision mới chưa áp dụng:

```powershell
.venv\Scripts\python -m alembic upgrade head
```

Thay đổi giới hạn mật khẩu và giao diện trong tác vụ này **không đổi schema**, không có
revision mới và không cần migration nếu database đã ở `0003_sessions_and_runs`.

## 2. Chạy FastAPI với tự nạp lại mã

Trong terminal backend, chạy:

```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log --loop app.core.event_loop:new_event_loop --log-config logging.json
```

Nếu cổng 8000 đang có backend cũ, dừng bằng Ctrl+C tại terminal đã chạy nó trước khi
khởi động lệnh trên. Không khởi chạy chồng nhiều API trên cùng cổng. `--reload` theo dõi
file Python trong thư mục backend; sửa schema/service Python sẽ được nạp lại. Khi đổi
`.env`, biến môi trường, dependency hoặc lệnh khởi động, dừng và chạy lại backend.
`python -m app` vẫn chạy được nhưng **không bật reload**: sửa Python sau đó phải restart.
Không đưa password/token vào log. Cấu hình trên tắt access log và dùng logger an toàn.

Terminal khác, kiểm tra đúng tiến trình đang chạy:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
$apiSpec = Invoke-RestMethod http://127.0.0.1:8000/openapi.json
$apiSpec.components.schemas.Credentials.properties.password | Select-Object minLength,maxLength
```

Kết quả phải là `minLength=6`, `maxLength=128`. Nếu vẫn thấy 12, đó là backend cũ/chạy
nhầm thư mục hoặc nhầm cổng, dù file hiện tại đã ghi 6. Rebuild Android không sửa được
validation trong tiến trình backend đang chạy.

## 3. Kết nối điện thoại, build và cài bản Android mới

Bật Developer options và USB debugging trên điện thoại, nối USB, chấp nhận khóa máy tính.
Từ **thư mục gốc**, mở terminal mới:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices -l
& $adb -d reverse tcp:8000 tcp:8000
& $adb -d reverse --list
cd android
.\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8000/'
& $adb -d shell am start -n com.example.chineselearningapp/.MainActivity
```

`-d` chọn một điện thoại USB. Nếu có nhiều thiết bị, thay bằng `-s <serial>` trong các
lệnh ADB và chọn đúng thiết bị khi cài qua Android Studio. Chạy lại reverse sau khi rút
cáp, khởi động lại điện thoại hoặc ADB. Đổi đường dẫn SDK nếu máy cài ở chỗ khác.

Phải build **và cài lại** khi sửa Kotlin, Compose, resource XML hoặc `DEV_API_BASE_URL`.
Chỉ sửa backend Python thì không cần build Android. Chỉ sửa UI thì không cần restart API.
`assembleDebug` chỉ tạo APK; nó không cập nhật ứng dụng đang cài trên điện thoại.
`installDebug` cập nhật ứng dụng, giữ dữ liệu hiện có; không cần uninstall/clear-data.

Trong Android Studio, dùng Gradle property `DEV_API_BASE_URL=http://127.0.0.1:8000/`
trong cấu hình Gradle hoặc `android/gradle.properties` cá nhân. Biến này là cấu hình
build, không phải một setting có thể đổi trong ứng dụng đang chạy.

## 4. Xác minh đăng ký 6 ký tự và phiên đăng nhập

Mở ứng dụng: chờ khôi phục phiên; tài khoản đã lưu sẽ vào Trang chủ, chưa đăng nhập
sẽ vào Đăng nhập. Nhấn Tạo tài khoản. Dùng email thử nghiệm chưa đăng ký, nhập mật khẩu
6 ký tự và nhập lại đúng mật khẩu. API hiện trả cặp session ngay khi đăng ký, nên thành
công sẽ vào Trang chủ, không yêu cầu đăng nhập thêm lần nữa.

- 5 hoặc 129 ký tự: lỗi ngay dưới trường mật khẩu, chưa gửi API.
- 6 hoặc 128 ký tự, email hợp lệ và xác nhận khớp: gửi API để đăng ký.
- Xác nhận không khớp: lỗi ngay dưới trường nhập lại.
- 401, 409, 422 hoặc 429 từ backend: thông báo riêng phía trên form.
- Mất kết nối: thông báo kết nối; không giả lập đăng nhập thành công.

Nếu form cho qua 6 ký tự nhưng máy chủ trả lỗi thông tin, kiểm tra lại OpenAPI tại bước 2.
Đăng xuất phải về Đăng nhập và Back không mở lại màn hình tài khoản cũ. Sau đăng nhập,
Back không trở lại form. Khởi động lại ứng dụng để kiểm tra phiên đã lưu/refresh.
Nếu mạng lỗi khi khôi phục phiên, ứng dụng giữ màn hình khôi phục với nút thử lại;
không chớp màn hình Đăng nhập hoặc tự xóa token còn có thể dùng.

Trang chủ hiển thị tên/email thật, nội dung API và phiên xem đã lưu. Chưa có nội dung
thì hiển thị trạng thái trống; không tạo XP, chuỗi ngày học hay bài đã hoàn thành giả.
Bài học vẫn chỉ xem trước. Bật `ALLOW_CONTENT_PREVIEW=true` ở backend và restart để mở
bundle; trên Android cần đồng ý xem trước. Các tính năng tương lai được ghi Sắp ra mắt.

## 5. Kiểm thử

Backend: dùng `TEST_DATABASE_URL` trỏ đến database test riêng đã migration, không phải
database phát triển cá nhân hay production. Các fixture API rollback dữ liệu của mình.

```powershell
cd backend # từ thư mục gốc
# Cấu hình TEST_DATABASE_URL cho database test PostgreSQL cài trực tiếp trên Windows.
.venv\Scripts\python -m pytest -q tests/test_sessions.py
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
cd ../android
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug
.\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.SessionNavigationTest' '-Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true'
```

Không có TEST_DATABASE_URL thì các test PostgreSQL bị skip; đó không phải bằng chứng
đăng ký thành công. UI tests trên chạy riêng lớp SessionNavigationTest với fixture giao diện,
không gọi auth thật hoặc xóa session của người dùng. Không chạy SessionVaultTest trên
điện thoại cá nhân đang có session cần giữ: test cũ đó xóa vault đích. Test UI không
thay cho kiểm thử API/PostgreSQL hay kiểm tra thủ công toàn bộ trải nghiệm thiết bị.

Test `AuthenticationIntegrationTest` là opt-in, chỉ nhận `test_api_base_url=http://127.0.0.1:8001/`.
Để chạy, mở API test riêng ở cổng 8001 với DATABASE_URL trỏ database test đã migration,
không trỏ database cá nhân. Tạo tài khoản test sẽ commit vào database test đó:

```powershell
# Terminal backend riêng; thay URL bằng database TEST của bạn trước khi chạy:
$env:DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/slice2_test'
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --no-access-log --loop app.core.event_loop:new_event_loop --log-config logging.json
```

Từ terminal Android, sau khi mở khóa điện thoại:

```powershell
& $adb -d reverse tcp:8001 tcp:8001
.\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.SessionNavigationTest,com.example.chineselearningapp.AuthenticationIntegrationTest' '-Pandroid.testInstrumentationRunnerArguments.test_api_base_url=http://127.0.0.1:8001/' '-Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true'
& $adb -d reverse --remove tcp:8001
```

Dừng API test bằng Ctrl+C khi xong; giữ API phát triển cổng 8000. Test dùng token RAM riêng,
không thay session vault thật. Runner có thể gỡ APK khi cleanup nếu không truyền property
giữ APK; có thể cần đăng nhập lại và chạy `installDebug` sau instrumentation. Kiểm thử
trên emulator/máy test riêng phù hợp hơn nếu cần giữ nguyên phiên cá nhân.
