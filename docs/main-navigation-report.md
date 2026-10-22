# Main navigation and Profile

The signed-in app now has four Material 3 bottom tabs: Trang chủ, Học tập, Ôn tập
and Hồ sơ. The existing bright white/mint aurora and theme remain shared with auth.
Material navigation items animate selection, use green indicators and have rounded
upper corners. Scaffold and NavigationBar handle content and system navigation insets.

## Navigation and behavior

- Authentication retains a separate Login/Registration graph without bottom navigation.
- The protected graph starts at Home and uses one controller. Tab switches save and
  restore state, pop to Home and avoid duplicate destinations. Back returns to Home.
- The preview catalog, vocabulary placeholder, health demo and existing lesson player
  remain detail routes. Bottom navigation appears only on the four main destinations.
- Home keeps its greeting, real catalog/run data, continue action and quick links.
  Its logout button and callback are removed. Its roadmap link opens Learning.
- Learning presents an empty roadmap state and working links to existing preview content
  and the health demo. Review presents an empty state without synthetic SRS counts.
- Profile shows the available account name and registered email, a generic avatar,
  existing unverified-email information and a noninteractive future settings notice.
- Profile owns the only logout action. Confirmation and cancellation use a saveable
  AlertDialog. Confirmation calls the existing SessionViewModel/SessionRepository
  logout path. Loading disables repeats; failures keep the session and show an error
  for retry. Successful logout clears session data through the existing implementation
  and discards the protected graph and saved tab history. Auth success opens Home.

## Files created

Paths below are relative to `android/app/src/` unless prefixed with `docs/`.

- `main/java/com/example/chineselearningapp/core/navigation/MainNavigation.kt`
- `main/java/com/example/chineselearningapp/core/navigation/MainBottomBar.kt`
- `main/java/com/example/chineselearningapp/core/designsystem/FeatureEmptyState.kt`
- `main/java/com/example/chineselearningapp/feature/learning/LearningScreen.kt`
- `main/java/com/example/chineselearningapp/feature/review/ReviewScreen.kt`
- `main/java/com/example/chineselearningapp/feature/profile/ProfileScreen.kt`
- `main/res/drawable/ic_home.xml`, `ic_person.xml`, `ic_review.xml` (Material icons)
- `main/res/values/main_navigation_strings.xml`
- `androidTest/java/com/example/chineselearningapp/MainNavigationTest.kt`
- `docs/main-navigation-report.md`

## Files modified

- `main/java/com/example/chineselearningapp/core/navigation/SessionNavigation.kt`
- `main/java/com/example/chineselearningapp/feature/home/HomeScreen.kt`
- `main/java/com/example/chineselearningapp/feature/profile/README.md`
- `test/java/com/example/chineselearningapp/SessionViewModelTest.kt`
- `androidTest/java/com/example/chineselearningapp/SessionNavigationTest.kt`
- `androidTest/java/com/example/chineselearningapp/AuthenticationIntegrationTest.kt`
- `docs/architecture.md`

Pre-existing working-tree changes, including the vocabulary player and backend changes,
were preserved. This task changes no backend contracts, database schema or dependencies.

## Validation and limits

Executed from `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug connectedDebugAndroidTest
```

- Build successful; debug APK assembled.
- 34 JVM tests passed with no failures.
- Physical Samsung SM-A225F (Android 12): 10 instrumentation tests passed, one skipped,
  no failures. The skipped test needs the isolated live authentication API.
- Lint: zero errors, 40 warnings (dependency update notices and unused resources).
- `git diff --check` passed for the changes.

The focused tests cover initial Home, all tab selections, duplicate selection and Back,
saved destination and Home scroll restoration, detail-screen navigation hiding the bar,
logout dialog restoration/cancellation/confirmation, protected-history removal,
Login/Registration hiding the bar, no Home logout, real account rendering and dark-mode
busy state. JVM tests cover repository logout execution, waiting for revocation,
duplicate suppression, error retention and retry. Existing repository/session tests run
alongside these checks.

Learning roadmap, SRS and account settings remain placeholders. Saved-state tests emulate
state recreation; they do not claim a full operating-system process-death exercise.
Live backend authentication is opt-in and requires an isolated test API on port 8001.
