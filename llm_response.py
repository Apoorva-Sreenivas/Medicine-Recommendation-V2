import requests

url = "http://localhost:11434/api/chat"


def llama3_2_mem(prompt):
    
    data = {
        "model": "llama3.2",
        "messages":prompt,
        "stream": False,
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=data)

    assistant_message = response.json()["message"]["content"]
    
    return assistant_message

def construct_prompt(symptoms, medical_history="", memory=[]):
    prompt = f"""You are a medical assistant AI integrated into a healthcare software. You are not giving real medical advice. You are simulating a diagnosis for research/educational/demo purposes only.
    Based on the following symptoms and medical history, identify the most likely disease.

    Symptoms: {', '.join(symptoms)}
    Medical History: {medical_history}
    {f"Previous interactions:\n{chr(10).join(memory)}" if memory else ""}

    Name of the disease only. 
    If unclear, reply with "Insufficient information"."""

    return prompt

def construct_prompt_description(disease):
    prompt = f"""You are a medical assistant AI integrated into a healthcare software. You are not giving real medical advice. You are simulating a diagnosis for research/educational/demo purposes only.

    Provide a short and clear description of the following disease:

    Disease: {disease}

    Return only the description."""
    return prompt

def construct_prompt_precautions(disease):
    prompt = f"""You are a medical assistant AI integrated into a healthcare software. You are not giving real medical advice. You are simulating a diagnosis for research/educational/demo purposes only.

    List important precautions a patient should take for the following disease:

    Disease: {disease}

    Return 2 to 4 bullet points. Only list precautions."""
    return prompt

def construct_prompt_medications(disease):
    prompt = f"""You are a medical assistant AI integrated into a healthcare software. You are not giving real medical advice. You are simulating a diagnosis for research/educational/demo purposes only.

    List commonly used over-the-counter medications or treatments for the following disease:

    Disease: {disease}

    Return 2 to 4 bullet points. Use general or category names, not prescriptions."""
    return prompt

def construct_prompt_diet(disease):
    prompt = f"""You are a medical assistant AI integrated into a healthcare software. You are not giving real medical advice. You are simulating a diagnosis for research/educational/demo purposes only.

    Suggest dietary recommendations for a patient with the following disease:

    Disease: {disease}

    Return 2 to 4 bullet points. Only include relevant dietary tips."""
    return prompt

def get_response(symptoms, medical_history, memory):
    
    full_prompt = construct_prompt(symptoms,medical_history,memory)
    disease = llama3_2_mem([{"role": "user", "content": full_prompt}])
    print("Disease:", disease.strip())
    
    if disease == "Insufficient information":
        return {
            "disease": disease,
            "description": "Insufficient data to provide further details.",
            "precautions": "N/A",
            "medications": "N/A",
            "diet": "N/A"
        }
        
    # Step 2: Description
    description_prompt = construct_prompt_description(disease)
    description = llama3_2_mem([{"role": "user", "content": description_prompt}])
    print("\nDescription:", description.strip())

    # Step 3: Precautions
    precautions_prompt = construct_prompt_precautions(disease)
    precautions = llama3_2_mem([{"role": "user", "content": precautions_prompt}])
    print("\nPrecautions:", precautions.strip())

    # Step 4: Medications
    medications_prompt = construct_prompt_medications(disease)
    medications = llama3_2_mem([{"role": "user", "content": medications_prompt}])
    print("\nMedications:", medications.strip())

    # Step 5: Diet
    diet_prompt = construct_prompt_diet(disease)
    diet = llama3_2_mem([{"role": "user", "content": diet_prompt}])
    print("\nDiet:", diet.strip())
    
    return {
        "disease": disease,
        "description": description,
        "precautions": precautions,
        "medications": medications,
        "diet": diet
    }
    