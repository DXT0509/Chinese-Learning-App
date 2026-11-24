# Character structure reveal

The roadmap player reuses the shared tokens, MascotChatBar and PrimaryButton.
Entry shows the 96 sp serif word and no cards. Each Continue tap reveals exactly
one AVAILABLE component, in authored order, with a 350 ms fade and 24 dp upward
translation. The scroll area follows the new card; the header/footer remain fixed.
Reveal progress survives configuration recreation and is keyed by word/content and
lesson version. Mascot text changes for every component and for the mnemonic.

Cards show a 36 sp glyph and two single-line labels: name/role and a short cue
of at most ten words. Long explanations, notes, examples, assets, attribution and
expand/collapse controls are absent from this screen. Published content is unchanged.
The compact person/structural cues and optional 你 memory aid follow the supplied UI
copy. The memory aid is a mnemonic, not a claim about historical character origins;
it appears only for 你 with both authored 亻 and 尔 components. Other roles use short
generic cues. General lesson notes are never treated as mnemonic content.

After all components, a further tap reveals the optional two-line mnemonic. Without
a mnemonic, the last component is the final reveal. The final button reads
“Hiểu rồi, tiếp tục →”; only that button calls the existing acknowledgement handler.
With no components/mnemonic it is available immediately, with no empty extra steps.
Skip retains the existing whole-lesson confirmation. No new API or migration.

Build/unit/lint checks do not validate device animation, large-font layout or touch.
