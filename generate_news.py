import requests
from tavily import TavilyClient
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

BLUE = "\033[34m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

load_dotenv()  # Load variables from .env file

tavily_api_key = os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")


# Function to Scrap the web for results
def scrapWeb(query,quantity):
    tavily_client = TavilyClient(api_key=tavily_api_key)
    try:
        web_search = tavily_client.search(query=query,search_depth="advanced",topic="news",days=10,max_results=quantity,include_images=True,include_image_descriptions=True,include_raw_content=True)
        print(f"{GREEN}Web scrape successful and result written to webscrap.json{RESET}")  
        with open('webscrap.json', 'w') as output:
            output.write(json.dumps(web_search))
        return web_search
    except:
        print("{RED}Tavily error occured{RESET}")

# Function to write the article with chatgpt
def getNewsArticle(result,image,siteName=""):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": f"You are a news reporter for news website called {siteName} , who shares unique view on various news topics with seo friendly content. And for the given content create a news report in valid json format"},
            {"role": "user", "content": result['raw_content']} 
        ],
        response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "article_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "description": "Short catchy title of the news meant to hook the user",
                        "type": "string"
                    },
                    "slug": {
                        "description": "Slug of the article",
                        "type": "string"
                    },
                    "description": {
                        "description": "Short description of the news article",
                        "type": "string"
                    },
                    "category": {
                        "description": "Category of the news from the predefined list",
                        "type": "string",
                        "enum": [
                            "BUSINESS",
                            "POLITICS",
                            "WORLD",
                            "LIFESTYLE",
                            "TECHNOLOGY",
                            "SCIENCE",
                            "SPORTS",
                            "HEALTH"
                        ]
                    },
                    "source": {
                        "description": "Source URL of the news",
                        "type": "string",
                        "format": "uri"
                    },
                    "content": {
                        "description": "Full content of the news article in 5-6 paragraphs with various views",
                        "type": "string"
                    },
                    "seo_title": {
                        "description": "Short catchy title of the news for SEO tags (50-60 characters)",
                        "type": "string"
                    },
                    "seo_description": {
                        "description": "Short description for meta tags (150-160 characters)",
                        "type": "string"
                    },
                    "keywords": {
                        "description": "List of keywords for SEO",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "publish_date":{
                        "description": "Publish date of the news article in ISO 8601 format,",
                        "type": "string"
                    }
                },
                "required": [
                    "title",
                    "slug",
                    "description",
                    "category",
                    "source",
                    "content",
                    "seo_title",
                    "seo_description",
                    "keywords",
                    "publish_date"
                ],
                "additionalProperties": False
            }
        }
    }

    )
    article = json.loads(response.choices[0].message.content)
    # article = {"title":"Trump's Second Term Begins with Controversial Moves","slug":"trumps-second-term-controversial-moves","description":"President Trump pulls security clearances and signs numerous executive orders as he returns for a second term.","category":"politics","source":"https://www.foxnews.com","content":"As President Donald Trump steps into his second term as the 47th president of the United States, he is already making headlines with a series of controversial actions. Notably, Trump has revoked the security clearances of over 50 national security officials who, in a 2020 letter, described Hunter Biden's laptop allegations as having 'all the classic earmarks of a Russian information operation.' This decision has sparked discussions on how Trump plans to manage national security concerns moving forward.\n\nAdditionally, Trump's inaugural address set the stage for his policy direction, one that analysts are already calling a 'playbook' for his term. Among the most striking of Trump's first-day actions were the signing of a record number of executive orders. These orders cover a vast range of topics, signaling a swift move towards fulfilling his administration's goals.\n\nAmong Trump's headline-grabbing activities is his decision not to grant clemency to Ross Ulbricht, founder of Silk Road, despite previous indications that this would be a 'Day 1' priority. Meanwhile, a federal judge has restrained the release of the second volume of a special counsel report, indicating legal challenges that lie ahead.\n\nIn the international arena, Trump made bold statements about retaking the Panama Canal, which have elicited strong reactions from global leaders. This stance comes as Trump seeks to navigate complex geopolitical landscapes, with the world closely watching his 'America First' strategies.\n\nOn domestic policy, Trump's administration faces immediate pushback on birthright citizenship, with critics describing a recent presidential order as 'unconstitutional.' Despite the backlash, Trump's allies in the House are doubling down, introducing legislation to support his immigration agenda.","seo_title":"Trump's Bold Moves in Second Term","seo_description":"Trump revokes security clearances, signs record executive orders on first day of second term. Global and domestic challenges unfold.","keywords":["Trump second term","executive orders","security clearances","immigration policy","Panama Canal","America First"]}
    altTxt = "Image default alt text"
    if(image.get("description")!=None):
        altTxt = image.get("description")
    article.update({
        "image_url": image.get("url", "/image_not_found.png"),  # Use default string if `url` is None
        "image_alt": altTxt,  # Use default string if `description` is None
    })
    print(f"{GREEN}Article generated with title:{article.get("title")} {RESET}")
    return article

# Funtion to call api to add to database
def putToDatabase(data):
    url = 'http://localhost:3000/api/article'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token-here'
    }
    payload = {"data": data}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed with status code:", response.status_code)
        print("Response text:", response.text)


def getInputPromt():
    while True:
        user_input = input(f"{BLUE}Enter your promt: {RESET}")
        promt = str(user_input)
        if promt != None and promt != "":
            print(f"Your promt is {GREEN}{promt}.{RESET}")
            return promt
        else:
            print(f"{RED}Please enter a valid prompt{promt}{RESET}")

def getInputquantity():
    while True:
        user_input = input(f"{BLUE}How many news do you need: {RESET}")
        if user_input.isdigit() and 0 < int(user_input) < 120:
            quantity = int(user_input)
            print(f"Quantity {GREEN}{quantity}.{RESET}")
            return quantity
        else:
            print(f"{RED}Invalid quantity. Please enter a number between 1 and 120.{RESET}")


def generateNews():
    promt = getInputPromt()
    # qty = getInputquantity()    
    # do a web scrap
    print(f"{BLUE}Scrpaing the web for news{RESET}")
    web_search = scrapWeb(query=promt,quantity=5) 
    if web_search != None:
        output_file = "articlelist.jsonl"
        # # for each result create an article object and write to the outpur file
        with open(output_file, "w") as file:
            for i, result in enumerate(web_search["results"], start=0):
                article = getNewsArticle(result=result,image=web_search["images"][i],siteName="ProgressKingdom")
                file.write(json.dumps(article)+"\n" )


        
# upload the articles from jsonl to the database        
def uploadNews():
    with open("articlelist.jsonl", "r") as file:
        for line in file:
            try:
                # Parse the JSON object from the line
                data = json.loads(line.strip())
                
                # Make the POST request
                putToDatabase(data=data)
                
            except json.JSONDecodeError:
                print("Error decoding JSON line:", line)
            except requests.RequestException as e:
                print("Error with POST request:", e)

# Asks for prompt and quantity
generateNews()
# Uploads to the database 
uploadNews()