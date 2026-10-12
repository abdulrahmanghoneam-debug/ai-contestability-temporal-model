# إمكان الوصول إلى تصحيح خطأ في قرار توظيف مؤتمت

حزمة حسابية قابلة لإعادة التشغيل لنموذج حالات منتهٍ يختبر وجود مسار إجرائي لتصحيح خطأ واقعي محدد، في حدود الزمن والميزانية وحفظ الأدلة وسلطة المراجعة المعلنة. الإصدار: **1.0.0**.

رابط المستودع المخصص للحزمة: [https://github.com/abdulrahmanghoneam-debug/ai-contestability-temporal-model](https://github.com/abdulrahmanghoneam-debug/ai-contestability-temporal-model).

تضم النتائج **34,560 إعدادًا مصطنعًا بالكامل**. لا تتضمن الحزمة بيانات أشخاص أو تجارب بشرية أو قياسًا لأداء نموذج لغوي. أعداد الوصول تخص فضاء المعلمات المختار؛ ليست احتمالات نجاح للمواطنين أو تقديرًا لانتشار مشكلة في مصر أو غيرها.

## التشغيل

تحتاج إلى **Python 3.10 أو أحدث**. جميع البرامج تستخدم المكتبة القياسية فقط، وتعمل دون اتصال بالإنترنت. نفذ الأوامر من جذر هذا المجلد:

```text
python -m unittest -v test_model test_audit
python run_study.py
python independent_audit.py
python audit_case.py --output audit_example.json
```

- الأمر الأول يشغل 13 اختبارًا. توجد نتيجة فحص نسخة النشر في [unit_test_summary.json](unit_test_summary.json) وسجله في [unit_test_output.txt](unit_test_output.txt).
- الأمر الثاني يعيد توليد الشبكة ذات 34,560 إعدادًا والجداول والرسمين وشهادات المسار. يفحص خوارزم الوصول انتقالات النموذج مباشرة، ثم يقارن النتائج بالتوصيف التحليلي.
- الأمر الثالث يفحص 1,500 إعداد إضافي من مجال أوسع وبذرة ثابتة 61792. هذا فحص إضافي للخوارزميتين اللتين تشتركان في تعريف النموذج، وليس برهانًا عامًا أو تحققًا من تمثيل الواقع.
- الأمر الرابع يشخص حالة مصطنعة ويعدد مجموعات الإضافات الدنيا بالاحتواء. لا يغير الزمن أو الميزانية ولا يقرر الإتاحة القانونية لتلك الإضافات.

تعيد أوامر الدراسة والفحص كتابة ملفات نتائجها؛ لذلك قد يلزم إنشاء بيان بصمات جديد إذا تغيرت الملفات بعد إصدار الحزمة. ملفات النشر في الجذر حفاظًا على أوامر التشغيل وتيسير رفع الحزمة؛ راجع [TESTING.md](TESTING.md) لتوثيق الاختبارات.

## النموذج والحدود

يتتبع النموذج الإخطار، والوصول إلى السجل، وطلب الدليل وحفظه، والإيداع، ثم مراجعة مخولة. يميز بين آخر موعد للإيداع، وآخر موعد لاستكمال المستندات، وأفق اكتمال المراجعة. الآليات الاختيارية هي إخطار يحدد الواقعة المتنازع عليها (`N`)، وحفظ مبكر للدليل (`P`)، وإيداع أولي قبل استكمال المستندات مع مهلة محددة (`F`)، وبدء ميعاد الإيداع من الإخطار بدلًا من القرار.

الزمن والتكلفة وحدات مجردة، وليسا أيامًا قانونية أو مبالغ مالية. التأخيرات يقينية داخل كل إعداد، ويمكن بدء أفعال متعددة في اللحظة نفسها؛ كل طلب أو إيداع أو حفظ يكلف وحدة واحدة. طلب الدليل لا يحفظ مصدره تلقائيًا. يفترض النموذج دليلًا أصيلًا كافيًا لإثبات الخطأ المحدد، واستمرار صلاحية النسخة المستلمة أو المحفوظة، وتصحيح المراجع المخول للخطأ المثبت بعد اكتمال المراجعة. لا يحاكي خلافًا في حجية المستند أو عدالة سياسة التوظيف. الإخطار المحدد يسمح بطلب الدليل مبكرًا؛ لا يمنح دليلًا خفيًا أو قدرة استدلالية إضافية.

تعني النتيجة وجود مسار ممكن داخل هذه الافتراضات، ولا تعني أن شخصًا حقيقيًا سيكتشفه أو ينجح في اتباعه. لا تقرر الحزمة مشروعية سياسة، أو اختصاص جهة، أو وجود حق إجرائي واجب التطبيق. يلزم التحقق المستقل من القانون والآجال والأدلة والسلطات قبل أي استعمال مؤسسي.

## النتائج المرجعية

تسجل المخرجات المحفوظة صفر اختلافات بين فاحص الوصول والتوصيف التحليلي على 34,560 إعدادًا، و10,075,168 حالة مستكشفة مجمعة، و69,120 مقارنة رتابة دون انتهاك. عند معامل التأخر `λ=1` واحتساب الميعاد من القرار، كانت أعداد الإعدادات التي تتيح الوصول إلى التصحيح كما يلي؛ لكل صف 720 إعدادًا:

| الآليات | عدد الإعدادات الممكنة |
|---|---:|
| الأساسي | 258 |
| N | 498 |
| P | 312 |
| F | 316 |
| NP | 530 |
| NF | 534 |
| PF | 427 |
| NPF | 573 |

في المجموعة نفسها مع غياب `N`، أتاح الجمع بين `P` و`F` الوصول في 57 إعدادًا لم يتيحه أيهما منفردًا. هذه خاصية للنموذج والمجال المصطنع المختار، وليست أثرًا سببيًا مقدرًا على بشر.

## محتويات الحزمة

- [model.py](model.py): الانتقالات، وفحص الوصول، والتوصيف التحليلي، وإعادة تشغيل الشهادات.
- [run_study.py](run_study.py)، [results.json](results.json)، [summary.csv](summary.csv)، [all_configurations.csv](all_configurations.csv): شبكة الدراسة ومخرجاتها.
- [witnesses.json](witnesses.json)، [audit_case.py](audit_case.py)، [audit_example.json](audit_example.json): أمثلة المسارات وتشخيص حالة واحدة.
- [independent_audit.py](independent_audit.py)، [independent_audit_results.json](independent_audit_results.json): الفحص الإضافي ببذرة ثابتة.
- [feasibility_counts.svg](feasibility_counts.svg)، [reachability_frontier.svg](reachability_frontier.svg): الرسوم المحسوبة.
- [README_ar.md](README_ar.md): نسخة محفوظة دون تعديل من دليل الحزمة الأصلية. بعض إشاراته إلى المخطوط و`package_sha256.json` و`legal_source_register.json` تخص التسليم الأصلي، وهي غير مدرجة في حزمة النشر هذه.
- [AI_USE.md](AI_USE.md): بيان استخدام الذكاء الاصطناعي والمراجعة البشرية التي أقر بها المستخدم.
- [MANIFEST_SHA256.json](MANIFEST_SHA256.json): بصمات جميع ملفات هذا الإصدار باستثناء البيان نفسه. أما [sha256_manifest.json](sha256_manifest.json) فهو بيان المخرجات الذي يولده برنامج الدراسة، وتغطيته أضيق.

هذا مستودع لمواد حسابية بحثية؛ لا يتضمن المخطوط أو بيانات المؤلفين الخاصة. لا تعني إتاحته قبولًا بمجلة أو اجتياز التحكيم، ولا يوجد ادعاء بمعرّف DOI. لم تُحدد رخصة لهذه النسخة؛ لا تُفترض منها رخصة مفتوحة أو أذونات إضافية لإعادة الاستخدام.

## English overview

Version 1.0.0 contains a finite-state reachability model for procedural correction of a specified factual error in an automated hiring decision. The preserved results cover **34,560 entirely synthetic configurations**; no personal records, human study, or language-model performance measurements are included. Python **3.10+**, standard library only. Run the four commands above from the repository root; the unit suite contains 13 tests.

Reachability is an existential property under explicit assumptions about deterministic delays, abstract costs, evidence validity and retention, deadlines, and an authorized reviewer who corrects a proven error. It does not measure actual user success, establish legal compliance, or assess hiring-policy fairness. Informative notice changes when the same evidence can be requested, without supplying hidden evidence. The repository makes no claim of journal acceptance, peer review, or a DOI. No license has been selected. AI assistance and the user-acknowledged human review are disclosed in [AI_USE.md](AI_USE.md).
