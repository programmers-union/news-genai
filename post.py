import json
import requests
       
def uploadNews(apiUrl):
    with open("articlelist.jsonl", "r") as file:
        for line in file:
            try:
                # Parse the JSON object from the line
                data = json.loads(line.strip())
                
                # Make the POST request
                headers = {
                    'Content-Type': 'application/json',
                    # 'Authorization': 'Bearer your-token-here'
                }
                payload = {"data": data}
                response = requests.post(apiUrl, json=payload, headers=headers)
                if response.status_code == 200:
                    print("Successfuly add article to the backend:", response.json())
                else:
                    print("Failed with status code:", response.status_code)
                    print("Response text:", response.text)
                
            except json.JSONDecodeError:
                print("Error decoding JSON line:", line)
            except requests.RequestException as e:
                print("Error with POST request:", e)



# # Uploads to the database 
uploadNews(apiUrl='http://localhost:3000/api/article')

