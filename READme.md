# CoBGT: Combination of BERT, GraphSAGE, and Transformer Model

## Overview
This project is an implementation of the paper "Robust Text-to-Cypher Using Combination of BERT, GraphSAGE, and Transformer (CoBGT) Model." The [original paper](https://www.mdpi.com/2076-3417/14/17/7881) proposes a novel technique to translate natural language text into cypher queries for the Neo4j graph database.
Please note that this paper was not authored by me, and the original authors did not provide a public GitHub repository for reference. The code in this repository represents my interpretation of the ideas from the paper, and as such, it may not be fully accurate or complete. It is an ongoing work, specifically focusing on the relation and properties prediction module.

## Prerequisites
To run this project, you'll need to install [libcypher-parser](https://github.com/cleishm/libcypher-parser). For more information about how to install and use the package, you can refer to my [cypher parser](https://github.com/justinsiowqi/cypher-parser) repository.

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
