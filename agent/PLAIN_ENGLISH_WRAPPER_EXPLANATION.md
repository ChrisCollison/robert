# Plain-English Wrapper Explanation

This is an outline only. It is not the full teaching document.

## 1. What this companion does and does not do

ROBERT remains the scientific engine in this workflow. It is still the system that builds the models, evaluates them, produces the report, and determines the ROBERT score. The companion does not take over any of that scientific work. It sits alongside ROBERT as a helper layer whose job is to save, organize, and explain the outputs that ROBERT already produces.

The easiest way to think about the companion is as a wrapper around ROBERT results. After ROBERT runs, it produces a set of output folders and files. Those files contain the real evidence behind the reported result: model metrics, verification results, plots, warnings, and other details that help explain what happened in the run. The companion gathers those outputs into a saved run folder, turns the most important parts into organized data files, and then presents that material in a form that is easier to browse and discuss.

This matters because ROBERT answers the scientific question of how the model performed, but collaborators often also want a practical explanation of what may have driven that outcome. A chemist or model user may reasonably ask, “Why did I get this ROBERT score?” The companion is meant to help answer that kind of question without changing the meaning of the original ROBERT result. Its role is to point back to the evidence that ROBERT already produced and organize that evidence into a clearer explanation.

In other words, the companion is an explanation and organization layer, not a replacement model. It helps preserve a run so that later runs do not overwrite it. It collects the key evidence into files that can be reused by the interface. It builds a diagnosis summary that highlights likely reasons behind a strong or weak score. It can also present the results in a local screen where a collaborator can review the run, inspect supporting figures, and ask guided questions in plain language.

Just as importantly, it has clear limits. The companion does not replace ROBERT. It does not choose new models, rerank ROBERT outcomes, or reinterpret the science in a way that overrides ROBERT itself. It does not modify ROBERT’s training process, split strategy, verification tests, or scoring rules. It does not introduce a second score that competes with the official ROBERT score. When the companion shows score-related information, it is still referring back to ROBERT’s own scoring method and ROBERT’s own output files.

That boundary is important for trust. The value of the companion is not that it invents a smarter answer than ROBERT, but that it helps a user see the answer that is already present in ROBERT’s evidence. If a score is low because the model is weak, because the data set is small, because verification tests raised concerns, or because the chosen descriptors may not be capturing the chemistry well, the companion should help surface those clues. But those clues should still come from ROBERT outputs and from clearly labeled companion interpretations, not from an alternative scoring system.

The companion is therefore best understood as a teaching and navigation aid. It helps collaborators move from a finished ROBERT run to a more understandable explanation of that run. It makes it easier to preserve runs, compare evidence, and ask focused questions about what the score seems to reflect.

At present, this is a wrapper approach. ROBERT runs first, and the companion then reads and organizes the files that ROBERT produced. A possible future direction would be for ROBERT itself to export more of this information directly in machine-readable form, such as JSON files. That could make the handoff simpler, but it remains a future possibility rather than a current feature.

So the short version is this: ROBERT remains the scientific authority. The companion exists to help people learn from ROBERT more easily by saving the run, organizing the evidence, and helping explain questions such as “Why did I get this ROBERT score?”

## 2. The 4-step workflow collaborators follow

With that role in mind, the companion workflow is easiest to follow as four practical steps. These steps do not add a second scientific process on top of ROBERT. They simply make a ROBERT run easier to save, review, and explain.

1. Run ROBERT and save the run.

The first step is simply to run ROBERT in the normal way and then save that run in a separate archived folder. This matters because ROBERT writes its main outputs into fixed folders. If a new run is started later, those folders can be overwritten. By saving each run into its own folder, the companion makes sure that a specific result can still be revisited later. For the user, this means that a good, bad, or puzzling ROBERT result does not disappear when the next experiment is launched. It also means that collaborators can return to the exact same run when they want to discuss what happened.

2. Extract and organize the important evidence.

Once the run has been saved, the companion reads the most important ROBERT output files and reorganizes them into a smaller set of companion files that are easier to use later. The purpose of this step is not to change the scientific content. It is to gather the key evidence into one place. That evidence includes things like performance measures, verification results, warnings, and report-related material. Some of this information is saved into JSON files. A JSON file is simply a structured text file that stores information in an organized way. For the user, this step means that the important pieces of the ROBERT run no longer have to be hunted down across many different output files.

3. Create a diagnosis summary.

After the evidence has been organized, the companion creates a diagnosis summary. This is the step where the workflow moves from raw output toward explanation. The diagnosis summary does not replace the ROBERT report, and it does not invent a new score. Instead, it gathers the most relevant clues and presents them in a more readable form. For example, it is intended to highlight whether the score seems to be connected to limited data, weak model behavior, verification concerns, or other patterns already visible in the ROBERT outputs. For the user, this step means that the run is no longer just a collection of files. It becomes something closer to a readable case summary.

4. Open the local app and ask questions.

The final step is to open the local app and review the run in an interactive way. The app loads one saved run at a time and shows the organized evidence, the diagnosis summary, and supporting figures. It is meant to give collaborators a practical way to move through the result without reading every raw file by hand. This is also the point where a user can ask direct questions, including guided questions such as why a score may be high or low. In that sense, the app is not the scientific source. It is the place where the saved ROBERT evidence is made easier to explore.

Taken together, these four steps describe the real role of the companion. First, preserve the run. Second, gather the important evidence. Third, build a readable explanation layer. Fourth, let the user inspect that material and ask focused questions. For a collaborator, the benefit is practical: the scientific authority remains ROBERT, but the path from ROBERT output to human understanding becomes much easier to follow.

## 3. What files are created and why they matter

Once the companion workflow has processed a ROBERT run, it produces a small group of files and folders that make the run easier to revisit, explain, and share with collaborators. Each one has a different job: some preserve the run history, some gather evidence into a more usable form, and some turn that evidence into a readable explanation.

Several of these files end in `.json`. In this document, a JSON file simply means a structured file that software can read reliably. You do not need to read those files directly in order to use the companion, but it is helpful to know what role each one plays.

Here is the simplest way to think about the main companion outputs:

| File or folder | What it is for in plain English |
|---|---|
| `run_manifest.json` | A record of how the run was saved. It helps answer basic questions such as which dataset was used, what was archived, and what report files were found. |
| `run_context.json` | The main organized evidence file for the companion. If you want one file that represents the core facts of the run for later explanation, this is the closest thing to that. |
| `llm_evidence.json` | A version of the evidence prepared for question-answering and explanation tools. Its purpose is to keep the explanation grounded in ROBERT outputs. |
| `dataset_profile.json` | A compact summary of the data set and curation context, when available. This can help explain whether the data itself may have influenced the score. |
| `diagnosis.json` | A structured version of the interpretation layer. It holds explanation-oriented observations in a form that software can reuse. |
| `diagnosis_summary.md` | A human-readable summary of the diagnosis. This is closer to something a collaborator would actually want to read. |
| `llm_run_bundle/` | A portable package of the key companion evidence files gathered together in one place. |
| `report_assets/` | A saved copy of the ROBERT report PDF and related report-viewing material for that run. |

It is worth pausing on why these are separate instead of being one large file. The reason is practical: different parts of the workflow need different kinds of outputs. Keeping those roles separate makes the workflow easier to manage without changing the original ROBERT results.

`run_manifest.json` matters because it anchors the run in time and context. If someone asks, “Which run was this?” or “Was the report saved with it?” this file helps answer that. It is less about interpretation and more about preserving the identity of the run.

`run_context.json` is the main evidence file for the companion layer. It gathers together the key results that were extracted from ROBERT outputs. If the companion were trying to explain a score, this is one of the main places it would look first. For a collaborator, the importance of this file is that it reduces many scattered run outputs into one organized reference point.

`llm_evidence.json` serves a related but slightly different purpose. It prepares the evidence in a form that explanation tools can use while still staying tied to ROBERT outputs. In plain terms, it helps the companion answer questions without drifting away from the source material.

`dataset_profile.json` adds context about the data set itself. This is useful because a ROBERT score is not only about the model. It can also reflect the size, shape, and quality of the available data. That said, this file is not present for every archived run. In the current archive, some older or earlier runs do not include every newer companion file, and `dataset_profile.json` is one of the clearest examples of that. So collaborators should not assume that every run will have the same level of supporting context.

The two diagnosis files work together. `diagnosis.json` stores the interpretation layer in a structured form that the app can reuse. `diagnosis_summary.md` turns that same general material into a readable summary. If a collaborator wants the easiest explanation-oriented entry point, `diagnosis_summary.md` is usually closer to that role than the more structured files.

`llm_run_bundle/` and `report_assets/` are useful because they help preserve the run as something more portable and reviewable. The bundle gathers the key companion evidence together, while the report assets keep a saved copy of the report material for that run. Together, they make it easier to revisit the run later without depending on the original top-level ROBERT output folders still being untouched.

The main idea is simple: these files exist so that a ROBERT run can be preserved, understood, and discussed more easily. They do not replace the original ROBERT outputs. They sit alongside them and make them easier to use. For chemistry collaborators, the practical takeaway is not that they need to memorize every file name, but that the companion creates a small set of organized records: one to identify the run, one to gather the main evidence, one to support explanation, one to summarize the diagnosis, and a few supporting folders to preserve the report and portable run materials.

## 4. How the UI helps explain a ROBERT score

The local app is a browser-based viewing and question-answering tool. It is built with Dash, which is simply the Python tool used to make the local browser app. A collaborator opens the app in a browser, chooses one archived ROBERT run, and then uses that run as the basis for review and discussion.

This step matters because it turns a saved ROBERT run into something you can inspect without reading every file by hand. The app does not change the run itself. It reads the structured files from the companion workflow and presents them in a way that is easier to follow. In practical terms, it gives you one place to look at the score, the supporting evidence, and the main clues about what may have driven the result.

When a run is selected, the app shows the information that matters most for interpretation. That includes metrics, plots, warnings, diagnosis text, and evidence from that run. The plots and evidence help show what ROBERT did well or poorly, while the warnings and diagnosis text help point toward likely reasons behind the score. If the companion has a dataset profile for that run, the app can also show that extra context so the collaborator can see whether the data itself may have influenced the result.

The app is especially useful for answering the kinds of questions collaborators naturally ask after a ROBERT run. For example:
- Why did I get this ROBERT score?
- Did VERIFY tests pass?
- Are there outliers?
- What features mattered?
- What should I inspect next?

Those questions are not answered by guesswork. They are answered by looking back at the saved evidence from the run and the summary files created by the companion. The app brings those pieces together so the user can move from a result to a reason. That is the main value of the browser view: it connects the number shown by ROBERT to the evidence behind it.

The app also helps the user decide where to look next. If the score seems weak, the user may want to inspect verification results, outliers, or the features that mattered most. If the score looks strong but there are warning signs, the user may want to inspect the diagnosis text or the plots more closely. If the run seems incomplete, the app can make that visible too. In other words, the app is not just a display screen. It is a guided starting point for interpretation.

All of this depends on the structured files described in Section 3. The app reads those files so it can show a run in a consistent way from one archived result to the next. That is why the earlier files matter: they are the bridge between the raw ROBERT outputs and the browser-based explanation experience.

The short version is that the local app helps a collaborator ask, “What happened in this ROBERT run, and what should I look at first?” It does that by showing the saved evidence in one place and by making the questions easier to answer in plain language.

## 5. What safety checks are in place before chat answers

The app should not simply let the AI answer freely from memory. That would be risky, because a free-form answer could drift away from what the ROBERT run actually showed. The companion is designed to do the opposite: it should stay tied to the saved ROBERT evidence and use that evidence first. That is why this layer is evidence-first. The goal is not to guess the answer. The goal is to answer from the run itself.

In practice, the app first tries to answer from the structured ROBERT evidence files. Those files hold the organized version of the run: the metrics, warnings, diagnosis notes, and other details that were copied from the ROBERT outputs. If the app can answer from those files, it stays close to the original run and keeps the explanation grounded in evidence rather than memory or broad language model habits.

Before the app trusts those copied values, it does a simple match check to make sure the copied values still agree with the original ROBERT files. In plain language, this is a match check to make sure the copied values still agree with the original ROBERT files. That check matters because the companion depends on accurate copying. If the copied values no longer match the source, then the explanation may be based on the wrong evidence.

If that check fails, the app should not trust the chat answer for that run. It is better to stop than to explain a result from mismatched or incomplete evidence. This is a deliberate guardrail. The companion is trying to protect the collaborator from a confident but unreliable explanation. When the evidence does not line up, the safest action is to treat the run as not ready for trusted chat answers.

This is also why the companion layer is evidence-first. It does not treat the chat as the source of truth. It treats the ROBERT outputs and the copied evidence files as the source of truth. The chat is only useful when it can stay anchored to those files. If the files do not agree, the chat should not be treated as dependable for that run.

There is one more important point. The checking process is not yet complete across all run types. The current workflow already includes checks, and those checks are active in the UI flow. But systematic checking across every kind of archived run still needs to be completed. That means the basic safety idea is already in place, but the full coverage still needs to be finished and confirmed across the full set of run situations.

For collaborators, the practical takeaway is simple. The companion does not let the AI speak first and hope for the best. It asks the evidence to lead. It checks that the evidence still matches the ROBERT files. And if the match is not good enough, it refuses to trust the answer for that run. That makes the companion safer, more honest, and more useful for explaining ROBERT results.

## 6. What is optional: OpenAI and local knowledge documents

The core companion workflow is based on saved ROBERT evidence, not on the AI model’s memory. That is the most important thing to remember about the optional features. The companion is already built to read the run-specific evidence files first. Everything else is there to add help, not to replace that evidence.

OpenAI support is optional and only used if it has been configured. If it is turned on, the AI language model that writes the explanation can help turn the saved ROBERT evidence into clearer wording. It can make the explanation easier to read, but it should not be treated as the source of truth. The source of truth is still the ROBERT run and the companion files created from that run.

The local knowledge documents are also optional. These are background notes and documentation that can help the companion give a better explanation of ROBERT language. A simple way to think about local knowledge lookup is: searching a local set of ROBERT notes or documentation for helpful background explanation. This can be useful when a collaborator wants a reminder of what terms like VERIFY, PFI, outliers, or ROBERT score language mean in practice.

Used well, local knowledge lookup can give the explanation a little more context. For example, it may help the app explain why VERIFY matters, what PFI means in a general sense, or why outliers deserve attention. It may also help the companion use smoother language when discussing the score. But it should still support the run-specific evidence, not replace it. If the saved evidence from the actual ROBERT run says one thing, that evidence matters more than any general background note.

That boundary is important. Local knowledge is background material, not the run itself. It can help a collaborator understand the language around ROBERT, but it cannot stand in for the run-specific files that show what happened in this exact case. The companion should always start from the saved evidence from the run and use local notes only as extra support.

RAG, in this context, is just a way of using local background material to help the explanation. It can be helpful, but its usefulness still needs to be tested. The team still needs to confirm how well this background lookup helps in real runs and whether it consistently improves the explanation without distracting from the evidence. So the right way to think about it is: optional support, not guaranteed magic.

For collaborators, the practical message is simple. If OpenAI is not configured, the companion can still work from saved ROBERT evidence. If local knowledge documents are not present, the companion can still explain the run. If both are available, they may make the explanation smoother and easier to read. But in every case, the saved ROBERT evidence remains the foundation.

## 7. What is already validated

Several parts of the companion workflow have already been shown to work in this repository. The most important point is that the workflow is not just a plan on paper. It already produces useful run files, opens them in the local app, and turns them into explanations that collaborators can read.

One clear sign of that progress is that several archived ROBERT runs already have the core companion files. That means the workflow has been able to save runs, organize the important evidence, and keep those runs in a form that can be reviewed later. It does not mean every possible run situation has been covered, but it does show that the main path is working for real archived runs.

The local app can also read saved run files and show organized evidence. In practical terms, that means a collaborator can open a saved run and see the key results in one place instead of digging through the original ROBERT folders by hand. The app is already able to use the saved evidence to present a readable view of the run, which is the central goal of the companion.

The companion can also produce diagnosis files for processed runs. That matters because the diagnosis step is what turns the raw evidence into a more readable explanation. It gives the collaborator a summary that can be used in the app or read on its own. In other words, the workflow does not stop at saving files. It can also turn those files into a more useful explanation layer.

Local knowledge indexing has also been run successfully. That shows the optional background-document feature can be built and used when needed. At the same time, its value for answering real questions still needs to be evaluated. It may help with explanations, but the team still needs to confirm how much it improves the actual answers and whether it stays clearly secondary to the saved ROBERT evidence.

Taken together, these results show that the companion already has a working core. It can save runs, organize evidence, open that evidence in the app, and create diagnosis files for processed runs. It can also build local knowledge support when that is useful. What has not been shown is that every possible ROBERT run type behaves the same way, so the validated part should be understood as the main workflow path, not as a claim that every edge case has been exhausted.

For collaborators, the practical message is simple: the companion already works well enough to preserve and explain several real ROBERT runs, and that is the part most people will use first.

## 8. What still needs testing

The companion already has working pieces, but it still needs broader testing before it should be treated as generally reliable. That is a normal stage for a workflow like this: the main path can work, while the team still checks how it behaves across more kinds of runs and more kinds of questions.

One important next step is to run the match-checking process systematically across saved runs. In plain language, this means checking that the copied values still agree with the original ROBERT files across a wider set of archived runs, not just a few examples. That broader check matters because the companion depends on reading values from ROBERT’s text output files correctly. If that reading step is wrong or incomplete, the explanation can be less trustworthy.

The workflow also needs more testing across different kinds of ROBERT runs. That includes regression and classification runs, PFI and No-PFI cases, weak and strong scores, runs with missing files, and runs that use external test sets. Those are all important because a companion that works for one run type may still behave differently when the run changes. The goal is not to prove that every edge case is perfect, but to make sure the main companion story holds up across the kinds of runs collaborators actually use.

Local knowledge lookup also still needs to be evaluated. It may help the companion explain terms and concepts more clearly, but the team still needs to see whether it actually improves answers in practice. The right test here is not just whether the feature runs, but whether the answer becomes more helpful, more accurate, and easier to understand for a collaborator.

Another practical issue is that early archived runs may lack newer companion files such as `dataset_profile.json`. That does not mean those runs are broken; it simply means the workflow has grown over time, and older runs may not include every newer supporting file. The testing plan should take that into account so that the absence of newer files is treated as expected for some older runs, not as a failure in itself.

It is also important to compare the companion’s answers against expert judgment. A small set of test questions should be enough to start with, such as questions about the score, VERIFY results, outliers, and the features that mattered most. The answers from the companion should be checked against what an experienced ROBERT user or chemistry collaborator would say after reviewing the same run. That kind of comparison is valuable because it shows whether the companion is giving a sensible explanation, not just a fluent one.

In short, the companion has already proven useful, but it still needs wider testing before the team should rely on it broadly. The next round of testing should cover more run types, more file patterns, more questions, and more comparisons with expert judgment. That will give collaborators a better sense of where the companion is strong, where it needs refinement, and how much trust they can place in its explanations.

## 9. Practical limitations today

This is a working companion prototype, not yet a polished public tool. It already helps preserve runs, organize evidence, and support explanations, but it is still being grown and refined for broader use. That means collaborators should treat it as a useful working layer rather than a finished product that can do everything in every situation.

One practical limitation is that the companion currently works around ROBERT by reading ROBERT’s saved output files after the run. That is a sensible choice because it avoids changing ROBERT itself. It lets the companion stay separate from the scientific engine and build explanations from the outputs ROBERT already produced. At the same time, this approach is less ideal than having ROBERT write more of the structured files directly. A direct export from ROBERT would be cleaner, simpler, and less dependent on copying values after the fact.

Another limitation is that the app currently runs locally, not as a hosted public website. That is useful for privacy and for keeping the workflow close to the person reviewing the run, but it also means the companion is not yet a shared online service that anyone can open from a browser. For now, it is best understood as a local working tool for the project team and nearby collaborators.

OpenAI use is also optional and depends on configuration. If it is not configured, the companion can still work from saved ROBERT evidence. If it is configured, it can help make the explanation more natural to read. The optional nature of this feature is helpful, but it also means the experience can differ from one setup to another. Some users may have the AI wording support turned on, while others may rely entirely on the saved evidence and the local app.

Early archived runs may not include every newer companion file. That is not unusual for a workflow that has grown over time. The older runs may still be perfectly useful, but they may not have later additions such as newer dataset context files. Collaborators should therefore expect a mix of run formats across the archive instead of assuming that every run will look exactly the same.

Local knowledge lookup is promising, but it still needs evaluation. It may help the companion explain terms and background ideas more smoothly, especially when a collaborator wants a reminder about ROBERT language or common result patterns. But it is still a support feature, not the main source of truth, and the team still needs to judge how useful it is in real answers.

The practical takeaway is that the companion already does something valuable, but it still has the feel of a project tool rather than a finished product. It is strongest when it stays close to saved ROBERT evidence and uses its optional features only as support. It is less strong when asked to stand in for ROBERT, replace the original outputs, or behave like a fully packaged public service. That is not a failure; it is simply the current stage of the work.

## 10. One-page glossary

**Companion layer**  
The companion layer is the extra set of tools and files that sit alongside ROBERT. It saves the results, organizes the evidence, and helps explain what the ROBERT run seems to show.

**Wrapper**  
A wrapper is a layer that works around an existing tool without replacing it. In this workflow, the wrapper reads ROBERT’s saved outputs after the run and builds explanation materials from them.

**JSON**  
JSON is a structured file that software can read reliably. The companion uses JSON files to store run information in a way that is easier to reuse later.

**Structured evidence**  
Structured evidence is the organized version of the important ROBERT results. It is the saved material the companion uses when it explains a run.

**.dat file**  
A `.dat` file is one of ROBERT’s text output files. These files hold the raw run details that the companion reads when it builds the saved explanation files.

**Diagnosis file**  
A diagnosis file is a companion file that turns ROBERT evidence into a more readable explanation. It helps show what may have driven the score and what to look at next.

**Local app**  
The local app is the browser-based tool used to view a saved ROBERT run and ask questions about it. It runs on the user’s own machine rather than as a public website.

**Dash**  
Dash is the Python tool used to make the local browser app.

**OpenAI**  
OpenAI is the optional AI support used for wording when it has been configured. It can help write or polish the explanation, but it is not the source of truth.

**LLM**  
LLM means the AI language model that writes the explanation. It can help turn saved ROBERT evidence into clearer language when that feature is turned on.

**Local knowledge documents**  
Local knowledge documents are notes or documentation saved on the computer for background help. They can give the companion extra context about ROBERT language, but they should not replace the saved run evidence.

**RAG**  
RAG is a way of using local background material to help answer a question. In this workflow, it means the companion can look at saved notes or documentation for extra context before writing an answer.

**Heuristic**  
A heuristic is a simple rule-based check. The companion uses heuristics when it wants a direct answer path that does not depend on the AI model.

**Match check**  
A match check is a simple check to make sure the copied values still agree with the original ROBERT files. It helps confirm that the companion is explaining the right run.

**PFI**  
PFI is a ROBERT result related to feature importance. It helps show which features mattered most in the run.

**No-PFI**  
No-PFI is the same run information without the feature-importance step. It gives a view of the run when that extra detail is not used or not available.

**VERIFY**  
VERIFY is the ROBERT stage that checks how well the model holds up in validation tests. It helps show whether the run’s performance looks dependable.

**CURATE**  
CURATE is the ROBERT stage that prepares the data before model building. It helps clean and organize the input data.

**GENERATE**  
GENERATE is the ROBERT stage that builds or screens models. It helps produce the candidate models that are later evaluated.

**PREDICT**  
PREDICT is the ROBERT stage that reports model performance and related results. It is one of the main sources of evidence for the companion.

**ROBERT-native JSON export**  
ROBERT-native JSON export means ROBERT itself writing structured JSON files directly. It is a future direction that could make the handoff from ROBERT to the companion simpler.
