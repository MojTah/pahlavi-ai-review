# Targeted online dictionary checks

28 September 2026. The user requested checking uncertain words against the original online dictionary. Four bounded public REST queries were performed with the existing rate-limited archive helper; no credentials or paid services were used. Exact responses and retrieval timestamps are bound in online-crosschecks.json and sources/local/public-texts-2026-09-20/kosh-targeted-crosscheck-20260928/manifest.json.

- GBD489, kištan: the live sense is کاشتن، کِشتن, exactly matching the archived XML. The vowel mark and accompanying synonym support the cultivation reading; an unvowelled Persian spelling must not be turned into an unsupported killing sense.
- DMX853, kištan: the exact wildcard pattern returned no record. A single bounded *kištan* follow-up found the archived entry with surrounding whitespace and the same کاشتن، کشتن sense. An empty exact-pattern result was not treated as absence of the word or permission to invent a correction.
- GBD14–16, ahrav: all three live XML entries equal their archived versions. GBD14 gives the single-word righteous/pious sense, while GBD15–16 combine a short form with longer kingship/harming phrases. The live website therefore confirms that the questionable form-to-phrase association exists in the source, rather than resolving it. Both compound records retain their holds pending printed source-layout evidence.

These are live checks of the same source lineage, not independent corroborating editions. They establish download fidelity for five returned entries, not universal dictionary correctness. When a source remains ambiguous, retain its meanings and uncertainty rather than choosing a convenient target.

The web text tool could not retrieve the landing page/API URLs, while the publisher's ordinary public JSON API worked through the existing archive helper. No access restriction or authentication was bypassed.
