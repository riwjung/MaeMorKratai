# Owner review — 2026-10-26

Owner-only `/review` and `/api/review` extend the existing workshop. Development source is imported at operation time from the private intake directory, never embedded in source/static assets. Original readings and audio are untouched. The 20 holdout answers are not imported into review; their original intake notebook remains in the existing workshop.

Persistence uses a separate **private Supabase Storage bucket `workshop-review`**, not SQL tables. No public/authenticated storage policies are added. The server verifies active membership and owner role before accessing service-role storage; documents are scoped to that authenticated owner's ID. The audio player uses the existing protected audio endpoint. No raw source is shipped to Vercel build/static files.

Each owner has `manifest.json`, `case-ID/source.json`, `style/source.json`, and immutable `*/revisions/00000001.json` records. Each revision includes source SHA-256, exact edited content, status, request UUID, authenticated reviewer ID, server timestamp and revision. Storage upload uses `upsert:false`; a duplicate revision is a conflict rather than last-write-wins. A retried identical latest request is idempotent. Approved content edited and saved as draft loses current approved status while retaining old audit records. Last 100 revisions are displayed; all are retained.

Sources are fingerprinted and tied to the intake case version and original reading revision. The import checks development-only case IDs, 40 unique cases, original content equality with backup/live records, and style references; existing different source objects are never overwritten. Source imports are resumable; manifest is written last. There is no whole-import transaction. A future new source version requires an explicit versioned migration; do not overwrite signed-off sources silently.

Approval is case-specific reference approval, not automatically generalized card-rule approval or publication to customers. Style answers require every proposal to be addressed. No LLM call, training, or automatic production answer generation is added.

## Operations

```sh
../.venv/bin/python scripts/credentials.py run node scripts/import-review.mjs /absolute/private/intake-directory
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs backup /absolute/private/new-backup-directory
```

The backup helper now includes private review source/history for active members in `review/` and `manifest.reviewFiles` with byte sizes and SHA-256. The withdrawal purge also deletes review objects for that withdrawn reader. The portable export is not a transactional database/Auth backup.

## Verification

`npm test`, `npm run typecheck`, credential-injected production build, then `tests/check_review_hosted.py` with hosted Supabase. The script creates isolated synthetic owner/reader accounts, tests persistence, explicit approval, history, stale/concurrent writes, idempotency, CSRF, anonymous/reader rejection, private storage access denial, holdout rejection, unsaved-change guard and mobile layout. It only reads the real owner's packet/audio; it never approves or edits actual owner content. Temporary accounts and objects are removed in finally cleanup. Artifacts stay in private runtime.

Production: set `WORKSHOP_TEST_URL=https://maemorkratai-workshop.vercel.app` for the same test. Real iPhone listening/content review remains the owner's task.
