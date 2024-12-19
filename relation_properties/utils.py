def read_question_cypher(file_path):
    """
    Read question_cypher.txt file.
    
    Args:
        file_path: The file path of question_cypher.txt.
    
    Returns:
        question1: First question.
        cypher1:Cypher statement of question 1.
        question2: Second question.
        cypher2: Cypher statement of question 2.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    question1 = cypher1 = question2 = cypher2 = ""

    if len(lines) >= 4:
        question1 = lines[0].strip().replace("Question 1: ", "")
        cypher1 = lines[1].strip().replace("Cypher 1: ", "")
        question2 = lines[2].strip().replace("Question 2: ", "")
        cypher2 = lines[3].strip().replace("Cypher 2: ", "")

    return question1, cypher1, question2, cypher2