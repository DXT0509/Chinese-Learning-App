# White and mint aurora background

`core/designsystem/AuroraBackground.kt` renders the shared background for Login,
Registration and Home through the existing `FreshBackground` wrapper. Screen layouts,
navigation, authentication and backend behavior are unchanged.

The default theme now stays light even when the device uses night mode: white surfaces,
near-white #F7FCF8, mint mist #EEF9F1, light green #DCF4E4 and soft mint #CFEFDC.
Primary containers are lighter so cards do not compete with the background. Deep green
actions and #20352A text retain their contrasting roles. System bars use dark icons to
remain readable against the light background. Explicit dark theme previews still work.

The background combines a white/near-white base, three broad radial mint washes around
the edges, and a white radial wash near the reading area. Smooth transparent gradient
stops produce the appearance of blurred blobs without blurring text or creating blur
buffers. Positions are relative to the viewport; radii scale with its shorter edge for
portrait/landscape layouts.

Performance: brushes are created in `drawWithCache` and reused until size or palette
changes. Five simple gradient draws run behind the content. There are no images, external
libraries, RenderEffect/API-31 blur dependencies, offscreen layers, timers or continuous
animations. No additional per-frame work runs while the screen is idle. This is a design
choice, not a measured GPU/frame-time benchmark.

Verification: `testDebugUnitTest assembleDebug lintDebug installDebug` passed (18 JVM
tests, no failures). The updated app was installed on Samsung SM-A225F and the Login
background/system-bar contrast was visually inspected on the device. The shared wrapper
also applies the same background to Registration and Home; their individual flows were
not rerun for this visual-only change. Screenshot:
`android/app/build/reports/ui-review/aurora-background.png` (ignored build artifact).
