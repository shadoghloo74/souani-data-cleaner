# Souani Data Cleaner — UAT Plan

## Version

**Application Version:** v1.0.0
**Testing Phase:** User Acceptance Testing (UAT)
**Status:** Planned
**Purpose:** Validate the application using realistic user workflows and real-world datasets before planning v1.1.

---

# 1. UAT Objectives

The objective of UAT is to verify that Souani Data Cleaner is suitable for practical use with real-world data.

The testing will focus on:

* Data loading.
* Data validation.
* Missing value processing.
* Outlier detection.
* Outlier treatment.
* Pipeline execution.
* Report generation.
* Backup creation.
* GUI usability.
* Windows executable stability.
* Error handling.
* Output correctness.

UAT is not intended to introduce new features or modify the architecture of v1.0.0.

---

# 2. Testing Environment

## Operating System

* Windows 10 / Windows 11

## Application

* Souani Data Cleaner v1.0.0

## Execution Mode

* Windows executable:
  `dist/Souani_Data_Cleaner.exe`

## Test Data

Testing should use realistic datasets representing actual expected usage.

Recommended formats:

* CSV
* Excel
* Other formats officially supported by the application

---

# 3. UAT Test Categories

## A. Application Startup

| Test               | Expected Result                  | Status |
| ------------------ | -------------------------------- | ------ |
| Launch application | Application starts successfully  | ⬜      |
| Open GUI           | GUI loads correctly              | ⬜      |
| Close application  | Application closes without error | ⬜      |

---

## B. Data Loading

| Test               | Expected Result                      | Status |
| ------------------ | ------------------------------------ | ------ |
| Load valid dataset | Dataset loads successfully           | ⬜      |
| Load empty dataset | Clear validation message             | ⬜      |
| Load invalid file  | Clear error message                  | ⬜      |
| Load large dataset | Dataset loads within acceptable time | ⬜      |

---

# 4. Missing Value Testing

Test datasets containing:

* Completely empty cells.
* Partially missing columns.
* Multiple missing columns.
* Mixed missing-value patterns.

Verify:

* Missing values are detected correctly.
* Selected treatment is applied correctly.
* Non-missing values remain unchanged.
* Final output is valid.

Status:

⬜ Passed
⬜ Failed
⬜ Needs Investigation

---

# 5. Outlier Detection Testing

Test the following detection methods:

* IQR
* Z-Score
* Modified Z-Score
* Percentile
* Standard Deviation

For each detector verify:

1. Correct detection of expected outliers.
2. No unnecessary modification of normal values.
3. Correct handling of small datasets.
4. Correct handling of repeated values.
5. Correct behavior with valid numeric columns.

---

# 6. Outlier Treatment Testing

Test:

* Clipping.
* Mean treatment.
* Median treatment.
* Constant treatment.
* Row dropping.
* Flagging.

For every treatment verify:

* Outliers are treated correctly.
* Normal values remain unchanged.
* Row counts are correct.
* Data types remain valid.
* Output can be saved successfully.

---

# 7. Pipeline Testing

Verify the complete workflow:

```text
Input Data
    ↓
Validation
    ↓
Detection
    ↓
Treatment
    ↓
Metadata
    ↓
EngineReport
    ↓
JSON / HTML Report
    ↓
Backup
    ↓
Final Clean Data
```

Expected result:

The complete workflow executes successfully without unexpected errors.

Status:

⬜ Passed
⬜ Failed
⬜ Needs Investigation

---

# 8. Plugin Testing

Verify that a valid external Plugin can:

* Load successfully.
* Provide its manifest.
* Register a Detector or Treatment.
* Execute through the Pipeline.
* Produce valid output.

Verify that the core Engine does not require modification.

Status:

⬜ Passed
⬜ Failed
⬜ Needs Investigation

---

# 9. Reporting Testing

Verify generated reports:

## JSON

Check:

* Valid JSON structure.
* Correct execution metadata.
* Correct detector information.
* Correct treatment information.
* Correct results.

## HTML

Check:

* File opens correctly.
* Information is readable.
* Results are complete.
* No broken sections.

---

# 10. Backup Testing

Before processing:

1. Confirm original data exists.
2. Execute cleaning operation.
3. Verify that a backup is created.
4. Verify that the backup represents the original data.
5. Verify that the processed output is separate from the backup.

Status:

⬜ Passed
⬜ Failed
⬜ Needs Investigation

---

# 11. GUI Usability Testing

Evaluate:

* Ease of navigation.
* Clarity of labels.
* Ease of selecting columns.
* Ease of selecting detection methods.
* Ease of selecting treatments.
* Error-message clarity.
* Report access.
* Backup access.
* Overall workflow simplicity.

Record all observations in the UAT issue log.

---

# 12. Performance Testing

Test at least three dataset sizes:

### Small

Approximately:

```text
< 10,000 rows
```

### Medium

Approximately:

```text
10,000 – 100,000 rows
```

### Large

Approximately:

```text
> 100,000 rows
```

Record:

* Dataset size.
* Processing time.
* Memory behavior.
* Errors.
* Application responsiveness.

---

# 13. UAT Issue Classification

Every problem discovered during UAT must be classified as one of:

```text
BUG
UX
PERFORMANCE
REPORTING
SECURITY
FEATURE REQUEST
DOCUMENTATION
```

Do not immediately modify the source code after discovering an issue.

Record it first.

---

# 14. Acceptance Criteria

The v1.0.0 release will be considered UAT-accepted when:

* Critical workflows operate correctly.
* No critical defects remain unresolved.
* Data processing produces expected results.
* Reports are generated correctly.
* Backups are created correctly.
* The Windows executable operates correctly.
* The GUI is usable for normal workflows.
* No data corruption is observed.

---

# 15. UAT Result

**Overall UAT Status:**

⬜ ACCEPTED

⬜ ACCEPTED WITH MINOR ISSUES

⬜ NOT ACCEPTED

---

# 16. Final Recommendation

After completing the UAT process, prepare a summary containing:

* Number of tests executed.
* Number passed.
* Number failed.
* Critical issues.
* Minor issues.
* UX observations.
* Performance observations.
* Recommended fixes.
* Features requested for v1.1.

The UAT results will be used as the primary input for planning the next development cycle.
