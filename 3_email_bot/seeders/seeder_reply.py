from utils.model import LLMModel                # Importing the LLM model
from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.llm_utils import LLMUtils            # Importing utilities for LLM manipulation
import json
import re                                       # Importing regular expressions module

class IncidentReplySeeder(LLMUtils):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_replies_from_email_list(self, email_list):
        formatted_problems = ""
        for i, email in enumerate(email_list, start=1):
            formatted_problems += (
                f"{i}. ID: {email['message_id']}\n"
                f"From: {email['from']}, Subject: {email['subject']}\n"
                f"Problem: {email['text']}\n\n"
            )

        # Create a mapping of indices to message_ids to ensure exact correspondence
        email_mapping = {i+1: email for i, email in enumerate(email_list)}
        
        prompt = (
            f"You are a technical assistant EXPERT of the 'ANIMAL FREEDOM' web platform.\n"
            f"You have received the following {len(email_list)} problems reported by different users:\n\n"
            f"{formatted_problems}\n"
            f"IMPORTANT: You MUST generate EXACTLY {len(email_list)} DIFFERENT and UNIQUE responses, one for EACH problem listed above.\n"
            f"For each problem, generate a DETAILED, TECHNICAL, and CREATIVE response with 100-150 words. Be technical but also empathetic.\n\n"
            f"GUIDELINES FOR RESPONSES:\n"
            f"- INVENT specific technical details for each problem (don't use generic responses)\n"
            f"- CREATE different technical solutions for each problem, even if they are similar\n"
            f"- MENTION specific tools such as DevTools, Debug Console, Element Inspector, etc.\n"
            f"- SUGGEST specific configurations to solve the problem (e.g., 'Disable extension X', 'Update to version Y')\n"
            f"- INCLUDE numbered and specific steps to solve the problem\n"
            f"- VARY the format and structure of the responses so they are not all the same\n"
            f"- PERSONALIZE each response based on the specific problem\n\n"
            f"EXAMPLES OF TECHNICAL RESPONSES (for reference only, create your own responses):\n\n"
            f"Example 1: 'We have identified that the 404 error when accessing reports on iOS is related to a conflict between Safari 15.2 and our REST API. We recommend: 1) Clear the browser cache in Settings > Safari > Clear History; 2) Check if iOS is updated to version 15.4+; 3) Try accessing using private browsing mode. If the problem persists, send us screenshots of the Error Console (open Safari > Settings > Advanced > Show Developer Menu > Developer > JavaScript Console).'\n\n"
            f"Example 2: 'The incompatibility with Chrome 98.1 during photo uploads is due to a limitation in the FileReader API when processing HEIC images. Solutions: 1) Convert the images to JPG using the Photos app before uploading; 2) Install our 'ANIMAL FREEDOM Helper' extension available in the Chrome Web Store; 3) Temporarily disable hardware acceleration in chrome://settings/system. Could you send us the error log (press F12 > Console) during the upload attempt for additional diagnosis?'\n\n"
            f"Return the results in a SINGLE JSON ARRAY WITHOUT using code blocks (no backticks).\n\n"
            f"IMPORTANT: \n"
            f"1. You MUST use EXACTLY the same values for 'message_id', 'from', and 'subject' that were provided for each problem.\n"
            f"2. DO NOT change or invent new values for these fields, as this will cause system failures.\n"
            f"3. Your response MUST be an ARRAY of JSON objects, even if it's just a single email.\n"
            f"4. Make sure your response starts with '[' and ends with ']'.\n"
            f"5. EACH response must be UNIQUE and DIFFERENT from the others - this is CRITICAL for model training.\n\n"
            f"""[
            {{
                "message_id": "email id",
                "from": "sender email",
                "subject": "email subject",
                "problem": "problem summary",
                "solution": "detailed and unique technical response for this specific problem"
            }},
            ...
            ]"""
                f"\nDo not add any other content besides the described JSON."
            )

        messages = [
            {
                "role": "system",
                "content": "You are a HIGHLY QUALIFIED technical expert who works in support for the 'ANIMAL FREEDOM' platform. You have extensive knowledge in web development, databases, networks, and operating systems. Your responses are DETAILED, TECHNICAL, and CREATIVE, always focused on solving problems efficiently. IMPORTANT: Each response you generate MUST be UNIQUE and DIFFERENT from the others, with specific technical details and customized solutions for each problem. You MUST vary the format, structure, and content of your responses so they are not generic. You MUST include specific steps, diagnostic tools, and technical configurations in your responses. You MUST invent plausible technical details when necessary to create more specific and useful responses."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        return response

def main():
    # Use the OpenAI model by default for better response quality
    llm_model = LLMModel(use_openai=True)
    seeder = IncidentReplySeeder(llm_model)

    print("Reading unread emails...")
    reader = EmailReader()
    emails = reader.read_emails(max_results=10, query='is:unread')
    sender = EmailSender()

    print(f"Total emails read: {len(emails)}")
    
    # Group emails by thread_id for better visualization
    threads = {}
    for email in emails:
        thread_id = email['thread_id']
        if thread_id not in threads:
            threads[thread_id] = []
        threads[thread_id].append(email)
    
    print(f"\nTotal: {len(threads)} threads containing {len(emails)} emails")
    
    # Limit the number of emails processed if necessary
    max_emails_to_process = 10
    if len(emails) > max_emails_to_process:
        print(f"Limiting processing to the first {max_emails_to_process} emails...")
        emails = emails[:max_emails_to_process]

    if not emails:
        print("No unread emails found. Exiting.")
        return

    # Group emails by subject to avoid duplicates
    emails_by_subject = {}
    for email in emails:
        subject = email['subject']
        if subject not in emails_by_subject:
            emails_by_subject[subject] = []
        emails_by_subject[subject].append(email)
    
    print("\n--- Emails grouped by subject ---")
    for subject, email_group in emails_by_subject.items():
        print(f"Subject '{subject}': {len(email_group)} email(s)")
    print("--- End of grouping ---\n")
    
    # Create a list of unique emails to process (one per subject)
    unique_emails = [email_group[0] for email_group in emails_by_subject.values()]
    
    if not unique_emails:
        print("No unique emails to process. Exiting.")
        return
    
    print(f"Processing {len(unique_emails)} unique emails in a single model call...")
    
    try:
        # Generate responses for all emails in a single call
        responses_json = seeder.generate_replies_from_email_list(unique_emails)
        
        # Extract and process the JSON responses
        try:
            # Try to extract the JSON from the response
            responses = json.loads(seeder.extract_json(responses_json))
            
            print(f"Responses generated successfully! Total: {len(responses)}")
            
            # Create a mapping of message_id to response
            responses_by_message_id = {}
            for response in responses:
                message_id = response.get('message_id')
                if message_id:
                    responses_by_message_id[message_id] = response
            
            # Send responses to corresponding emails
            for email in unique_emails:
                message_id = email['message_id']
                if message_id in responses_by_message_id:
                    response_data = responses_by_message_id[message_id]
                    solution = response_data.get('solution', '')
                    
                    original_msg = {
                        "from_": email['from'],
                        "subject": email['subject'],
                        "headers": {"Message-ID": message_id},
                        "thread_id": email['thread_id']
                    }
                    
                    print(f"Sending response to: {email['subject']}")
                    result = sender.reply_email(
                        original_msg=original_msg,
                        reply_body=solution
                    )
                    
                    if result:
                        print(f"Response successfully sent to: {email['from']}")
                    else:
                        print(f"Failed to send response to: {email['from']}")
                else:
                    print(f"Warning: No response found for email with message_id: {message_id}")
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Trying alternative extraction method...")
            
            # Use LLMUtils methods to try to extract the JSON
            try:
                # Create a temporary instance of LLMUtils
                llm_utils = LLMUtils()
                responses = llm_utils.robust_json_parse(responses_json)
                
                if isinstance(responses, list) and len(responses) > 0:
                    print(f"Alternative extraction successful! Total: {len(responses)}")
                    
                    # Process the extracted responses
                    for email in unique_emails:
                        # Find the corresponding response
                        matching_response = None
                        for response in responses:
                            if response.get('message_id') == email['message_id']:
                                matching_response = response
                                break
                        
                        if matching_response:
                            solution = matching_response.get('solution', '')
                            
                            original_msg = {
                                "from_": email['from'],
                                "subject": email['subject'],
                                "headers": {"Message-ID": email['message_id']},
                                "thread_id": email['thread_id']
                            }
                            
                            print(f"Sending response to: {email['subject']}")
                            result = sender.reply_email(
                                original_msg=original_msg,
                                reply_body=solution
                            )
                            
                            if result:
                                print(f"Response successfully sent to: {email['from']}")
                            else:
                                print(f"Failed to send response to: {email['from']}")
                        else:
                            print(f"Warning: No response found for email: {email['subject']}")
                else:
                    raise ValueError("Could not extract valid responses")
                    
            except Exception as e2:
                print(f"Error in alternative extraction: {e2}")
                print("Falling back to individual processing method...")
                
                # Process each email individually as fallback
                for email in unique_emails:
                    process_single_email(seeder, email, sender)
    
    except Exception as e:
        print(f"Error processing emails in batch: {e}")
        print("Falling back to individual processing method...")
        
        # Process each email individually as fallback
        for email in unique_emails:
            process_single_email(seeder, email, sender)

    print("\nEmail processing completed!")

def process_single_email(seeder, email, sender):
    """Process a single email as fallback"""
    print(f"Processing individually: {email['from']} - Subject: {email['subject']}")
    
    single_email_prompt = (
        f"You are a technical assistant EXPERT of the 'ANIMAL FREEDOM' web platform.\n"
        f"You have received the following problem reported by a user:\n\n"
        f"From: {email['from']}, Subject: {email['subject']}\n"
        f"Problem: {email['text']}\n\n"
        f"Generate a DETAILED, TECHNICAL, and CREATIVE response with 100-150 words. Be technical but also empathetic.\n\n"
        f"GUIDELINES FOR THE RESPONSE:\n"
        f"- INVENT specific technical details for the problem\n"
        f"- CREATE a personalized technical solution\n"
        f"- MENTION specific tools such as DevTools, Debug Console, etc.\n"
        f"- SUGGEST specific configurations to solve the problem\n"
        f"- INCLUDE numbered and specific steps to solve the problem\n\n"
        f"Return ONLY the response text, without additional formatting."
    )
    
    single_messages = [
        {"role": "system", "content": "You are a technical expert who creates detailed and personalized responses."},
        {"role": "user", "content": single_email_prompt}
    ]
    
    try:
        # Use higher temperature for more creative responses
        custom_response = seeder.llm_model.generate_completion(single_messages, temperature=0.8)
        
        original_msg = {
            "from_": email['from'],
            "subject": email['subject'],
            "headers": {"Message-ID": email['message_id']},
            "thread_id": email['thread_id']
        }
        
        print(f"Sending response to: {email['subject']}")
        result = sender.reply_email(
            original_msg=original_msg,
            reply_body=custom_response
        )
        
        if result:
            print(f"Individual response successfully sent to: {email['from']}")
        else:
            print(f"Failed to send individual response to: {email['from']}")
    except Exception as e:
        print(f"Error processing email individually: {e}")

if __name__ == "__main__":
    main()
