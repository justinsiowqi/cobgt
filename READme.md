# CoBGT: Combination of BERT, GraphSAGE, and Transformer Model

## Overview
This project is an implementation of the paper "Robust Text-to-Cypher Using Combination of BERT, GraphSAGE, and Transformer (CoBGT) Model." The [original paper](https://www.mdpi.com/2076-3417/14/17/7881) proposes a novel technique to translate natural language text into cypher queries for the Neo4j graph database.
Please note that this paper was not authored by me, and the original authors did not provide a public GitHub repository for reference. The code in this repository represents my interpretation of the ideas from the paper, and as such, it may not be fully accurate or complete. It is an ongoing work, specifically focusing on the relation and properties prediction module.

## Credits and Acknowledgements
Parts of this project leverages the work by :
- [Synthetic dataset created with Gemini 1.5 Pro](https://github.com/neo4j-labs/text2cypher/tree/main/datasets/synthetic_gemini_demodbs) by Tomaz Bratanic
- [Libcypher Parser](https://github.com/cleishm/libcypher-parser) by Chris Leishman, Louis-Pierre Beaumont, Jeff Lovitz and Dvir Dukhan

For more details, you can visit the project page and the FAQ.

## Prerequisites
To run this project, you'll need to install [libcypher-parser](https://github.com/cleishm/libcypher-parser). For more information about how to install and use the package, you can refer to my [cypher parser](https://github.com/justinsiowqi/cypher-parser) repository.

You will also need to install the spaCy English Core Model.
```bash
pip install spacy
python -m spacy download en_core_web_lg
```

## Running the Key Value Extraction Module
To run this module, you'll need to generate a dataset containing question-cypher pairs in order to fine-tune the BERT model. Alternatively, you can attach your own dataset.

```bash
cd key_value
python generate_questions.py
python generate_cypher.py
```

## Running the Relation Properties Module
To properly run the model with the correct data, you'll need to create or edit the question_cypher.txt file. This file must be formatted correctly to ensure that the questions and Cypher queries are parsed as expected.

File Format Requirements:
- Two Questions: The file should contain two questions and their corresponding Cypher statements.
- Question and Cypher Format: Each question and Cypher pair should be followed by "Question" and "Cypher" labels as shown below. Ensure you maintain the exact format for the labels.
- End with a Semicolon: Each Cypher statement must end with a semicolon (;).
- File Structure: The file should follow the format:

```bash
Question 1: <Your Question>
Cypher 1: <Your Cypher Statement>

Question 2: <Your Question>
Cypher 2: <Your Cypher Statement>
```
