# Deduplication Analysis Report tools:

## Overview
This report summarizes the deduplication analysis performed on 7,551 text files from the ANZ dataset. The analysis was conducted at three levels: word, sentence/line, and chunk (with varying sizes).

---

## Directory and File Information
- **Data Directory:** `~/data`
- **Total Files Processed:** 7,551

## Execute 

type ./run.sh


 dedupe_analyzer_chunk.py
 dedupe_analzyer.py
 dedupe_analzyer_sentence.py
 run.sh

---

## Word-Level Deduplication Analysis

### Overall Statistics
| Metric                     | Value         |
|----------------------------|---------------|
| Total Words Analyzed       | 1,107,614     |
| Unique Words Found         | 924           |

### Deduplication Potential
| Metric                     | Value         |
|----------------------------|---------------|
| Original Size              | 3,645.96 KB   |
| Deduplicated Size          | 4,330.48 KB   |
| Potential Bytes Saved      | -684.52 KB    |
| Deduplication Factor       | 0.84x         |
| Potential Space Reduction  | -18.77%       |

> **Note:** Negative savings indicate that deduplication at the word level increases storage requirements for this dataset.

### Top 50 Most Frequent Words
<custom-element data-json="%7B%22type%22%3A%22table-metadata%22%2C%22attributes%22%3A%7B%22title%22%3A%22Top%2050%20Most%20Frequent%20Words%22%7D%7D" />

| Rank | Word      | Frequency | Bytes/Word |
|------|-----------|-----------|------------|
| 1    | kt        | 78,468    | 2          |
| 2    | 1         | 66,593    | 1          |
| 3    | winds     | 66,216    | 5          |
| 4    | waves     | 66,102    | 5          |
| 5    | ft        | 62,819    | 2          |
| 6    | to        | 59,357    | 2          |
| 7    | 5         | 52,674    | 1          |
| 8    | 10        | 34,878    | 2          |
| 9    | night     | 20,225    | 5          |
| 10   | of        | 19,851    | 2          |
| 11   | showers   | 19,166    | 7          |
| 12   | around    | 16,504    | 6          |
| 13   | a         | 16,463    | 1          |
| 14   | chance    | 16,463    | 6          |
| 15   | less      | 15,779    | 4          |
| 16   | and       | 15,216    | 3          |
| 17   | nw        | 13,385    | 2          |
| 18   | with      | 12,813    | 4          |
| 19   | gusts     | 12,796    | 5          |
| 20   | s         | 12,061    | 1          |
| 21   | tstms     | 11,772    | 5          |
| 22   | in        | 11,526    | 2          |
| 23   | than      | 10,310    | 4          |
| 24   | sw        | 9,847     | 2          |
| 25   | 20        | 9,798     | 2          |
| 26   | 15        | 9,609     | 2          |
| 27   | from      | 9,395     | 4          |
| 28   | w         | 9,324     | 1          |
| 29   | wed       | 8,283     | 3          |
| 30   | tue       | 8,280     | 3          |
| 31   | thu       | 8,270     | 3          |
| 32   | fri       | 8,262     | 3          |
| 33   | sat       | 8,244     | 3          |
| 34   | mon       | 8,243     | 3          |
| 35   | sun       | 8,236     | 3          |
| 36   | the       | 7,885     | 3          |
| 37   | anz535    | 7,551     | 6          |
| 38   | tidal     | 7,551     | 5          |
| 39   | potomac   | 7,551     | 7          |
| 40   | key       | 7,551     | 3          |
| 41   | bridge    | 7,551     | 6          |
| 42   | indian    | 7,551     | 6          |
| 43   | head      | 7,551     | 4          |
| 44   | tonight   | 7,488     | 7          |
| 45   | this      | 6,739     | 4          |
| 46   | afternoon | 6,438     | 9          |
| 47   | n         | 6,266     | 1          |
| 48   | edt       | 6,258     | 3          |
| 49   | e         | 5,941     | 1          |
| 50   | rain      | 5,769     | 4          |

---

## Sentence/Line-Level Deduplication Analysis

### Overall Statistics
| Metric                     | Value         |
|----------------------------|---------------|
| Total Bytes Processed      | 4,844,327     |
| Total Sentences/Lines      | 181,407       |
| Unique Sentences/Lines     | 15,205        |

### Potential Savings
| Metric                     | Value         |
|----------------------------|---------------|
| Potential Reduction        | 4,239,096 bytes|
| Deduplication Factor       | 8.00x         |

### Top 50 Unique Sentences/Phrases by Frequency
<custom-element data-json="%7B%22type%22%3A%22table-metadata%22%2C%22attributes%22%3A%7B%22title%22%3A%22Top%2050%20Unique%20Sentences%2FPhrases%20by%20Frequency%22%7D%7D" />

| Rank | Count | Bytes (Single) | Bytes (Total) | Sentence/Phrase                                      |
|------|-------|----------------|---------------|------------------------------------------------------|
| 1    | 6,809 | 44             | 299,596       | "Tidal Potomac from Key Bridge to Indian Head"      |
| 2    | 6,050 | 7              | 42,350        | "TONIGHT"                                            |
| 3    | 4,682 | 3              | 14,046        | "THU"                                                |
| 4    | 4,679 | 3              | 14,037        | "FRI"                                                |
| 5    | 4,675 | 3              | 14,025        | "WED"                                                |
| 6    | 4,670 | 3              | 14,010        | "TUE"                                                |
| 7    | 4,668 | 3              | 14,004        | "SAT"                                                |
| 8    | 4,656 | 3              | 13,968        | "SUN"                                                |
| 9    | 4,653 | 3              | 13,959        | "MON"                                                |
| 10   | 2,934 | 64             | 187,776       | "Winds and waves higher and visibilities lower in and near tstms." |
| 11   | 2,689 | 32             | 86,048        | "NW winds 5 to 10 kt. Waves 1 ft."                   |
| 12   | 2,526 | 9              | 22,734        | "WED NIGHT"                                          |
| 13   | 2,525 | 9              | 22,725        | "TUE NIGHT"                                          |
| 14   | 2,519 | 9              | 22,671        | "THU NIGHT"                                          |
| 15   | 2,506 | 9              | 22,554        | "FRI NIGHT"                                          |
| 16   | 2,503 | 9              | 22,527        | "SAT NIGHT"                                          |
| 17   | 2,503 | 9              | 22,527        | "SUN NIGHT"                                          |
| 18   | 2,502 | 9              | 22,518        | "MON NIGHT"                                          |
| 19   | 1,869 | 5              | 9,345         | "TODAY"                                              |
| 20   | 1,797 | 32             | 57,504        | "S winds around 5 kt. Waves 1 ft."                   |
| 21   | 1,705 | 31             | 52,855        | "S winds 5 to 10 kt. Waves 1 ft."                    |
| 22   | 1,636 | 6              | 9,816         | "tstms."                                             |
| 23   | 1,498 | 14             | 20,972        | "THIS AFTERNOON"                                     |
| 24   | 1,472 | 35             | 51,520        | "S winds 5 kt. Waves less than 1 ft."                |
| 25   | 1,457 | 31             | 45,167        | "N winds 5 to 10 kt. Waves 1 ft."                    |
| 26   | 1,393 | 32             | 44,576        | "SW winds 5 to 10 kt. Waves 1 ft."                   |
| 27   | 1,387 | 31             | 42,997        | "W winds 5 to 10 kt. Waves 1 ft."                    |
| 28   | 1,303 | 13             | 16,939        | "REST OF TODAY"                                      |
| 29   | 1,294 | 33             | 42,702        | "SW winds around 5 kt. Waves 1 ft."                  |
| 30   | 1,087 | 33             | 35,871        | "NW winds around 5 kt. Waves 1 ft."                  |
| 31   | 1,055 | 11             | 11,605        | "Waves 1 ft."                                        |
| 32   | 1,039 | 32             | 33,248        | "E winds around 5 kt. Waves 1 ft."                   |
| 33   | 977   | 36             | 35,172        | "NW winds 5 kt. Waves less than 1 ft."               |
| 34   | 976   | 32             | 31,232        | "W winds around 5 kt. Waves 1 ft."                   |
| 35   | 953   | 15             | 14,295        | "REST OF TONIGHT"                                    |
| 36   | 916   | 33             | 30,228        | "SE winds around 5 kt. Waves 1 ft."                  |
| 37   | 898   | 35             | 31,430        | "N winds 5 kt. Waves less than 1 ft."                |
| 38   | 897   | 36             | 32,292        | "SW winds 5 kt. Waves less than 1 ft."               |
| 39   | 832   | 32             | 26,624        | "NE winds 5 to 10 kt. Waves 1 ft."                   |
| 40   | 778   | 33             | 25,674        | "NE winds around 5 kt. Waves 1 ft."                  |
| 41   | 750   | 32             | 24,000        | "N winds around 5 kt. Waves 1 ft."                   |
| 42   | 742   | 45             | 33,390        | "Tidal Potomac from Key Bridge to Indian Head-"      |
| 43   | 733   | 35             | 25,655        | "W winds 5 kt. Waves less than 1 ft."                |
| 44   | 701   | 36             | 25,236        | "NE winds 5 kt. Waves less than 1 ft."               |
| 45   | 661   | 10             | 6,610         | "and tstms."                                         |
| 46   | 614   | 35             | 21,490        | "E winds 5 kt. Waves less than 1 ft."                |
| 47   | 593   | 9              | 5,337         | "OVERNIGHT"                                          |
| 48   | 577   | 31             | 17,887        | "E winds 5 to 10 kt. Waves 1 ft."                    |
| 49   | 571   | 52             | 29,692        | "NW winds 5 to 10 kt with gusts to 20 kt. Waves 1 ft."|
| 50   | 549   | 16             | 8,784         | "chance of tstms."                                   |

---

## Chunk-Level Deduplication Analysis

### Chunk Size: 1024 bytes
| Metric                     | Value         |
|----------------------------|---------------|
| Total Files Analyzed       | 7,551         |
| Total Original Size        | 4,992.68 KB   |
| Total Chunks Processed     | 90            |
| Unique Chunks Found        | 78            |
| Size After Dedupe          | 78.00 KB      |
| Duplicate Chunks Found     | 10            |
| Total Potential Savings    | 12.00 KB      |
| Deduplication Ratio        | 64.01:1       |

### Chunk Size: 2048 bytes
- **Result:** No full-sized chunks found to analyze. Try a smaller chunk size.

### Chunk Size: 256 bytes
| Metric                     | Value         |
|----------------------------|---------------|
| Total Files Analyzed       | 7,551         |
| Total Original Size        | 4,992.68 KB   |
| Total Chunks Processed     | 16,157        |
| Unique Chunks Found        | 13,663        |
| Size After Dedupe          | 3,415.75 KB   |
| Duplicate Chunks Found     | 2,418         |
| Total Potential Savings    | 623.50 KB     |
| Deduplication Ratio        | 1.46:1        |

### Chunk Size: 128 bytes
| Metric                     | Value         |
|----------------------------|---------------|
| Total Files Analyzed       | 7,551         |
| Total Original Size        | 4,992.68 KB   |
| Total Chunks Processed     | 36,183        |
| Unique Chunks Found        | 30,285        |
| Size After Dedupe          | 3,785.62 KB   |
| Duplicate Chunks Found     | 5,614         |
| Total Potential Savings    | 737.25 KB     |
| Deduplication Ratio        | 1.32:1        |

---

## Summary of Findings
- **Word-level deduplication** is not effective for this dataset, as it results in a negative space reduction.
- **Sentence/line-level deduplication** shows significant potential, with an 8x reduction in size.
- **Chunk-level deduplication** is most effective at smaller chunk sizes (128 and 256 bytes), with the best ratio achieved at 256 bytes (1.46:1).

---

## Recommendations
- For maximum storage savings, consider deduplicating at the sentence/line level.
- If chunk-level deduplication is preferred, use a chunk size of 256 bytes for a balance between savings and complexity.

