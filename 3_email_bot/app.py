from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.model import LLMModel
from utils.llm_utils import LLMUtils
from chromadb.utils import embedding_functions
import chromadb
import json
import os

def main():
    """
    Main function that processes unread emails, searches for similar questions in the knowledge base,
    finds associated answers and sends them as a response to the original email.
    """
    reader = EmailReader()
    sender = EmailSender()
    
    # Read unread emails
    emails = reader.read_emails(max_results=10, query='is:unread')
    print(f"Found {len(emails)} new emails to process.")
    
    if not emails:
        print("No new emails to process.")
        return
    
    # Configure ChromaDB
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        # Ensure directory exists
        os.makedirs("./db/chroma_persist", exist_ok=True)
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_or_create_collection("email_bot", embedding_function=default_ef)
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Make sure the database was created by running the indexer.py script first.")
        return
    
    # Check if there are documents in the collection
    try:
        collection_info = collection.get(limit=1)
        if not collection_info["ids"]:
            print("The collection is empty. Run the indexer.py script to index emails first.")
            return
    except Exception as e:
        print(f"Error checking collection: {e}")
        return
    
    # Process each email
    for i, email in enumerate(emails, 1):
        print(f"\n[{i}/{len(emails)}] Processing email from {email['from']} - Subject: {email['subject']}")

        # Prepare query text - use only the first 200 characters to avoid noise
        query_text = email['text'][:200] if len(email['text']) > 200 else email['text']
        
        print(f"\nQuery text: {query_text[:50]}...")
        
        # Semantic search for similar questions
        try:
            # First, get all available questions for analysis
            all_questions = collection.get(
                where={"$and": [
                    {"type": {"$eq": "question"}},
                    {"has_response": {"$eq": True}}
                ]},
                include=["metadatas"]
            )
            
            print(f"Total available questions with answers: {len(all_questions['ids'])}")

            # Semantic search with only 1 result (the most similar)
            results = collection.query(
                query_texts=[query_text],
                n_results=1,  # Get only the most similar result
                where={"$and": [
                    {"type": {"$eq": "question"}},
                    {"has_response": {"$eq": True}}
                ]}  # Ensure we only get questions with answers
            )
            
            if not results["ids"] or len(results["ids"][0]) == 0:
                print("No similar questions found in the knowledge base.")
                continue
                
            # Define a similarity threshold (lower value means more similar)
            # ChromaDB uses distance, so lower values are better
            similarity_threshold = 1.5  # Adjust this value as needed
            
            # Filter results by similarity
            filtered_results = {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": []
            }
            
            for i, distance in enumerate(results["distances"][0]):
                if distance < similarity_threshold:
                    filtered_results["ids"].append(results["ids"][0][i])
                    filtered_results["documents"].append(results["documents"][0][i])
                    filtered_results["metadatas"].append(results["metadatas"][0][i])
                    filtered_results["distances"].append(distance)
            
            if not filtered_results["ids"]:
                print(f"No questions with sufficient similarity found (threshold: {similarity_threshold}).")
                continue
                
            print(f"Found {len(filtered_results['ids'])} questions with sufficient similarity.")

            # Show found questions with their similarity scores
            print("\n=== SIMILAR QUESTIONS FOUND ===")
            
            # Variable to store the response to be sent
            response_to_send = None
            response_meta = None
            
            # Process only the most similar question
            if filtered_results["ids"]:
                question_id = filtered_results["ids"][0]
                question_doc = filtered_results["documents"][0]
                question_meta = filtered_results["metadatas"][0]
                distance = filtered_results["distances"][0]
                
                print(f"\nMost similar question: {question_meta.get('subject')}")
                print(f"Similarity: {distance}")
                print(f"ID: {question_id}")
                print(f"Thread ID: {question_meta.get('thread_id')}")
                print(f"Has answer: {question_meta.get('has_response', False)}")
                
                # If the question has an associated answer, retrieve and show it
                if question_meta.get("has_response") and question_meta.get("response_id"):
                    response_id = question_meta.get("response_id")
                    
                    # Get the answer by ID
                    response_results = collection.get(
                        ids=[response_id],
                        include=["documents", "metadatas"]
                    )
                    
                    if response_results["ids"]:
                        resp_doc = response_results["documents"][0]
                        resp_meta = response_results["metadatas"][0]
                        
                        print(f"\nASSOCIATED ANSWER:")
                        print(f"From: {resp_meta.get('from')}")
                        print(f"Subject: {resp_meta.get('subject')}")
                        print(f"Answer text:\n{resp_doc[:200]}...")
                        
                        # Store the response for sending
                        response_to_send = resp_doc
                        response_meta = resp_meta
                    else:
                        print(f"Referenced answer (ID: {response_id}) not found!")
                else:
                    print("This question has no associated answer.")
                
                # If we found a response, send it
                if response_to_send:
                    print("\n=== SENDING RESPONSE AUTOMATICALLY ===")
                    
                    # Prepare the original email for response
                    original_msg = {
                        "from_": email['from'],
                        "subject": email['subject'],
                        "headers": {"Message-ID": email['message_id']},
                        "thread_id": email['thread_id']
                    }
                    
                    # Send the response
                    try:
                        result = sender.reply_email(
                            original_msg=original_msg,
                            reply_body=response_to_send
                        )
                        
                        if result:
                            print(f"Response successfully sent to {email['from']}!")
                            
                            # Mark the original email as read
                            if 'id' in email:
                                mark_result = reader.mark_as_read(message_id=email['id'])
                                if mark_result:
                                    print(f"Email successfully marked as read!")
                                else:
                                    print(f"WARNING: Could not mark the email as read.")
                            else:
                                # Fallback to thread_id if message id is not available
                                mark_result = reader.mark_as_read(thread_id=email['thread_id'])
                                if mark_result:
                                    print(f"Entire thread successfully marked as read!")
                                else:
                                    print(f"WARNING: Could not mark the thread as read.")
                        else:
                            print(f"ERROR: Failed to send response to {email['from']}. Check credentials and permissions.")
                    except Exception as e:
                        print(f"ERROR: Error sending response: {e}")
            
        except Exception as e:
            print(f"Error searching for similar questions: {e}")
    
    print("\nEmail processing completed!")

def debug_collection():
    """
    Function to debug the ChromaDB collection, showing information about stored documents.
    """
    try:
        # Configure ChromaDB
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_or_create_collection("email_bot", embedding_function=default_ef)
        
        # Get all documents
        results = collection.get(include=["documents", "metadatas"])
        
        # Count questions and answers
        questions = [meta for meta in results["metadatas"] if meta.get("type") == "question"]
        answers = [meta for meta in results["metadatas"] if meta.get("type") == "answer"]
        questions_with_answers = [p for p in questions if p.get("has_response") == True]
        
        print(f"\n=== COLLECTION SUMMARY ===")
        print(f"Total documents: {len(results['ids'])}")
        print(f"Questions: {len(questions)}")
        print(f"Answers: {len(answers)}")
        print(f"Questions with answers: {len(questions_with_answers)}")
        
        # Check for discrepancies
        if len(questions_with_answers) != len(answers):
            print(f"\nALERT: There is a discrepancy between questions with answers ({len(questions_with_answers)}) and answers ({len(answers)})!")
        
        # Show all available answers
        print("\n=== ALL AVAILABLE ANSWERS ===")
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("type") == "answer":
                print(f"\n{i+1}) ID: {results['ids'][i]}")
                print(f"   From: {meta.get('from', 'Unknown')}")
                print(f"   Subject: {meta.get('subject', 'No subject')}")
                print(f"   Thread ID: {meta.get('thread_id', 'Unknown')}")
                print(f"   In reply to: {meta.get('in_reply_to', 'Unknown')}")
                print(f"   Text: {results['documents'][i][:100]}...")
        
        # Show all question-answer pairs
        print("\n=== ALL QUESTION-ANSWER PAIRS ===")
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("type") == "question" and meta.get("has_response") == True:
                print(f"\nQuestion: {meta.get('subject')}")
                print(f"ID: {results['ids'][i]}")
                print(f"Thread ID: {meta.get('thread_id')}")
                print(f"Response ID: {meta.get('response_id')}")
                print(f"Text: {results['documents'][i][:100]}...")
                
                # Find the answer
                response_id = meta.get("response_id")
                if response_id:
                    for j, id_ in enumerate(results["ids"]):
                        if id_ == response_id:
                            resp_meta = results["metadatas"][j]
                            resp_doc = results["documents"][j]
                            print(f"\nCorresponding answer:")
                            print(f"From: {resp_meta.get('from')}")
                            print(f"Text: {resp_doc[:150]}...")
                            break
                    else:
                        print("\nWARNING: Referenced answer not found!")
                        
                        # Try to find by thread_id
                        thread_id = meta.get("thread_id")
                        expected_response_id = f"{thread_id}-answer"
                        print(f"Looking for alternative ID: {expected_response_id}")
                        
                        for j, id_ in enumerate(results["ids"]):
                            if id_ == expected_response_id:
                                resp_meta = results["metadatas"][j]
                                resp_doc = results["documents"][j]
                                print(f"\nAnswer found with alternative ID:")
                                print(f"From: {resp_meta.get('from')}")
                                print(f"Text: {resp_doc[:150]}...")
                                print(f"\nWARNING: Problem detected: The question references '{response_id}' but the answer has ID '{expected_response_id}'")
                                break
                
                print("-" * 60)
        
        # Show similarity statistics between questions
        if len(questions) > 1:
            print("\n=== QUESTION SIMILARITY TEST ===")
            print("Testing similarity between questions to check for semantic duplicates...")
            
            # Get only the question texts
            question_texts = []
            question_ids = []
            for i, meta in enumerate(results["metadatas"]):
                if meta.get("type") == "question":
                    question_texts.append(results["documents"][i])
                    question_ids.append(results["ids"][i])
            
            # Test similarity between each pair of questions
            for i in range(len(question_texts)):
                query_results = collection.query(
                    query_texts=[question_texts[i]],
                    n_results=len(question_texts),
                    where={"type": {"$eq": "question"}}
                )
                
                print(f"\nSimilarity for question {i+1} (ID: {question_ids[i]}):")
                for j, (id_, distance) in enumerate(zip(query_results["ids"][0], query_results["distances"][0])):
                    if j > 0:  # Skip the question itself
                        print(f"  - Similarity with {id_}: {distance}")
                        if distance < 0.1:  # Very low value indicates high similarity
                            print(f"    ALERT: Very similar questions detected!")
        
    except Exception as e:
        print(f"Error debugging collection: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        print("Debug mode activated. Showing collection information...")
        debug_collection()
    else:
        print("Normal mode. Processing unread emails...")
        main()
        
    # print("\nTo debug the collection, run: python app.py debug")
