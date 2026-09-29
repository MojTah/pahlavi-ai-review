# پایگاه دانش تنظیم دقیق مدل‌های ترجمهٔ پهلوی

به‌روزرسانی: ۲۸ سپتامبر ۲۰۲۶. این بخش برای تصمیم‌گیری و استفادهٔ مجدد عامل‌های هوش مصنوعی است؛ دادهٔ آموزشی مدل ترجمه نیست.

**نتیجهٔ فعلی: آموزش کامل NLLB انجام شد، اما این مدل در مقایسهٔ کور از جِمای برگزیده بهتر نبود.** هر دو داور برای NLLB آموزش‌دیده صفر و برای جِما یک ترجمهٔ قابل‌قبول از ۱۵ مورد ثبت کردند. خطاهای جدی NLLB نیز بیشتر بود. یک خروجی آن به سقف طول رسید؛ آزمون رسمی از نظر تکمیل خروجی‌ها نامعین است و شرایط معنایی بهبود هم برقرار نیست. [گزارش و شواهد](../../experiments/nllb-supervised-20260928/REPORT.md).

**ورودی یکپارچهٔ داده‌ها:** [فهرست مرکزی](../../data/unified-corpus/README.md) اکنون متن‌های قدیمی، داده‌های تازه، کتاب‌ها و یادداشت‌های واژگانی را با منشأ و وضعیت جداگانه ثبت کرده است. مجموعهٔ کنترل همان ۲٬۲۳۷ جفت قبلی است؛ ۲۶٬۸۸۰ مورد نیازمند بازبینی‌اند. [بازبینی Gemini Pro](../../data/unified-corpus/GEMINI-REVIEW.md) انجام شد، اما پیشنهاد اصلی آن پس از بررسی مستقل داده‌ها تأیید نشد؛ تأیید معنایی کامل هنوز باقی است.

## چه چیزهایی باقی مانده؟

1. **بازبینی مستقل نتیجه انجام شد:** محاسبات، هویت خروجی‌ها و حفظ شکست‌ها تأیید شدند؛ [گزارش بازبینی](../../experiments/nllb-supervised-20260928/OUTCOME-QA.md). داوری هوش مصنوعی همچنان تأیید متخصص نیست.
2. **آزمون متن‌های آشنا تکمیل شد:** هر دو داور فقط ۲ ترجمه از ۲۰ مورد را پذیرفتند. هر پنج معنی واژگانیِ مستند حفظ شد، اما از ۲۳ بررسیِ ساختار جمله، داوران فقط ۲ و ۴ مورد را درست دانستند. مبدأ درست احتمال پاسخ مرجع را بالا برد؛ این معیارِ کیفیت ترجمه نیست. [نتیجهٔ کامل](../../experiments/nllb-seen-20260928/precision-repair/REPORT.md).
3. **قبل از آموزش، کل مجموعهٔ قابل‌اعتماد را آماده کنیم:** [جدول منابع](../../SOURCE-COVERAGE.md) و [بازبینی داده‌های کنارگذاشته‌شده](../../experiments/composition-evidence-20260928/RECOVERY-FOLLOWUP.md) مسیر تکمیل داده را مشخص می‌کنند. [شرط آمادگی داده](../../DATASET-READINESS.md) مقدم بر انتخاب مدل و روش بعدی است. PDF انگلیسی و فارسیِ [مکنزی](../../experiments/mackenzie-access-20260928/README.md) اکنون در دسترس است؛ دو عامل صفحات نمونه را بررسی کردند و تطبیق با سایت، تفکیک معنی‌ها و یک اصلاح چاپ دوم را تأیید کرد. نسخهٔ فارسی تصویری است و متن استخراج‌شدهٔ انگلیسی خطا دارد؛ استخراج کامل و تأیید داده هنوز انجام نشده است. سایت و کتاب یک ریشه دارند و نباید دو شاهد مستقل شمرده شوند. [هفت جملهٔ چاپ‌شده](../../experiments/composition-evidence-20260928/README.md) هم فقط نامزدند. دادهٔ معتبر انگلیسی می‌تواند نامزدِ آموزش کمکیِ جداگانه باشد؛ آن را خودکار ترجمهٔ معیار فارسی ننامیم. با هر افزودهٔ کوچک آموزش را تکرار نکنیم.
4. **تمرکز فعلی فقط کیفیت داده است:** دانلودهای سایت با چت دیگری است. [یکدست‌سازی جدید](../../experiments/kosh-quality-20260928/README.md) ۴۲٬۹۰۴ رکورد را حفظ کرده: ۲۶٬۳۷۷ گروه واژه‌ـ‌معنی برای بازبینی، ۹۰۳ ردیف تکراریِ ادغام‌شده و ۱۵٬۶۲۴ مورد جداشده. هر ۳۸٬۶۸۶ شناسهٔ اعلام‌شده در فهرست کوش دریافت شده و همهٔ فیلدهای اصلی و XML حفظ شده‌اند. رکوردهای نسخهٔ قبلی تغییر نکرده‌اند؛ تطبیق شمار داده، تأیید درستی معنا یا آمادگی آموزش نیست. نسخهٔ قدیمی مکنزی تا روشن‌شدن کدگذاری و ارتباط نسخه‌ها جدا می‌ماند. [عامل اختصاصی](../../experiments/kosh-quality-20260928/AGENT.md) باید ابتدا از Gemini Pro یا بالاتر استفاده کند و کیفیت، انتساب و هم‌پوشانی را بررسی کند؛ دادهٔ آموزش هنوز همان ۲٬۲۳۷ جفت است.
5. **حفظ شرط کیفیت برای تحویل:** جِمای مرحلهٔ ۲۸۰ مدل مرجع می‌ماند. آزمون PAL-REF و انتقال وزن‌ها به رایانه فقط پس از عبور نامزد از معیارهای تعیین‌شده دنبال شوند. سقف هزینهٔ تجمعی ۲۵ دلار و اعتبار موجود است؛ هر اجرای تازه بررسی زندهٔ بودجه لازم دارد.


داده‌ها هنوز تأیید کامل متخصص زبان پهلوی ندارند. خواندن خط اصلی، رمزگشایی واژه‌های ناشناخته و کیفیت/زمان اجرا روی رایانهٔ ۸ گیگابایتی هم اثبات نشده‌اند. این‌ها با موفقیت در ترجمهٔ آوانویسی خودبه‌خود حل نمی‌شوند.

## راهنمای استفاده برای عامل بعدی

| نیاز | مرجع |
|---|---|
| وضعیت و تصمیم فعلی | [وضعیت پروژه](../../PROJECT_STATE.md) و [راهبرد پژوهشی](../../output/research-next-step-20260928/REPORT.md) |
| چگونگی تنظیم دقیق هر مدل و تنظیمات حل‌نشده | [MODEL-RECIPES.md](MODEL-RECIPES.md) |
| شواهد موافق و مخالف و دلیل کنارگذاشتن گزینه‌ها | [EVIDENCE-AND-DECISIONS.md](EVIDENCE-AND-DECISIONS.md) |
| نتیجه و دامنهٔ بررسی سازگاری NLLB | [گزارش آمادگی](../../experiments/nllb-feasibility-20260928/README.md) و [بازبینی مستقل](../../experiments/nllb-feasibility-20260928/REVIEW.md) |
| تعریف ثابت کیفیت ترجمه | [قرارداد ارزیابی](../../experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json) و [پروتکل PAL-REF](../../benchmarks/pal-reference-v1/PROTOCOL.md) |

### Agent operating notes

- Read this index, the relevant model recipe, and its linked experiment before proposing a run. Actual artifacts and current user instructions override this summary.
- Separate **LOCAL EXECUTED**, **PRIMARY EXTERNAL**, **PROPOSED**, and **OPEN** evidence. A paper in another language is a rationale for testing, not a measured Pahlavi improvement.
- Keep model, representation, training objective, adaptation method, data selection, decoding and evaluation as separate decisions. Change only the factors named in the experiment. Our next comparison selects an attainable system; it does not isolate a causal architecture effect.
- Reuse valid checks and existing qualified data. Repeat a check when its inputs, implementation or relevant environment change. Do not rerun training merely to reconstruct recorded history.
- Preserve the benchmark and uncertainty labels. Do not copy held-out answers or reviewer corrections into training or a retrieval store. Repeated DEV/PAL evaluation is development evidence, not a fresh independent test.
- After a verified result, update the applicable recipe/status and cite its dated artifact. Preserve failed recipes and superseded decisions with their scope. Recheck mutable API, provider and model documentation before execution.
- This KB authorizes no cloud spending, credential changes, uploads, email or Drive actions. It contains references and methods, not credentials or model weights.

The current checkpoint uses Classic + Critic, with root as the integration/documentation writer and separate fresh semantic reviewers. The trained pilot and comparison have their own linked evidence; documentation does not authorize another job. The separate NLLB compatibility checkpoint has its own independent Critic record. Existing Markdown and linked experiment records cover the present need; no database, retrieval service or new dependency is required.

Documentation review: `/root/finetuning_kb_research` checked the model/method distinctions, paper claims and remaining gates. Its required correction was the then-stale linked independent-review status; the feasibility README/REVIEW now record the distinct final critic's result. Root also corrected the Aycock paper title against the primary source. This review does not validate an executable training recipe.
