from utils.model import LLMModel                # Importing the LLM model
from utils.sender_smtp import EmailSender       # Importing EmailSender to send emails via smtp
from dotenv import load_dotenv
from utils.llm_utils import LLMUtils            # Importing utilities for LLM manipulation
import json
import os
import re                                       # Importing regular expressions module
load_dotenv()

class IncidentSeeder(LLMUtils):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_incidents(self):
        prompt = (
            "Generate a list with EXACTLY 10 DETAILED and REALISTIC technical incidents reported by users of our 'ANIMAL FREEDOM' dog and pedigree management web system.\n\n"
            "IMPORTANT: Your response MUST contain EXACTLY 10 incidents, no more, no less.\n\n"
            "GUIDELINES FOR INCIDENTS:\n"
            "- Each incident must be UNIQUE and SPECIFIC\n"
            "- Include TECHNICAL DETAILS such as browsers, versions, specific devices\n"
            "- Mention SPECIFIC FUNCTIONALITIES of the system (pedigree registration, photo upload, report generation, etc.)\n"
            "- Include STEPS that the user tried to solve the problem\n"
            "- Describe SPECIFIC BEHAVIORS of the system (exact error messages, unexpected behaviors)\n"
            "- Use appropriate TECHNICAL TERMINOLOGY\n"
            "- Include IMPACT on the user's work\n\n"
            
            "Each incident should contain ONLY:\n"
            "- A SPECIFIC, TECHNICAL, and DETAILED title in the 'title' field\n"
            "- A first-person description in the 'description' field, with EXACTLY 200 words, rich in technical details\n\n"
            
            "EXAMPLES OF GOOD TITLES:\n"
            "- '404 Error when trying to access pedigree reports on iOS devices'\n"
            "- 'Failure in synchronizing dog data with pedigree across different devices'\n"
            "- 'System incompatibility with Firefox 98.2 browser when uploading photos'\n\n"
            
            "CRITICAL JSON FORMATTING RULES:\n"
            "1. Use ONLY double quotes (\") for keys and values, NEVER single quotes (')\n"
            "2. Each object MUST end with a comma (,) except the last one\n"
            "3. NEVER use semicolons (;) anywhere in the JSON\n"
            "4. Do not include special or non-ASCII characters in the JSON\n"
            "5. Make sure each key and value are correctly enclosed in double quotes\n"
            "6. Do not use line breaks within text values\n\n"
            
            "The response must be STRICTLY a pure JSON array. Do not include any explanation, title, text outside the JSON, markdown, or line breaks before or after.\n"
            "Example of expected response:\n"
            "[\n"
            "  {\n"
            '    "title": "Error saving new dog",\n'
            '    "description": "I tried to register a new dog and an error message appeared..."\n'
            "  },\n"
            "  {\n"
            '    "title": "Failed to generate pedigree report",\n'
            '    "description": "When trying to generate the pedigree report for my dog..."\n'
            "  },\n"
            "  ... (8 more similar objects) ...\n"
            "]"
        ) 

        messages = [
            {
                "role": "system",
                "content": "You are an EXPERT in creating EXACTLY 10 realistic simulations of technical problems in JSON format. NEVER use markdown formatting. ALWAYS return ONLY a valid JSON array, starting with '[' and ending with ']'. Each object in the array must have exactly two properties: 'title' and 'description'. Do not include any text outside the JSON. Do not use headers, bold, italic, or any other formatting. Just pure JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        
        # Print the first 200 characters of the response for diagnosis
        print(f"First 200 characters of the response: {response[:200]}")
        
        # Direct approach: extract only what appears to be JSON
        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        
        if json_start >= 0 and json_end > json_start:
            # Extract what appears to be JSON
            json_text = response[json_start:json_end]
            print(f"Extracted JSON (first 100 characters): {json_text[:100]}...")
            
            # Try to fix common problems
            json_text = json_text.replace(";", ",")
            json_text = json_text.replace("'", '"')
            
            # Extreme approach: manually extract each object and rebuild the JSON
            try:
                print("Attempting manual object extraction...")
                # Extract all objects that start with { and end with }
                objects = re.findall(r'{[^{}]*"title"[^{}]*"description"[^{}]*}', json_text, re.DOTALL)
                
                if objects:
                    print(f"Found {len(objects)} potential objects.")
                    valid_objects = []
                    
                    for i, obj_text in enumerate(objects):
                        # Clean each object individually
                        clean_obj = obj_text.replace(";", ",").replace("'", '"')
                        
                        # Ensure all keys are in double quotes
                        clean_obj = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', clean_obj)
                        
                        # Remove extra commas before closing braces
                        clean_obj = re.sub(r',\s*}', '}', clean_obj)
                        
                        try:
                            # Try to parse the object
                            obj = json.loads(clean_obj)
                            
                            # Check if it has the necessary fields
                            if "title" in obj and "description" in obj:
                                valid_objects.append(obj)
                                print(f"Object {i+1} valid: {obj['title'][:30]}...")
                        except json.JSONDecodeError as e:
                            print(f"Object {i+1} invalid: {e}")
                    
                    if valid_objects:
                        print(f"Manual extraction successful! {len(valid_objects)} valid objects.")
                        return json.dumps(valid_objects)
            except Exception as e:
                print(f"Error in manual extraction: {e}")
            
            # If manual extraction fails, try to parse the corrected JSON
            try:
                incidents = json.loads(json_text)
                print(f"JSON parsed successfully! Found {len(incidents)} incidents.")
                clean_response = json.dumps(incidents)
                return clean_response
            except json.JSONDecodeError as e:
                print(f"Error parsing extracted JSON: {e}")
                
                # Try to fix the specific error
                if "Expecting ',' delimiter" in str(e):
                    error_match = re.search(r'line (\d+) column (\d+)', str(e))
                    if error_match:
                        error_line = int(error_match.group(1))
                        error_col = int(error_match.group(2))
                        
                        print(f"Trying to fix specific error on line {error_line}, column {error_col}...")
                        
                        # Split the text into lines
                        lines = json_text.split('\n')
                        
                        # Check if the error line is within bounds
                        if 0 < error_line <= len(lines):
                            # Adjust for zero-based index
                            line_idx = error_line - 1
                            problematic_line = lines[line_idx]
                            
                            print(f"Problematic line: {problematic_line}")
                            
                            # Insert a comma at the error position
                            if error_col <= len(problematic_line):
                                fixed_line = problematic_line[:error_col] + ',' + problematic_line[error_col:]
                                lines[line_idx] = fixed_line
                                print(f"Fixed line: {fixed_line}")
                                
                                # Rebuild the JSON
                                fixed_json = '\n'.join(lines)
                                
                                try:
                                    incidents = json.loads(fixed_json)
                                    print(f"JSON fixed successfully! Found {len(incidents)} incidents.")
                                    return json.dumps(incidents)
                                except json.JSONDecodeError as e2:
                                    print(f"Still error after specific correction: {e2}")
                # Continue with other approaches
        
        # If the direct approach fails, try more robust methods
        try:
            # Try to use the robust JSON parsing method
            incidents = self.robust_json_parse(response)
            print(f"JSON processed successfully! Found {len(incidents)} incidents.")
            clean_response = json.dumps(incidents)
            return clean_response
        except Exception as e:
            print(f"Error in robust analysis: {e}")
            
            # Try to extract and clean the JSON manually
            try:
                clean_response = self.extract_json_from_response(response)
                clean_response = self.clean_json_string(clean_response)
                
                # Check if the JSON is valid
                if self.is_valid_json(clean_response):
                    incidents = json.loads(clean_response)
                    print(f"JSON extracted and cleaned successfully! Found {len(incidents)} incidents.")
                else:
                    # Try more aggressive cleaning
                    clean_response = clean_response.replace(";", ",").replace("'", '"')
                    if self.is_valid_json(clean_response):
                        incidents = json.loads(clean_response)
                        print(f"JSON aggressively cleaned successfully! Found {len(incidents)} incidents.")
                    else:
                        # Try the emergency method
                        try:
                            incidents = self.emergency_json_fix(clean_response)
                            if incidents:
                                clean_response = json.dumps(incidents)
                                print(f"Emergency extraction successful! Found {len(incidents)} incidents.")
                            else:
                                # Last attempt: manual JSON construction
                                print("Attempting manual JSON construction...")
                                incidents = self.manual_json_construction(response)
                                if incidents:
                                    clean_response = json.dumps(incidents)
                                    print(f"Manual construction successful! Found {len(incidents)} incidents.")
                                    return clean_response
                                else:
                                    raise ValueError("Emergency method failed")
                        except Exception as ex:
                            print(f"All extraction attempts failed: {ex}")
                            # Return an empty array to indicate failure
                            return "[]"
            except Exception as e:
                print(f"Error extracting JSON: {e}")
                return "[]"
        
        # If we got here, we have a valid JSON in clean_response
        try:
            incidents = json.loads(clean_response)
            # Ensure we have exactly 10 incidents
            if len(incidents) > 10:
                print(f"The model generated {len(incidents)} incidents. Limiting to 10...")
                incidents = incidents[:10]
                return json.dumps(incidents)
            elif len(incidents) < 10:
                print(f"The model generated only {len(incidents)} incidents instead of 10. Generating the remaining {10 - len(incidents)}...")
                
                # Generate the missing incidents
                missing_count = 10 - len(incidents)
                additional_prompt = (
                    f"Generate EXACTLY {missing_count} ADDITIONAL and DIFFERENT technical incidents from the following that have already been generated:\n\n"
                    f"{json.dumps(incidents, indent=2)}\n\n"
                    f"The new incidents should follow the same format, but be completely different in content.\n"
                    f"Return only a JSON array with the {missing_count} NEW incidents, without including the previous ones.\n"
                    f"Each incident should have a specific technical title and a detailed first-person description."
                )
                
                additional_messages = [
                    {
                        "role": "system",
                        "content": "You are an EXPERT in creating realistic simulations of technical problems. Generate exactly the requested number of incidents, no more, no less."
                    },
                    {
                        "role": "user",
                        "content": additional_prompt
                    }
                ]
                
                additional_response = self.llm_model.generate_completion(additional_messages)
                
                # Use robust methods to analyze the additional response
                try:
                    additional_incidents = self.robust_json_parse(additional_response)
                    print(f"Additional JSON processed successfully! Found {len(additional_incidents)} additional incidents.")
                    
                    # Ensure we don't take more than we need
                    additional_incidents = additional_incidents[:missing_count]
                    # Combine the original incidents with the additional ones
                    incidents.extend(additional_incidents)
                    print(f"Now we have {len(incidents)} incidents in total.")
                    return json.dumps(incidents)
                except Exception as e:
                    print(f"Error processing additional incidents: {e}")
                    # Continue with the incidents we already have
                    print("Continuing with the incidents already generated.")
            
            return clean_response
        except json.JSONDecodeError as e:
            print(f"Error processing JSON: {e}")

        # Try to ask the model for correction
        correction_prompt = (
            "Correct the content below so that it is a valid JSON array, containing EXACTLY 10 objects with the keys 'title' and 'description'.\n"
            "Remove any text outside the JSON, and return only the JSON with EXACTLY 10 items:\n\n"
            f"{response}"
        )
        correction_messages = [{"role": "user", "content": correction_prompt}]
        corrected = self.llm_model.generate_completion(correction_messages)
        clean_corrected = self.extract_json(corrected)

        if self.is_valid_json(clean_corrected):
            # Check again the number of incidents after correction
            try:
                incidents = json.loads(clean_corrected)
                if len(incidents) > 10:
                    print(f"After correction, the model still generated {len(incidents)} incidents. Limiting to 10...")
                    incidents = incidents[:10]
                    return json.dumps(incidents)
            except json.JSONDecodeError:
                pass
            return clean_corrected
        else:
            print("Error: The model could not generate a valid JSON even after correction.")
            return "[]  # Failed to generate valid JSON even after correction"

def get_default_incidents():
    """
    Returns a list of default incidents to use as fallback.
    """
    return [
        {
            "title": "404 Error when trying to access pedigree reports on iOS devices",
            "description": "I'm trying to access my dog's pedigree reports through my iPhone 13 with iOS 16.2, but I constantly receive a 404 error. I've tried using different browsers (Safari, Chrome, and Firefox), clearing cache and cookies, and even reinstalling the apps, but the problem persists. Interestingly, I can access the reports normally through my Windows laptop. This issue is preventing me from checking important information about my dog's lineage during dog show visits. The exact error message is: '404 Error: Resource not found. The requested report is not available at this time.' I urgently need a solution, as I have an important show in three days."
        },
        {
            "title": "Failure in synchronizing dog data with pedigree across different devices",
            "description": "I updated my dog's information (vaccines, weight, height) on my Android tablet (Samsung Galaxy Tab S7, Android 12), but when I access the system from my computer (Windows 11, Chrome 98.0.4758.102), the changes don't appear. I've tried forcing synchronization using the 'Update data' button in the interface, cleared the browser cache, and even waited 24 hours, but the information remains outdated. The developer console shows the error: 'SyncError: Failed to update record #45872 - Database conflict'. This issue is affecting my work as a breeder, as I need consistent access to updated data across all devices to properly manage my kennel."
        },
        {
            "title": "System incompatibility with Firefox 98.2 browser when uploading photos",
            "description": "I'm trying to upload photos of my dog using Firefox 98.2 on Windows 10, but the system consistently freezes after selecting the images. The progress indicator reaches 45% and then freezes, followed by an error message: 'Image processing failure: unsupported format'. The same images (JPG, 2MB each) work perfectly when I use Chrome. I've tried disabling all Firefox extensions, clearing the cache, and even reinstalling the browser, but the problem persists. Inspecting the console, I see the error: 'Uncaught TypeError: Cannot read property 'processImage' of undefined'. This is delaying the update of my dogs' profiles for the next exhibition event."
        },
        {
            "title": "Error when trying to generate pedigree certificate in PDF format",
            "description": "When I try to generate the PDF pedigree certificate for my newly registered dog, the system processes for approximately 30 seconds and then displays the message: 'Document generation error: Failed to render lineage chart'. I'm using a MacBook Pro with macOS Monterey 12.3 and Safari 15.4. I've tried using Chrome and Firefox, but the result is the same. The problem occurs specifically with this dog; I can generate certificates for other animals without issues. Analyzing this animal's history, I noticed it has a particularly extensive lineage (7 complete generations), which may be causing the problem. I need this certificate for an international exhibition next week."
        },
        {
            "title": "System freezes when trying to add more than 5 photos simultaneously to dog gallery",
            "description": "I'm trying to add 8 high-resolution photos (each approximately 4MB, JPEG format) simultaneously to my dog's gallery, but the system completely freezes. The browser (Chrome 99.0.4844.51 on Windows 11) becomes unresponsive for about 2 minutes and then displays the message: 'This page is not responding. Wait or end process'. In the developer console, I see the error: 'OutOfMemoryError: Allocation failed - JavaScript heap out of memory'. If I add the photos one by one, it works, but it's extremely inefficient. I've tried reducing the image resolution and using different browsers, but the problem persists with multiple uploads."
        },
        {
            "title": "Failure to export dog medical history to CSV format",
            "description": "I'm trying to export my dog's complete medical history to a CSV file to share with the veterinarian, but the system generates a corrupted file. When I try to open the file in Excel or Google Sheets, I receive the message: 'The file is damaged and cannot be opened'. Analyzing the generated file, I noticed it contains strange characters at the beginning (�PNG) and seems to be mixing formats. I'm using a Dell XPS 15 with Windows 10 Pro and Edge 99.0.1150.46. I've tried different browsers and even accessing from another computer, but the problem persists. This dog's history is particularly extensive, with 47 medical entries over 6 years."
        },
        {
            "title": "Validation error when trying to register dog with existing microchip",
            "description": "I'm trying to register a new dog in the system, but I receive the error: 'Validation failed: Microchip number 900182000123456 is already registered in the system'. The problem is that this dog is mine and has just been transferred to me by another breeder who also uses the system. I've checked with the previous breeder and he confirmed that he removed the dog from his system before the transfer. I tried contacting technical support, but I haven't received a response after 3 days. I need to register this animal urgently to participate in an exhibition next week. I'm using an HP Pavilion with Windows 10 and Chrome 98.0.4758.102."
        },
        {
            "title": "Broken user interface when accessing the system on ultrawide screen (21:9)",
            "description": "I'm using an LG 34WN750 ultrawide monitor with 3440x1440 resolution (21:9 aspect ratio) and the system interface layout is completely broken. Page elements are overlapping, some buttons are inaccessible, and the side menu partially disappears under other elements. I've tried different browsers (Chrome, Firefox, and Edge), adjusting the page zoom, and even changing the monitor resolution, but the problem persists. Interestingly, when I connect my laptop to a standard 16:9 monitor, everything works perfectly. This issue is significantly affecting my productivity, as I need to constantly switch between monitors to use the system properly."
        },
        {
            "title": "System incorrectly calculates dog age for exhibitions",
            "description": "I discovered that the system is incorrectly calculating my dog's age for exhibition categorization purposes. My dog was born on 03/15/2020, but the system is considering it as 6 months younger than it actually is. This caused it to be entered in the wrong category at a recent exhibition, which resulted in its disqualification. Upon closer analysis, I noticed that the problem only occurs with dogs born in the first quarter of 2020. I'm using a Lenovo ThinkPad with Windows 11 and Firefox 97.0.1. I've tried updating the dog's data and even deleting and re-registering it, but the calculation remains incorrect."
        },
        {
            "title": "Failure when trying to connect system account with mobile app",
            "description": "I'm trying to connect my ANIMAL FREEDOM system account with the mobile app (version 2.3.5 on Android 12, Samsung Galaxy S22). When I enter my credentials in the app and click 'Connect', I receive the message: 'Authentication failure: Invalid token'. I've verified that my credentials are correct (I can log in normally through the browser), reinstalled the app, cleared the app data, and even reset my phone's network settings. In the app's error log, I see: 'OAuth2Error: Invalid grant_type parameter'. This issue is preventing me from receiving important notifications about my dogs and accessing information when I'm at exhibitions without access to a computer."
        }
    ]

def main():
    # Initialize models with OpenAI for better quality
    llm_model = LLMModel(use_openai=True)
    seeder = IncidentSeeder(llm_model)
    sender = EmailSender(email=os.getenv("SEEDER_MAILER"), password=os.getenv("SEEDER_MAILER_PWD"))

    print("Starting the Incidents Seeder...")

    # Try to generate incidents with the LLM
    try:
        incidents = seeder.generate_incidents()
        
        # Try to extract and process the JSON in a simplified way
        try:
            # Extract the JSON from the response
            json_text = incidents
            
            # If the text doesn't start with '[', try to find the beginning of the JSON
            if not json_text.strip().startswith('['):
                start = json_text.find('[')
                if start >= 0:
                    json_text = json_text[start:]
            
            # Clean the JSON to fix simple problems
            json_text = json_text.replace(";", ",").replace("'", '"')
            
            # Fix common problems with commas in descriptions
            json_text = re.sub(r'("description":\s*"[^"]*)"([^"]*")', r'\1\\\"\2', json_text)
            
            # Try to load the JSON
            incidents_list = json.loads(json_text)
            print(f"JSON processed successfully! Found {len(incidents_list)} incidents.")
        except Exception as e:
            print(f"Error processing JSON: {e}")
            
            # Try a simpler approach to extract the JSON
            try:
                # Look for a JSON array in the response
                start = incidents.find("[")
                end = incidents.rfind("]") + 1
                if start >= 0 and end > start:
                    json_text = incidents[start:end]
                    # Replace single quotes with double quotes
                    json_text = json_text.replace("'", '"')
                    # Replace semicolons with commas
                    json_text = json_text.replace(";", ",")
                    # Try to load the JSON
                    incidents_list = json.loads(json_text)
                    print(f"JSON extracted with alternative method! Found {len(incidents_list)} incidents.")
                else:
                    # If unable to extract the JSON, use default incidents
                    print("Could not find a JSON array in the response. Using default incidents...")
                    incidents_list = get_default_incidents()
            except Exception as e2:
                print(f"Alternative extraction failed: {e2}")
                print("Using default incidents...")
                incidents_list = get_default_incidents()
    except Exception as e:
        print(f"Error generating incidents with the LLM: {e}")
        print("Using default incidents...")
        incidents_list = get_default_incidents()
    # Check for duplicate titles and ensure we have exactly 10 unique incidents
    unique_titles = set()
    unique_incidents = []
    
    # First, filter incidents to keep only those with unique titles
    for incident in incidents_list:
        title = incident['title']
        if title not in unique_titles:
            unique_titles.add(title)
            unique_incidents.append(incident)
        else:
            print(f"Removing incident with duplicate title: {title}")
    
    # Now, check if we have 10 unique incidents
    if len(unique_incidents) != 10:
        print(f"WARNING: We have {len(unique_incidents)} incidents with unique titles instead of 10.")
        
        # If there are more than 10, cut to keep only 10
        if len(unique_incidents) > 10:
            print(f"Cutting to 10 incidents...")
            unique_incidents = unique_incidents[:10]
        
        # If there are less than 10, generate default incidents to complete
        else:
            missing = 10 - len(unique_incidents)
            print(f"Generating {missing} default incidents to complete the total of 10...")
            
            # Get default incidents to complete
            default_incidents = get_default_incidents()
            
            # Add only default incidents with titles that don't already exist
            added = 0
            for incident in default_incidents:
                if incident['title'] not in unique_titles and added < missing:
                    unique_incidents.append(incident)
                    unique_titles.add(incident['title'])
                    added += 1
            
            # If incidents are still missing, create new ones with modified titles
            if added < missing:
                remaining = missing - added
                print(f"We still need {remaining} unique incidents. Generating with modified titles...")
                
                for i in range(remaining):
                    # Create a unique title by adding a timestamp
                    import time
                    timestamp = int(time.time()) + i
                    
                    new_incident = {
                        "title": f"Technical issue #{timestamp % 1000} in the ANIMAL FREEDOM system",
                        "description": f"I am experiencing a technical issue when using the ANIMAL FREEDOM system. When I try to access the main functionality, I receive an error message that prevents normal use of the platform. I have tried refreshing the page, clearing the browser cache, and even using a different browser, but the problem persists. This error is affecting my productivity and I need an urgent solution to continue my work. Please help resolve this issue as soon as possible. Thank you in advance for your attention and support."
                    }
                    
                    unique_incidents.append(new_incident)
            
            print(f"Now we have exactly {len(unique_incidents)} incidents with unique titles to process.")
    
    # Update the incident list to use only those with unique titles
    incidents_list = unique_incidents
    
    print(f"Processing {len(incidents_list)} incidents...")
    
    for i, incident in enumerate(incidents_list):
        try:
            sender.send_email(
                to_address=os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL"),
                subject=incident['title'],
                body=incident['description']
            )
            print(f"Email {i + 1} sent successfully.")
        except Exception as e:
            print(f"Error sending email {i + 1}: {e}")

    print("Incidents Seeder completed.")

if __name__ == "__main__":
    main()
