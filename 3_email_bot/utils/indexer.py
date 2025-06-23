from utils.reader import EmailReader
from chromadb.utils import embedding_functions
import chromadb 
import os
import re

def main():
    """
    Main function to index emails and their responses.
    This function cleans the existing collection and reindexes everything from scratch.
    """
    print("Indexing all emails...")
    
    # Configure ChromaDB
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Ensure directory exists
    os.makedirs("./db/chroma_persist", exist_ok=True)
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        
        # Check if collection exists and delete it
        try:
            collection = chromadb_client.get_collection("email_bot")
            print("Existing collection found. Deleting...")
            chromadb_client.delete_collection("email_bot")
            print("Collection deleted successfully.")
        except Exception as e:
            print(f"No existing collection found or error deleting: {e}")
        
        # Create a new collection
        collection = chromadb_client.create_collection("email_bot", embedding_function=default_ef)
        print("New collection created successfully.")
        
        # Read emails
        reader = EmailReader()
        emails = reader.read_emails(max_results=10, query='')
        print(f"Total emails read: {len(emails)}")
        
        # Group emails by thread_id
        threads = {}
        for email in emails:
            thread_id = email['thread_id']
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(email)
        
        print(f"Total threads: {len(threads)}")
        
        # Process each thread
        for thread_id, thread_emails in threads.items():
            print(f"\nProcessing thread {thread_id} with {len(thread_emails)} emails")
            
            if len(thread_emails) == 0:
                continue
                
            # The first email is the question
            original_email = thread_emails[0]
            question_id = f"{thread_id}-question"
            
            # Prepare question metadata, ensuring there are no None values
            question_metadata = {
                "from": original_email.get("from", ""),
                "subject": original_email.get("subject", ""),
                "text": original_email.get("text", ""),
                "type": "question",
                "thread_id": thread_id,
                "message_id": original_email.get("message_id", ""),
                "has_response": len(thread_emails) > 1
            }
            
            # Ensure no value is None
            for key, value in list(question_metadata.items()):
                if value is None:
                    question_metadata[key] = ""
            
            # Store the question
            collection.add(
                ids=[question_id],
                documents=[original_email["text"]],
                metadatas=[question_metadata]
            )
            
            print(f"Question indexed with ID: {question_id}")
            
            # If there are more emails, the last one is the answer
            if len(thread_emails) > 1:
                response_email = thread_emails[-1]
                response_id = f"{thread_id}-answer"
                
                # Prepare metadata, ensuring there are no None values
                response_metadata = {
                    "from": response_email.get("from", ""),
                    "subject": response_email.get("subject", ""),
                    "text": response_email.get("text", ""),
                    "type": "answer",
                    "thread_id": thread_id,
                    "message_id": response_email.get("message_id", ""),
                    "in_reply_to": original_email.get("message_id", ""),
                    "original_question": original_email.get("text", ""),
                    "original_subject": original_email.get("subject", "")
                }
                
                # Ensure no value is None
                for key, value in list(response_metadata.items()):
                    if value is None:
                        response_metadata[key] = ""
                
                # Store the answer
                collection.add(
                    ids=[response_id],
                    documents=[response_email["text"]],
                    metadatas=[response_metadata]
                )
                
                print(f"Answer indexed with ID: {response_id}")
                
                # Prepare updated question metadata, ensuring there are no None values
                updated_question_metadata = {
                    "from": original_email.get("from", ""),
                    "subject": original_email.get("subject", ""),
                    "text": original_email.get("text", ""),
                    "type": "question",
                    "thread_id": thread_id,
                    "message_id": original_email.get("message_id", ""),
                    "has_response": True,
                    "response_id": response_id
                }
                
                # Ensure no value is None
                for key, value in list(updated_question_metadata.items()):
                    if value is None:
                        updated_question_metadata[key] = ""
                
                # Update the question to indicate it has an answer
                collection.update(
                    ids=[question_id],
                    metadatas=[updated_question_metadata]
                )
                
                print(f"Question updated with reference to answer: {response_id}")
        
        print("\nIndexing completed successfully!")
        
    except Exception as e:
        print(f"Error during indexing: {e}")

def debug_question_answer_pairs():
    """
    Specific function to debug question-answer pairs in the database.
    Shows in detail each question and its corresponding answer.
    """
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_collection("email_bot")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        print("Check if the collection was created by running the main() function first.")
        return

    # Get all documents and metadata
    results = collection.get(include=["documents", "metadatas"])

    # Separate questions and answers
    questions = []
    answers = []
    
    for i, meta in enumerate(results["metadatas"]):
        if meta.get("type") == "question":
            questions.append((i, results["ids"][i], results["documents"][i], meta))
        elif meta.get("type") == "answer":
            answers.append((i, results["ids"][i], results["documents"][i], meta))
    
    print(f"\n=== DEBUG SUMMARY ===")
    print(f"Total documents: {len(results['ids'])}")
    print(f"Questions found: {len(questions)}")
    print(f"Answers found: {len(answers)}")
    print("=" * 50)
    
    # Check if there are answers
    if len(answers) == 0:
        print("\nWARNING: No answers found in the database!")
        print("Check if the indexing process is correctly identifying the answers.")
        print("Possible causes:")
        print("1. Response emails are not being recognized as answers")
        print("2. The condition 'is_reply or has_citation' is not being satisfied")
        print("3. There are no response emails in the threads")
        print("\nCheck the original emails and make sure there are responses.")
    else:
        print(f"\n{len(answers)} answers found in the database.")
    
    # Show all answers in detail
    print("\n=== ALL ANSWERS FOUND ===")
    for i, id_, doc, meta in answers:
        print(f"\nAnswer ID: {id_}")
        print(f"Thread ID: {meta.get('thread_id')}")
        print(f"From: {meta.get('from')}")
        print(f"Subject: {meta.get('subject')}")
        print(f"In reply to: {meta.get('in_reply_to')}")
        print(f"Full answer text:\n{doc}")
        print("-" * 50)
    
    # Show all question-answer pairs
    print("\n=== DETAILED QUESTION-ANSWER PAIRS ===")
    for i, id_, doc, meta in questions:
        print(f"\nQuestion ID: {id_}")
        print(f"Thread ID: {meta.get('thread_id')}")
        print(f"From: {meta.get('from')}")
        print(f"Subject: {meta.get('subject')}")
        print(f"Has answer: {meta.get('has_response', False)}")
        print(f"Full question text:\n{doc}")
        
        # If it has an answer, show it
        if meta.get("has_response") and meta.get("response_id"):
            response_id = meta.get("response_id")
            print(f"Referenced Response ID: {response_id}")
            
            # List all available response IDs for debugging
            available_response_ids = [r_id for _, r_id, _, _ in answers]
            print(f"Available response IDs: {available_response_ids}")
            
            # Check if the response ID is in the list of available IDs
            if response_id in available_response_ids:
                print(f"Response ID found in the list of available responses")
            else:
                print(f"Response ID NOT found in the list of available responses")
            
            # Find the corresponding answer
            found_response = False
            for j, r_id, r_doc, r_meta in answers:
                print(f"Comparing '{r_id}' with '{response_id}'")
                if r_id == response_id:
                    found_response = True
                    print(f"\nCorresponding answer:")
                    print(f"From: {r_meta.get('from')}")
                    print(f"Subject: {r_meta.get('subject')}")
                    print(f"Full answer text:\n{r_doc}")
                    break
            
            if not found_response:
                print("\nWARNING: Referenced answer not found!")
                print("Trying to find by thread_id instead of response_id...")
                
                # Try to find by thread_id
                thread_id = meta.get("thread_id")
                expected_response_id = f"{thread_id}-answer"
                print(f"Thread ID: {thread_id}, Expected Response ID: {expected_response_id}")
                
                for j, r_id, r_doc, r_meta in answers:
                    if r_id == expected_response_id or r_meta.get("thread_id") == thread_id:
                        print(f"\nAnswer found by thread_id:")
                        print(f"ID: {r_id}")
                        print(f"From: {r_meta.get('from')}")
                        print(f"Subject: {r_meta.get('subject')}")
                        print(f"Full answer text:\n{r_doc}")
                        
                        # Fix the problem by updating the collection
                        print("\nFixing the reference in the collection...")
                        try:
                            default_ef = embedding_functions.DefaultEmbeddingFunction()
                            chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
                            collection = chromadb_client.get_collection("email_bot")
                            
                            # Update the question metadata with the correct answer ID
                            collection.upsert(
                                ids=[id_],
                                documents=[doc],
                                metadatas=[{
                                    **meta,
                                    "response_id": r_id
                                }]
                            )
                            print("Reference fixed successfully!")
                        except Exception as e:
                            print(f"Error fixing reference: {e}")
                        
                        break
                else:
                    print("\nCould not find an answer for this question.")
        else:
            print("\nThis question has no associated answer.")
        
        print("-" * 50)

def search_questions(query_text, n_results=1):
    """
    Searches for questions similar to the query text and returns the corresponding questions and answers.
    
    Args:
        query_text (str): The query text to search for similar questions
        n_results (int): Number of results to return
        
    Returns:
        list: List of dictionaries containing questions and answers
    """
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_collection("email_bot")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        print("Check if the collection was created by running the main() function first.")
        return []
    
    # Search only for documents of type "question"
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"type": "question"}
    )
    
    qa_pairs = []
    
    if not results["ids"] or len(results["ids"][0]) == 0:
        print("No results found.")
        return []
    
    print(f"\n=== SEARCH RESULTS FOR: '{query_text}' ===")
    
    for i, (id_, doc, meta) in enumerate(zip(results["ids"][0], results["documents"][0], results["metadatas"][0])):
        print(f"\n{i+1}) Question: {meta.get('subject')}")
        print(f"   From: {meta.get('from')}")
        print(f"   Similarity: {results['distances'][0][i]}")
        print(f"   Text: {doc[:150]}...")
        
        qa_pair = {
            "question_id": id_,
            "question": doc,
            "question_subject": meta.get("subject"),
            "question_from": meta.get("from"),
            "has_response": meta.get("has_response", False),
            "response": None,
            "response_text": None
        }
        
        # If it has an answer, find and show it
        if meta.get("has_response") and meta.get("response_id"):
            response_id = meta.get("response_id")
            response_results = collection.get(ids=[response_id], include=["documents", "metadatas"])
            
            if response_results["ids"]:
                resp_doc = response_results["documents"][0]
                resp_meta = response_results["metadatas"][0]
                
                print(f"\n   ANSWER:")
                print(f"   From: {resp_meta.get('from')}")
                print(f"   Subject: {resp_meta.get('subject')}")
                print(f"   Full answer text:\n{resp_doc}")
                
                qa_pair["response"] = resp_doc
                qa_pair["response_from"] = resp_meta.get("from")
                qa_pair["response_subject"] = resp_meta.get("subject")
            else:
                print("   (Referenced answer not found)")
        else:
            print("   (No answer)")
        
        print("-" * 40)
        qa_pairs.append(qa_pair)
    
    return qa_pairs

if __name__ == "__main__":

    # Uncomment the function you want to execute
    # Example of use: first index the emails and then search for a question

    main()  # Index all emails
    # debug_question_answer_pairs()  # Check question-answer pairs
    # search_questions("system freezing when adding photos", n_results=1)  # Search for similar questions
