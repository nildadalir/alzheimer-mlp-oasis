"""Build the English bachelor thesis Word document."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
RESULTS = ROOT / "results"
OUT_PATH = ROOT / "docs" / "Bachelor_Thesis_English.docx"


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_para(doc, text, *, size=12, bold=False, italic=False, align="justify", space_after=8, first_line=True):
    p = doc.add_paragraph()
    if align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if first_line and align == "justify":
        pf.first_line_indent = Cm(0.75)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(run, size=16 if level == 1 else 14 if level == 2 else 12, bold=True)
    return h


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    set_run_font(run, size=11, italic=True)


def add_picture(doc, path: Path, width=5.8):
    if not path.exists():
        add_para(doc, f"[Figure missing: {path.name}]", align="center", first_line=False, italic=True)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width))


def shade_header(cell):
    shading = cell._teProp if False else cell._tc.get_or_add_tcPr()
    from docx.oxml import OxmlElement

    fill = OxmlElement("w:shd")
    fill.set(qn("w:fill"), "1F4E79")
    fill.set(qn("w:val"), "clear")
    shading.append(fill)
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.bold = True


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_run_font(run, size=10, bold=True, color=RGBColor(255, 255, 255))
        shade_header(cell)
    for r_i, row in enumerate(rows):
        for c_i, value in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(value))
            set_run_font(run, size=10)
    doc.add_paragraph()
    return table


def configure_document(doc):
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")


def cover_page(doc):
    logo = FIGURES / "iau_logo.jpeg"
    if logo.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(logo), width=Inches(1.6))

    lines = [
        ("ISLAMIC AZAD UNIVERSITY", 16, True),
        ("North Tehran Branch", 14, True),
        ("Faculty of Engineering", 13, False),
        ("Department of Electrical Engineering and Computer Science", 12, False),
        ("", 12, False),
        ("BACHELOR’S THESIS", 16, True),
        ("Field of study: Information Technology", 13, False),
        ("", 12, False),
        ("Diagnosis of Alzheimer’s Disease Using Neural Networks", 18, True),
        ("", 12, False),
        ("Supervisor", 12, False),
        ("Eng. Samaneh Yazdani", 13, True),
        ("", 12, False),
        ("Author", 12, False),
        ("Niloofar Dalir Abdinia", 13, True),
    ]
    for text, size, bold in lines:
        if not text:
            doc.add_paragraph()
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold)


def front_matter(doc):
    doc.add_page_break()
    add_heading_styled(doc, "Declaration of Originality", 1)
    add_para(
        doc,
        "I hereby declare that this bachelor’s thesis is the result of my own research. "
        "Whenever I have used the scientific work of others (including theses, books, papers, "
        "and online resources), I have cited the source according to academic practice. "
        "This thesis has not been submitted, in whole or in part, for any other degree at "
        "this or any other institution. I accept full responsibility for the accuracy of "
        "this declaration.",
    )
    add_para(doc, "Author: Niloofar Dalir Abdinia", first_line=False, align="left")

    add_heading_styled(doc, "Dedication", 1)
    add_para(
        doc,
        "This work is dedicated to every student who reads it with academic honesty and "
        "uses it as a starting point for further research.",
    )

    add_heading_styled(doc, "Acknowledgements", 1)
    add_para(
        doc,
        "I would like to thank my parents, who have supported me at every stage of my life. "
        "Whatever I have achieved, I owe first to their patience and care.",
    )
    add_para(
        doc,
        "I am also deeply grateful to my supervisor, Eng. Samaneh Yazdani, for her guidance "
        "throughout this project. I wish her and her family continued success.",
    )

    add_heading_styled(doc, "Abstract", 1)
    add_para(
        doc,
        "Alzheimer’s disease is a progressive neurodegenerative disorder that threatens "
        "quality of life and remains difficult to diagnose from clinical signs alone. "
        "There is no single laboratory test that maps symptoms to a definite diagnosis "
        "in living patients, so machine-learning methods are widely studied as decision-support tools.",
    )
    add_para(
        doc,
        "This thesis develops a multilayer perceptron (MLP) classifier for Alzheimer’s "
        "detection on a standard clinical dataset derived from the OASIS study (Kaggle). "
        "After removing Converted (uncertain) cases, 336 records remain, each described "
        "by nine clinical and morphometric features and a binary label (Demented / Nondemented). "
        "Features are min–max normalized to [−1, +1]. Predictor importance is estimated "
        "with the minimum-redundancy maximum-relevance (MRMR) algorithm. The network has "
        "two hidden layers with 8 and 4 neurons.",
    )
    add_para(
        doc,
        "On a 10% held-out test set the original MATLAB experiments reached 100% accuracy "
        "in 9 of 10 runs when all features—including Clinical Dementia Rating (CDR)—were used. "
        "MRMR ranked CDR and MMSE as the dominant predictors, while eTIV and ASF contributed "
        "almost nothing. Removing those two weak features left accuracy unchanged. A later "
        "Python reproduction with a stratified 90/10 split confirmed 100% test accuracy with "
        "CDR present and 85.3% accuracy when CDR was withheld, which is the more realistic "
        "estimate of performance from the remaining clinical variables.",
    )
    add_para(doc, "Keywords: Alzheimer’s disease, artificial neural networks, MLP, feature selection, MRMR, OASIS", italic=True, first_line=False)

    add_heading_styled(doc, "Table of Contents", 1)
    toc = [
        "Abstract",
        "Chapter 1  Introduction",
        "    1.1  Problem statement",
        "    1.2  Motivation",
        "    1.3  Research challenges",
        "    1.4  Objectives",
        "    1.5  Research method",
        "    1.6  Key terms",
        "    1.7  Thesis structure",
        "Chapter 2  Background and related work",
        "    2.1  Alzheimer’s disease",
        "    2.2  Clinical and imaging diagnosis",
        "    2.3  Machine-learning methods",
        "    2.4  Related work",
        "Chapter 3  Proposed method",
        "    3.1  Pipeline",
        "    3.2  Dataset",
        "    3.3  Editing and encoding",
        "    3.4  Normalization",
        "    3.5  Feature selection (MRMR)",
        "    3.6  Train–test split",
        "    3.7  Neural-network classifier",
        "Chapter 4  Evaluation",
        "    4.1  Experimental setup",
        "    4.2  Evaluation metrics",
        "    4.3  Classifier results",
        "    4.4  Feature-selection results",
        "    4.5  Conclusions and limitations",
        "References",
    ]
    for item in toc:
        add_para(doc, item, align="left", first_line=False, space_after=2)


def chapter1(doc):
    doc.add_page_break()
    add_heading_styled(doc, "Chapter 1  Introduction", 1)

    add_heading_styled(doc, "1.1  Problem statement", 2)
    add_para(
        doc,
        "Alzheimer’s disease is a progressive brain disorder that gradually impairs memory, "
        "learning, reasoning, judgment, communication, and everyday activities [21]. It is a "
        "major cause of death worldwide. Over the last decade, data mining and machine learning "
        "have attracted growing attention in healthcare, especially for computer-aided diagnosis "
        "(CAD) systems that help clinicians make safer, more consistent decisions [2], [3], [8].",
    )
    add_para(
        doc,
        "This research uses an artificial neural network to detect Alzheimer’s disease from "
        "clinical features, and it studies how strongly each variable is associated with the "
        "diagnostic label. Two problems are addressed.",
    )
    add_para(
        doc,
        "Problem 1 — classifier design. A model y = f(x) maps an n-dimensional feature vector x, "
        "extracted from clinical examinations, to a binary decision: demented or nondemented. "
        "Feature extraction from raw medical examinations is outside the scope of this work; "
        "a public, already-annotated dataset is used. The quality of the classifier is measured "
        "by standard detection metrics. The learning algorithm is a multilayer perceptron.",
    )
    add_picture(doc, FIGURES / "pipeline_overview.png", width=5.2)
    add_caption(doc, "Figure 1-1. Overall classification pipeline used in this thesis.")

    add_para(
        doc,
        "Problem 2 — feature selection. A mapping g reduces the original n features to k ≤ n "
        "features. The classifier is then re-evaluated so that the effect of dimension reduction "
        "on accuracy and runtime can be measured. High-dimensional feature spaces scatter the "
        "samples, slow training, and can even degrade accuracy when irrelevant variables pull "
        "the learner off course. Feature selection estimates the contribution of each input to "
        "the output label, discards weak predictors, and—equally important in medicine—reports "
        "which clinical signs are most associated with disease. That ranking can support "
        "prevention and treatment discussions, provided it is interpreted with clinical caution.",
    )

    add_heading_styled(doc, "1.2  Motivation", 2)
    add_para(
        doc,
        "Poor clinical decisions can have irreversible consequences. Software that supports "
        "diagnosis can reduce error and the cost of unnecessary tests. In addition, quantifying "
        "the influence of each symptom on the predicted label may help clinicians focus on the "
        "most informative observations when screening for Alzheimer’s disease.",
    )

    add_heading_styled(doc, "1.3  Research challenges", 2)
    add_para(
        doc,
        "The central difficulty is that the mapping from clinical measurements to diagnosis is "
        "not given by a closed-form equation. Machine learning estimates that mapping from data. "
        "Even then, several practical issues remain: training can be slow when a network has more "
        "parameters than the problem requires; hyperparameters are often tuned by trial and error; "
        "and a large number of weakly related inputs can increase classification error rather than "
        "reduce it.",
    )

    add_heading_styled(doc, "1.4  Objectives", 2)
    add_para(doc, "The objectives of this thesis are:", first_line=False)
    add_para(doc, "1. To implement an artificial neural network for Alzheimer’s detection on a public clinical dataset.", first_line=False)
    add_para(doc, "2. To rank input features by their relevance to the diagnostic label (MRMR) and to test whether dropping the weakest features preserves accuracy while simplifying the model.", first_line=False)

    add_heading_styled(doc, "1.5  Research method", 2)
    add_para(
        doc,
        "The dataset is partitioned into a training set (90%) and a test set (10%). An MLP is "
        "trained on the training portion and evaluated on the unseen test portion. Feature "
        "selection is applied to the normalized table, and the classifier is re-run after the "
        "weakest features are removed. Figure 1-1 summarizes the workflow.",
    )

    add_heading_styled(doc, "1.6  Key terms", 2)
    add_para(doc, "Machine learning: algorithms that estimate unknown mappings from examples rather than from an explicit formula.", first_line=False)
    add_para(doc, "Artificial neural network: a learning model inspired by interconnected biological neurons, whose connection weights are fitted from training data.", first_line=False)
    add_para(doc, "Deep learning: neural networks with many hidden layers, able to approximate highly nonlinear functions and to learn representations from raw data such as images.", first_line=False)
    add_para(doc, "Feature selection: the process of scoring and optionally discarding input variables according to their relevance to the target, in order to simplify the model and often to speed up learning.", first_line=False)

    add_heading_styled(doc, "1.7  Thesis structure", 2)
    add_para(
        doc,
        "Chapter 2 reviews Alzheimer’s disease, diagnostic practice, the learning methods used "
        "in this work, and related papers. Chapter 3 describes the proposed pipeline, the dataset, "
        "normalization, MRMR, and the MLP architecture. Chapter 4 reports experimental results, "
        "discusses limitations, and concludes.",
    )


def chapter2(doc):
    doc.add_page_break()
    add_heading_styled(doc, "Chapter 2  Background and Related Work", 1)
    add_para(
        doc,
        "This chapter provides the background required to read the rest of the thesis. "
        "Section 2.1 introduces Alzheimer’s disease. Section 2.2 summarizes clinical and "
        "imaging diagnosis. Section 2.3 reviews the learning methods that appear in this "
        "study or in closely related work. Section 2.4 surveys previous machine-learning "
        "approaches to Alzheimer’s detection.",
    )

    add_heading_styled(doc, "2.1  Alzheimer’s disease", 2)
    add_para(
        doc,
        "Alzheimer’s disease is a neurodegenerative disorder in which cognitive abilities "
        "decline over time [25]. It was first described in 1907 by the German psychiatrist "
        "and neuropathologist Alois Alzheimer, who reported a 51-year-old woman with memory "
        "loss and disorientation. Autopsy showed severe cortical degeneration. The World Health "
        "Organization estimates that the number of people living with dementia will rise "
        "sharply by 2050 [25].",
    )
    add_picture(doc, FIGURES / "brain_comparison.png", width=4.4)
    add_caption(doc, "Figure 2-1. A typical brain (left) compared with a brain in late-stage Alzheimer’s disease (right).")
    add_para(
        doc,
        "According to WHO reporting around 2017, someone in the world develops dementia every "
        "few seconds. Memory decline is usually the symptom that prompts a clinical visit, but "
        "deficits also appear in thinking, language, judgment, reasoning, and perception. "
        "Impairment typically begins with recent events and later reaches remote memories. "
        "Alzheimer’s disease is the most common form of dementia.",
    )
    add_para(
        doc,
        "Pathologically, amyloid-β plaques accumulate around neurons in the hippocampus and "
        "elsewhere, disrupting synaptic communication and damaging nearby cells. Tau protein "
        "aggregates into neurofibrillary tangles inside neurons. Together with reduced "
        "neurotransmitter signalling, these processes produce brain atrophy. The strongest "
        "known genetic risk factor is APOE ε4; other associated factors include head trauma, "
        "clinical depression, and hypertension. Definite neuropathological confirmation is "
        "possible only after death. In life, diagnosis combines history, cognitive testing, "
        "imaging, and blood tests to exclude other causes. Good nutrition, physical activity, "
        "and social engagement are associated with lower cognitive-decline risk; no supplement "
        "has been shown to prevent the disease.",
    )

    add_heading_styled(doc, "2.2  Diagnosis of Alzheimer’s disease", 2)
    add_para(
        doc,
        "In clinic, the diagnosis is based on everyday symptoms—often reported by a relative—plus "
        "cognitive testing and investigations that rule out thyroid disease, vitamin deficiency, "
        "tumours, and other reversible causes. The physician also examines reflexes, gait, vision, "
        "hearing, coordination, and balance.",
    )
    add_para(
        doc,
        "Brain imaging is an important complementary tool. CT provides X-ray slices used mainly "
        "to exclude tumours and large lesions. MRI uses radio waves and a strong magnetic field "
        "and is generally preferred over CT for this disease because it can show atrophy in "
        "Alzheimer’s-related regions. PET injects a small amount of radiotracer to highlight "
        "metabolic or molecular abnormalities. Many published CAD systems take MRI or PET volumes "
        "as input. The present thesis instead uses a tabular clinical dataset; imaging is reviewed "
        "here because it dominates the related-work literature.",
    )
    add_picture(doc, FIGURES / "mri_sample.jpeg", width=5.6)
    add_caption(doc, "Figure 2-2. Example of brain MRI slices of the kind used in imaging-based CAD studies.")

    add_heading_styled(doc, "2.3  Machine-learning methods", 2)
    add_para(
        doc,
        "Machine learning builds a mathematical model from sample data in order to make predictions "
        "without being given an explicit program for the task [26]. Supervised methods learn from "
        "labelled pairs (xi, yi). Unsupervised methods, including clustering, look for structure "
        "without labels [27], [28]. This thesis is a supervised binary classification problem.",
    )
    add_picture(doc, FIGURES / "supervised_learning.png", width=4.8)
    add_caption(doc, "Figure 2-3. Supervised learning: a model is fit on labelled data and then applied to new samples.")

    add_heading_styled(doc, "2.3.1  Artificial neural networks", 3)
    add_para(
        doc,
        "An artificial neural network is a composition of simple units (neurons). Each neuron "
        "computes a weighted sum of its inputs and passes the result through a nonlinear "
        "activation such as tanh or a rectifier [30]. Learning means adjusting the weights from "
        "training examples. A multilayer perceptron (MLP) stacks an input layer, one or more "
        "hidden layers, and an output layer. Training commonly uses backpropagation with a "
        "gradient-based optimizer. The error surface may contain local minima, and convergence "
        "depends on the learning rate and the random initial weights [30].",
    )
    add_picture(doc, FIGURES / "neuron.png", width=4.6)
    add_caption(doc, "Figure 2-4. A computational neuron: weighted inputs are combined and mapped to an output.")
    add_para(
        doc,
        "In this thesis the network is small (two hidden layers, 8 and 4 neurons) because the "
        "dataset has only a few hundred rows. Deep networks with tens of layers are discussed "
        "below for completeness; they are the standard choice for raw MRI, not for a 9-feature table.",
    )

    add_heading_styled(doc, "2.3.2  Random forests", 3)
    add_para(
        doc,
        "A random forest aggregates many decision trees trained on bootstrap samples and random "
        "feature subsets [31]. The ensemble vote reduces overfitting relative to a single deep "
        "tree and handles both classification and regression. Forests are accurate and relatively "
        "easy to use, but they are slower and harder to interpret than one tree. They appear in "
        "several Alzheimer’s CAD papers listed in Section 2.4 and are reviewed here as a "
        "strong classical baseline, even though the implemented classifier is an MLP.",
    )
    add_picture(doc, FIGURES / "random_forest.png", width=5.2)
    add_caption(doc, "Figure 2-5. Idea of a random forest: several trees vote, and their outputs are aggregated.")

    add_heading_styled(doc, "2.3.3  Deep learning", 3)
    add_para(
        doc,
        "Deep learning refers to neural networks with many hidden layers that learn hierarchical "
        "representations of data [32]. Convolutional networks in particular have become the "
        "dominant approach for MRI- and PET-based Alzheimer’s classification. They are not used "
        "as the primary model in this bachelor project because the input is a low-dimensional "
        "clinical table rather than an image volume.",
    )
    add_picture(doc, FIGURES / "deep_network.png", width=5.4)
    add_caption(doc, "Figure 2-6. Schematic of a fully connected deep network.")

    add_heading_styled(doc, "2.3.4  Extreme learning machines", 3)
    add_para(
        doc,
        "An extreme learning machine (ELM) is a single-hidden-layer feedforward network whose "
        "hidden weights are drawn at random and never updated; only the output weights are solved, "
        "usually in closed form [31]. ELMs can train very quickly. They are included in the "
        "background because they are a lightweight alternative to backpropagation MLPs on small "
        "tabular problems.",
    )
    add_picture(doc, FIGURES / "elm.png", width=5.6)
    add_caption(doc, "Figure 2-7. Extreme learning machine: random hidden projection, closed-form output weights.")

    add_heading_styled(doc, "2.3.5  Feature selection", 3)
    add_para(
        doc,
        "Feature selection describes the data with fewer, more informative variables. Irrelevant "
        "inputs slow training and can distort generalization. Filter methods score features from "
        "the data alone (for example mutual information). Wrapper methods call the learner inside "
        "the search. Embedded methods fold selection into training itself [32]. This thesis uses "
        "MRMR, a filter that maximizes relevance to the label while minimizing redundancy among "
        "the chosen features. The ranking also has a clinical reading: it estimates how strongly "
        "each recorded symptom co-varies with the diagnostic tag.",
    )

    add_heading_styled(doc, "2.4  Related work", 2)
    add_para(
        doc,
        "Machine-learning papers on Alzheimer’s detection follow the same train-and-test pattern "
        "shown in Figure 1-1. Inputs fall into two families. The first family uses CT, MRI, or PET "
        "images; features are either hand-crafted or learned by a convolutional network. Those "
        "studies cannot easily include bedside cognitive scores. The second family uses tabular "
        "clinical records (spreadsheets), which is the setting of this thesis. Table 2-1 lists "
        "representative methods, dataset types, and reported accuracies. Direct numerical comparison "
        "is imperfect because the datasets, class definitions, and validation protocols differ.",
    )
    add_table(
        doc,
        ["Study", "Year", "Method", "Data", "Accuracy", "Feature sel."],
        [
            ["Emadi & Hasheminejad [15]", "2019", "3D-CNN", "CT", "85%", "—"],
            ["Khosravi [1]", "2019", "DT, NN", "Excel", "91.34%", "—"],
            ["Akhtari & Koleini [16]", "2021", "DL (U-Net)", "MRI", "95.3%", "—"],
            ["Razavi et al. [17]", "2020", "Deep NN", "MRI", "98.17%", "—"],
            ["Mazrouei Rad et al. [18]", "2022", "ERNN", "MRI", "86.5%", "—"],
            ["Jalali & Sarraf [19]", "2022", "DL", "MRI", "95%", "—"],
            ["Dai et al. [20]", "2021", "DL, CNN", "MRI, PET", "98.05%", "—"],
            ["Alroobaea et al. [22]", "2021", "LR, SVM, RF", "MRI", "99.43%", "—"],
            ["Afzal et al. [23]", "2021", "SVM, KNN, DL, LDA", "MRI, PET", "99.4%", "—"],
            ["Sathiyamoorthi et al. [24]", "2021", "CDL", "MRI", "97%", "—"],
            ["Lazli et al. [5]", "2018", "SVM", "MRI, PET", "75%", "—"],
            ["Ahmad et al. [10]", "2021", "DL, CNN", "MRI", "97%", "—"],
            ["Slim et al. [14]", "2021", "Parallel CNN", "MRI", "93%", "—"],
        ],
    )
    add_caption(doc, "Table 2-1. Selected learning methods reported for Alzheimer’s detection.")
    add_para(
        doc,
        "Most high accuracies in Table 2-1 are obtained on imaging datasets with deep models. "
        "Tabular clinical work is less common; Khosravi [1] is the closest published setting, "
        "with 91.34% using decision trees and neural networks. The contribution of the present "
        "thesis is a complete, documented MLP-plus-MRMR pipeline on OASIS clinical features, "
        "including an explicit ranking of symptoms and a discussion of the role of CDR.",
    )


def chapter3(doc):
    doc.add_page_break()
    add_heading_styled(doc, "Chapter 3  Proposed Method", 1)
    add_para(
        doc,
        "Chapter 1 defined two tasks: build a classifier, and rank (then optionally reduce) "
        "the input features. This chapter describes the solution. The classifier is a multilayer "
        "perceptron. Feature selection uses MRMR. Section 3.1 lists the processing steps. "
        "Sections 3.2–3.7 detail the dataset, encoding, normalization, MRMR, the train–test "
        "split, and the network.",
    )

    add_heading_styled(doc, "3.1  Pipeline", 2)
    add_para(doc, "The implementation proceeds as follows.", first_line=False)
    add_para(doc, "Step 1. Edit the raw table: drop Converted cases, encode categorical fields, and fill missing SES/MMSE values.", first_line=False)
    add_para(doc, "Step 2. Normalize every column to the interval [−1, +1].", first_line=False)
    add_para(doc, "Step 3. Run MRMR to score the influence of each input on the label.", first_line=False)
    add_para(doc, "Step 4. Split the normalized table into training (90%) and test (10%) subsets.", first_line=False)
    add_para(doc, "Step 5. Train the MLP on the training subset and evaluate it on the test subset.", first_line=False)
    add_para(doc, "Step 6. Repeat the evaluation after dropping the weakest features.", first_line=False)

    add_table(
        doc,
        ["File", "Description"],
        [
            ["oasis_clinical.csv", "Raw Kaggle/OASIS clinical table, 373 rows"],
            ["dataset2_edited.csv", "Converted cases removed; Group and Sex encoded as ±1"],
            ["dataset3_normalized.csv", "All columns scaled to [−1, +1]"],
            ["dataset4_train.csv", "90% training rows"],
            ["dataset5_test.csv", "10% test rows"],
        ],
    )
    add_caption(doc, "Table 3-1. Dataset files used in the pipeline.")

    add_table(
        doc,
        ["Program", "Role", "Input", "Output"],
        [
            ["edit_dataset", "Encode and clean", "oasis_clinical.csv", "dataset2_edited.csv"],
            ["normalize", "Min–max scaling", "dataset2_edited.csv", "dataset3_normalized.csv"],
            ["feature_selection", "MRMR ranking", "dataset3_normalized.csv", "bar chart + scores"],
            ["split_data", "90/10 split", "dataset3_normalized.csv", "train and test CSVs"],
            ["mlp_classifier", "Train/test MLP", "train/test CSVs", "metrics"],
        ],
    )
    add_caption(doc, "Table 3-2. Programs implemented for this thesis (MATLAB and Python).")

    add_heading_styled(doc, "3.2  Dataset", 2)
    add_para(
        doc,
        "The dataset was obtained from Kaggle and contains clinical observations in CSV form. "
        "It has nine input features and one output label. The label takes the values Demented, "
        "Nondemented, and Converted (patients who changed diagnostic status during follow-up). "
        "The raw file has 373 rows: 146 Demented, 190 Nondemented, and 37 Converted. Because the "
        "task is to predict presence versus absence of Alzheimer’s disease, Converted rows are "
        "removed, leaving 336 labelled samples.",
    )
    add_table(
        doc,
        ["Feature", "Meaning", "Range / values"],
        [
            ["Group", "Diagnostic label", "Demented / Nondemented"],
            ["Sex (M/F)", "Biological sex", "M / F"],
            ["Age", "Age in years", "60–98"],
            ["EDUC", "Years of education", "6–23"],
            ["SES", "Socioeconomic status", "1–5 (0 if missing)"],
            ["MMSE", "Mini-Mental State Examination", "4–30"],
            ["CDR", "Clinical Dementia Rating", "0–2"],
            ["eTIV", "Estimated total intracranial volume", "1106–2004"],
            ["nWBV", "Normalized whole-brain volume", "0.644–0.837"],
            ["ASF", "Atlas scaling factor", "0.876–1.587"],
        ],
    )
    add_caption(doc, "Table 3-3. Features in the clinical dataset.")
    add_para(
        doc,
        "A methodological caveat is necessary. CDR is a clinician-assigned dementia rating; it is "
        "highly aligned with the Group label by construction. Using CDR as an ordinary predictor "
        "therefore inflates accuracy. Chapter 4 reports results both with and without CDR so that "
        "this effect is visible.",
    )

    add_heading_styled(doc, "3.3  Editing and encoding", 2)
    add_para(
        doc,
        "Neural networks require numeric inputs. Group is encoded as +1 (Demented) and −1 "
        "(Nondemented). Sex is encoded as +1 (male) and −1 (female). The header row is not stored "
        "in the numeric CSVs. Nineteen SES values and two MMSE values are missing in the retained "
        "rows; they are filled with 0 and 4 respectively, matching the original thesis preparation. "
        "The result is dataset2_edited.csv (336 × 10).",
    )

    add_heading_styled(doc, "3.4  Normalization", 2)
    add_para(
        doc,
        "Min–max normalization prevents features with large numeric range (for example eTIV) from "
        "dominating features with small range (for example nWBV). Each column x is first mapped to "
        "[0, 1] by (x − min) / (max − min) and then linearly rescaled to [lb, ub] = [−1, +1]:",
    )
    add_para(doc, "x' = (ub − lb) · (x − xmin) / (xmax − xmin) + lb.", align="center", first_line=False, italic=True)
    add_para(
        doc,
        "Because the label already lies in {−1, +1}, it is unchanged by this transform. The same "
        "holds for Sex. The original MATLAB listing used csvread/csvwrite; the corrected programs "
        "use readmatrix/writematrix (MATLAB) and NumPy (Python).",
    )

    add_heading_styled(doc, "3.5  Feature selection with MRMR", 2)
    add_para(
        doc,
        "MRMR ranks features by a trade-off between relevance to the label and redundancy with "
        "features already chosen. In MATLAB this is the toolbox function fscmrmr. The ranking "
        "answers two questions: which clinical signs are most associated with the label, and "
        "which columns can be dropped without harming the classifier. Chapter 4 shows that CDR "
        "and MMSE dominate, while eTIV and ASF are effectively unused.",
    )

    add_heading_styled(doc, "3.6  Train–test split", 2)
    add_para(
        doc,
        "The original MATLAB script called dividerand(n, 0.9, 0.1) with two output arguments. "
        "That function expects three ratios (train, validation, test) and defaults the missing "
        "test ratio to 0.15. Combined with two outputs, the 10% “test” set was actually the "
        "validation index vector, about 13% of rows were discarded, and the written files "
        "contained 263 + 29 = 292 rows instead of 336. The corrected split is a true 90/10 "
        "partition of every row. The Python reproduction additionally stratifies on the label "
        "and fixes a random seed so that results can be regenerated.",
    )

    add_heading_styled(doc, "3.7  Neural-network classifier", 2)
    add_para(
        doc,
        "The network is a 9–8–4–1 MLP: nine inputs (or seven after dropping eTIV and ASF), two "
        "hidden layers with 8 and 4 neurons, and a single linear output. Hidden units use the "
        "hyperbolic tangent. Training in MATLAB uses Levenberg–Marquardt (trainlm), the default "
        "of newff / feedforwardnet. Because the data have already been split, the network must "
        "not split them again internally; the corrected MATLAB code sets divideFcn to dividetrain. "
        "The raw output is a real number; it is thresholded at 0, mapping to +1 (demented) or −1 "
        "(healthy). Architecture depth and width were chosen by trial and error on this dataset, "
        "as described in the original thesis.",
    )
    add_para(
        doc,
        "The original listing of newff used hardcoded spreadsheet ranges (263 training rows and "
        "29 test rows, and in one place a claim of seven input neurons). The MATLAB screenshots "
        "in Chapter 4 show nine input neurons, which matches the nine clinical features. The "
        "corrected programs infer sizes from the files and no longer hard-code row counts.",
    )


def chapter4(doc):
    doc.add_page_break()
    add_heading_styled(doc, "Chapter 4  Evaluation", 1)
    add_para(
        doc,
        "This chapter evaluates the two solutions of Chapter 3. Section 4.1 describes the "
        "experimental machine. Section 4.2 defines the metrics. Section 4.3 reports MLP "
        "performance from the original MATLAB runs and from the corrected Python reproduction. "
        "Section 4.4 reports MRMR rankings. Section 4.5 concludes, including limitations that "
        "matter for any later clinical reading of the results.",
    )

    add_heading_styled(doc, "4.1  Experimental setup", 2)
    add_table(
        doc,
        ["Item", "Specification"],
        [
            ["CPU", "Intel Core i7"],
            ["RAM", "8 GB"],
            ["Operating system", "Windows 10, 64-bit"],
            ["Original environment", "MATLAB 2021, Deep Learning Toolbox"],
            ["Reproduction environment", "Python 3, scikit-learn"],
        ],
    )
    add_caption(doc, "Table 4-1. Experimental platform used for the original MATLAB study.")
    add_para(
        doc,
        "After editing, the table has 336 rows, nine input features, and one label. Ninety "
        "percent of rows are used for training and ten percent for testing.",
    )

    add_heading_styled(doc, "4.2  Evaluation metrics", 2)
    add_para(
        doc,
        "Performance is summarized by a confusion matrix. The positive class is Demented (+1). "
        "The original MATLAB script swapped the names of false positives and false negatives; "
        "the definitions below are the standard ones and are used throughout this English version.",
    )
    add_table(
        doc,
        ["", "Predicted healthy (−1)", "Predicted demented (+1)"],
        [
            ["Actually healthy (−1)", "TN", "FP"],
            ["Actually demented (+1)", "FN", "TP"],
        ],
    )
    add_caption(doc, "Table 4-2. Confusion matrix. Positive class = Demented.")
    add_para(doc, "TP — true positive: a demented subject correctly identified.", first_line=False)
    add_para(doc, "TN — true negative: a healthy subject correctly identified.", first_line=False)
    add_para(doc, "FP — false positive: a healthy subject predicted as demented.", first_line=False)
    add_para(doc, "FN — false negative: a demented subject predicted as healthy.", first_line=False)
    add_para(doc, "Accuracy = (TP + TN) / (TP + TN + FP + FN).", first_line=False)
    add_para(doc, "Precision = TP / (TP + FP).", first_line=False)
    add_para(doc, "Recall / sensitivity = TP / (TP + FN).", first_line=False)
    add_para(doc, "Specificity = TN / (TN + FP).", first_line=False)
    add_para(doc, "F1 = 2 · precision · recall / (precision + recall).", first_line=False)
    add_para(
        doc,
        "Training time, test time, and per-sample prediction time are also reported for the "
        "original MATLAB runs.",
    )

    add_heading_styled(doc, "4.3  Classifier performance", 2)
    add_para(
        doc,
        "Table 4-3 repeats the three MATLAB runs documented in the original thesis. The test "
        "file then contained 29 rows (22 healthy, 7 demented)—a consequence of the dividerand "
        "bug described in Section 3.6. Nine of ten runs reached 100% accuracy; one run reached "
        "93.10% (two healthy subjects were labelled demented if the confusion counts are read "
        "with standard FP/FN names: TP=5, TN=22, FP=0, FN=2 in standard terms would correspond "
        "to missing two patients, but the printed listing showed TP=5, TN=22, FP=2, FN=0 because "
        "FP and FN were swapped in code). Accuracy itself is unaffected by that naming swap.",
    )
    add_table(
        doc,
        ["Metric", "Run 1", "Run 2", "Run 3"],
        [
            ["TP / TN", "5 / 22", "7 / 22", "7 / 22"],
            ["Printed FP / FN", "2 / 0", "0 / 0", "0 / 0"],
            ["Accuracy", "93.10%", "100%", "100%"],
            ["Precision (printed)", "0.71", "1.00", "1.00"],
            ["Recall (printed)", "1.00", "1.00", "1.00"],
            ["F1", "0.83", "1.00", "1.00"],
            ["Train time (s)", "2.61", "1.61", "1.38"],
            ["Test time (s)", "0.123", "0.11", "0.10"],
            ["Per sample (µs)", "4241", "3793", "3448"],
        ],
    )
    add_caption(doc, "Table 4-3. Original MATLAB MLP results on the 29-row test file, as recorded in 2022.")
    add_picture(doc, FIGURES / "matlab_run1.png", width=5.8)
    add_caption(doc, "Figure 4-1. MATLAB run 1 (93.10% accuracy). Network: 9-8-4-1.")
    add_picture(doc, FIGURES / "matlab_run2.png", width=5.8)
    add_caption(doc, "Figure 4-2. MATLAB run 2 (100% accuracy).")
    add_picture(doc, FIGURES / "matlab_run3.png", width=5.8)
    add_caption(doc, "Figure 4-3. MATLAB run 3 (100% accuracy).")

    add_para(
        doc,
        "The corrected Python pipeline uses all 336 rows, a stratified 90/10 split (302 / 34), "
        "and a tanh MLP with hidden layers (8, 4). With all nine features, test accuracy is 100% "
        "(TP=15, TN=19). After dropping eTIV and ASF, accuracy remains 100%. After dropping CDR, "
        "accuracy falls to 85.3% (precision 0.81, recall 0.87). That last figure is the honest "
        "estimate of what the remaining clinical variables can do without the clinician’s CDR score.",
    )
    add_table(
        doc,
        ["Setting", "Features", "Test n", "Accuracy", "Precision", "Recall", "F1"],
        [
            ["Python, all features", "9", "34", "100%", "1.00", "1.00", "1.00"],
            ["Python, no eTIV/ASF", "7", "34", "100%", "1.00", "1.00", "1.00"],
            ["Python, no CDR", "8", "34", "85.3%", "0.81", "0.87", "0.84"],
        ],
    )
    add_caption(doc, "Table 4-4. Reproducible Python results (random seed 42, stratified split).")
    add_picture(doc, RESULTS / "confusion_all_features.png", width=4.0)
    add_caption(doc, "Figure 4-4. Python confusion matrix, all nine features.")
    add_picture(doc, RESULTS / "confusion_without_cdr.png", width=4.0)
    add_caption(doc, "Figure 4-5. Python confusion matrix after removing CDR.")

    add_heading_styled(doc, "4.4  Feature-selection results", 2)
    add_para(
        doc,
        "Figure 4-6 and Table 4-5 show the original MATLAB MRMR ranking. CDR is by far the most "
        "informative feature, followed by MMSE, sex, SES, and nWBV. Education and age contribute "
        "little. eTIV and ASF have scores at machine precision, i.e. they are unused. Removing "
        "those two columns did not change MATLAB accuracy (still 100% on the recorded run) and "
        "slightly reduced training time (1.38 s to 1.36 s).",
    )
    add_picture(doc, FIGURES / "mrmr_scores.png", width=5.6)
    add_caption(doc, "Figure 4-6. MATLAB MRMR scores, features ordered from most to least important.")
    add_table(
        doc,
        ["Index", "Feature", "MRMR score (MATLAB)"],
        [
            ["6", "CDR", "0.655134157956"],
            ["5", "MMSE", "0.253882404762"],
            ["1", "Sex (M/F)", "0.249348772788"],
            ["4", "SES", "0.231951709708"],
            ["8", "nWBV", "0.171986597950"],
            ["3", "EDUC", "0.042562729236"],
            ["2", "Age", "0.028857244824"],
            ["7", "eTIV", "≈ 0"],
            ["9", "ASF", "0"],
        ],
    )
    add_caption(doc, "Table 4-5. MATLAB MRMR importance for each input feature.")
    add_picture(doc, FIGURES / "matlab_run_reduced.png", width=5.8)
    add_caption(doc, "Figure 4-7. MATLAB run after dropping eTIV and ASF (7-8-4-1 network, 100% accuracy).")
    add_picture(doc, RESULTS / "mrmr_feature_importance.png", width=5.4)
    add_caption(doc, "Figure 4-8. Python MRMR ranking used in the public repository (CDR and MMSE still dominate).")

    add_heading_styled(doc, "4.5  Conclusions and limitations", 2)
    add_para(
        doc,
        "This thesis implemented an MLP classifier for Alzheimer’s detection on a public clinical "
        "dataset of 336 demented and nondemented subjects. With CDR included, both the original "
        "MATLAB experiments and the Python reproduction reach 100% test accuracy on a small held-out "
        "set. MRMR shows that CDR and MMSE carry almost all of the signal, while intracranial-volume "
        "features are redundant. Dropping eTIV and ASF does not hurt accuracy.",
    )
    add_para(
        doc,
        "Those headline numbers must be read with care. First, CDR is not an independent biomarker; "
        "it is a clinical staging score tightly coupled to the diagnosis. Without CDR, test accuracy "
        "in the Python reproduction is 85.3%, which is still useful as a screening aid but is not "
        "perfect. Second, the test sets are small (29 or 34 rows), so a single split can look "
        "optimistic. Third, missing SES and MMSE values were filled with constants rather than a "
        "proper imputation model. Fourth, the original MATLAB split accidentally discarded rows; "
        "the public code in this repository corrects that behaviour.",
    )
    add_para(
        doc,
        "Within those limits, the work shows that a small neural network can separate the two "
        "classes in this table, that MRMR provides an interpretable ranking of symptoms, and that "
        "the most responsible next step is to evaluate the same pipeline with CDR held out and "
        "with cross-validation on a larger cohort. The accompanying GitHub repository contains "
        "corrected MATLAB programs, a full Python implementation, and the English text of this thesis.",
    )


def references(doc):
    doc.add_page_break()
    add_heading_styled(doc, "References", 1)
    refs = [
        "[1] H. Sarvi, “A method for predicting Alzheimer’s disease using a decision-tree model,” 8th National Conference on Computer Science and Information Technology, 2019.",
        "[2] S. Gupta et al., “Supervised computer-aided diagnosis (CAD) methods for classifying Alzheimer’s disease-based neurodegenerative disorders,” Computational and Mathematical Methods in Medicine, 2022.",
        "[3] G. S. Babu and B. S. Mahanand, “Computer aided detection of imaging biomarkers for Alzheimer's disease,” International Journal of Signal and Imaging Systems Engineering, vol. 12, no. 3, pp. 108–118, 2021.",
        "[4] M. P. Arakeri and S. K. Manvi, “Medical imaging and computer-aided diagnosis,” in Medical Imaging Methods, CRC Press, 2021, pp. 45–56.",
        "[5] L. Lazli, M. Boukadoum, and O. Ait Mohamed, “Computer-aided diagnosis system for Alzheimer's disease using fuzzy-possibilistic tissue segmentation and SVM classification,” IEEE Life Sciences Conference (LSC), 2018.",
        "[6] R. G. de Souza et al., “Computer-aided diagnosis of Alzheimer’s disease by MRI analysis and evolutionary computing,” Research on Biomedical Engineering, vol. 37, no. 3, pp. 455–483, 2021.",
        "[7] I. Garali et al., “Region-based brain selection and classification on PET images for Alzheimer's disease computer aided diagnosis,” IEEE ICIP, 2015.",
        "[8] I. Garali et al., “Brain region ranking for 18FDG-PET computer-aided diagnosis of Alzheimer's disease,” Biomedical Signal Processing and Control, vol. 27, pp. 15–23, 2016.",
        "[9] S. Saravanakumar and P. Thangaraj, “A computer aided diagnosis system for identifying Alzheimer’s from MRI scan using improved Adaboost,” Journal of Medical Systems, vol. 43, no. 3, 2019.",
        "[10] M. F. Ahmad et al., “Deep learning approach to diagnose Alzheimer’s disease through magnetic resonance images,” International Conference on Innovative Computing (ICIC), 2021.",
        "[11] S. Shaji, N. Ganapathy, and R. Swaminathan, “Classification of Alzheimer condition using MR brain images and inception-residual network model,” Current Directions in Biomedical Engineering, vol. 7, no. 2, pp. 763–766, 2021.",
        "[12] P. R. Ananya, V. Pachisia, and S. Ushasukhanya, “Optimization of CNN in capsule networks for Alzheimer’s disease prediction using CT images,” in Proceedings of International Conference on Deep Learning, Computing and Intelligence, Springer, 2022.",
        "[13] S. Qiu et al., “Dwarfism computer-aided diagnosis algorithm based on multimodal pyradiomics,” Information Fusion, vol. 80, pp. 137–145, 2022.",
        "[14] A. Slim, A. Melouah, and S. Layachi, “Alzheimer’s disease diagnosis using parallel convolutional neural networks,” ICRAMI, 2021.",
        "[15] F. Emadi and M. Hasheminejad, “Diagnosis of Alzheimer’s disease using 3D convolutional neural networks,” 5th Conference on Distributed Computing and Big Data Processing, 2019.",
        "[16] A. Akhtari and M. Koleini, “Diagnosis of Alzheimer’s disease using an optimized deep U-Net,” 7th International Conference on Knowledge and Technology, 2021.",
        "[17] F. Razavi, M. J. Tarokh, and M. Alborzi, “Identifying Alzheimer’s disease using a deep learning neural network,” Journal of Research in Behavioural Sciences, vol. 18, no. 2, pp. 260–269, 2020.",
        "[18] E. Mazrouei Rad, V. Hosseinzadeh, and S. Shabahang, “Diagnosis of Alzheimer’s disease by feature extraction from MRI images,” 12th International Conference on New Solutions in Engineering, 2022.",
        "[19] Z. Jalali Farahani and S. Sarraf Esmaeili, “Deep learning for diagnosing Alzheimer’s disease from MRI images,” 2nd International Conference on Electrical, Computer and Mechanical Engineering, 2022.",
        "[20] Y. Dai et al., “Computer-aided diagnosis of Alzheimer’s disease via deep learning models and radiomics method,” Applied Sciences, vol. 11, no. 17, p. 8104, 2021.",
        "[21] C. Fabrizio et al., “Artificial intelligence for Alzheimer’s disease: promise or challenge?,” Diagnostics, vol. 11, no. 8, p. 1473, 2021.",
        "[22] R. Alroobaea et al., “Alzheimer's disease early detection using machine learning techniques,” 2021.",
        "[23] S. Afzal et al., “Alzheimer disease detection techniques and methods: a review,” 2021.",
        "[24] V. Sathiyamoorthi et al., “A deep convolutional neural network based computer aided diagnosis system for the prediction of Alzheimer's disease in MRI images,” Measurement, vol. 171, p. 108838, 2021.",
        "[25] S. Liang and Y. Gu, “Computer-aided diagnosis of Alzheimer’s disease through weak supervision deep learning framework with attention mechanism,” Sensors, vol. 21, no. 1, p. 220, 2020.",
        "[26] L. Lazli, M. Boukadoum, and O. Ait Mohamed, “A survey on computer-aided diagnosis of brain disorders through MRI based on machine learning and data mining methodologies with an emphasis on Alzheimer disease diagnosis,” Applied Sciences, vol. 10, no. 5, p. 1894, 2020.",
        "[27] T. Jiang, J. L. Gradus, and A. J. Rosellini, “Supervised machine learning: a brief primer,” Behavior Therapy, vol. 51, no. 5, pp. 675–687, 2020.",
        "[28] M. Ahmed, R. Seraj, and S. M. S. Islam, “The k-means algorithm: a comprehensive survey and performance evaluation,” Electronics, vol. 9, no. 8, p. 1295, 2020.",
        "[29] H. Alvani and D. Pour, “Application of artificial neural networks in strategic decision making,” Management Studies, vol. 18, no. 54, pp. 1–38, 2007.",
        "[30] M. B. Menhaj, Fundamentals of Neural Networks, vol. 1. Amirkabir University of Technology Press, 3rd ed., 2005.",
        "[31] M. Kia, Soft Computing in MATLAB. Kian Academic Press, 1st ed., 2018.",
        "[32] A. Torkian, Deep Learning. Niaz Danesh Press, 3rd ed., 2021.",
    ]
    for ref in refs:
        add_para(doc, ref, first_line=False, space_after=6, align="left")


def add_footer(doc):
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Niloofar Dalir Abdinia  ·  Bachelor’s Thesis  ·  Islamic Azad University, North Tehran Branch")
    set_run_font(run, size=9, italic=True, color=RGBColor(80, 80, 80))


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    doc = Document()
    configure_document(doc)
    add_footer(doc)
    cover_page(doc)
    front_matter(doc)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    references(doc)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
