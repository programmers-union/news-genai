from pathlib import Path
import requests
from tavily import TavilyClient
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
from PIL import Image
from urllib.parse import urlparse, unquote

BLUE = "\033[34m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

load_dotenv()  # Load variables from .env file

tavily_api_key = os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
# TODO: Use this for in case of public hosted upload api
# upload_api_key = os.getenv("UPLOAD_API_KEY")

def download_image(image_url,slug ):
    save_dir="uploads/"
    try:
        # Ensure the directory exists
        base_dir = Path.cwd()  # Get script directory
        new_path = os.path.join(base_dir, save_dir)
        os.makedirs(save_dir, exist_ok=True)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        # Send a GET request to the image URL
        response = requests.get(image_url,headers=headers, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        filename = slug

        # If the filename doesn't have an extension, try to determine it from the Content-Type header
        if not os.path.splitext(filename)[1]:
            content_type = response.headers.get('Content-Type')
            if content_type:
                extension = content_type.split('/')[-1]
                if extension in ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff','webp']:
                    filename += f'.{extension}'

        # Full path to save the image
        save_path = os.path.join(new_path, filename)

        # Save the image
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"✅ Image downloaded successfully: {save_path}")
        crop_image_to_16_9(save_path)
        return os.path.join(save_dir, filename)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading image: {e}")
        return None

# def download_image(image_url, save_path="downloaded_image.jpg"):
#     try:
#         # Ensure the directory exists
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)

#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
#         }
#         response = requests.get(image_url,headers=headers, stream=True)
#         response.raise_for_status()  # Raise an error for bad status codes
        
#         with open(save_path, "wb") as file:
#             for chunk in response.iter_content(1024):
#                 file.write(chunk)
        
#         print(f"✅ Image downloaded successfully: {save_path}")
#         crop_image_to_16_9(save_path)
#         return save_path
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Error downloading image: {e}")
#         return None

def crop_image_to_16_9(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            target_width = width
            target_height = int(width * 9 / 16)
            
            if target_height > height:
                target_height = height
                target_width = int(height * 16 / 9)
            
            left = (width - target_width) / 2
            top = (height - target_height) / 2
            right = (width + target_width) / 2
            bottom = (height + target_height) / 2
            
            img_cropped = img.crop((left, top, right, bottom))
            img_cropped.save(image_path)
            print(f"✅ Image cropped to 16:9 ratio: {image_path}")
    except Exception as e:
        print(f"❌ Error cropping image: {e}")


# Function to Scrap the web for results
def scrapWeb(query):
    tavily_client = TavilyClient(api_key=tavily_api_key)
    try:
        web_search = tavily_client.search(query=query,search_depth="advanced",topic="news",days=10,max_results=5,include_images=True,include_image_descriptions=True,include_raw_content=True)
        print("\r✅ Web scrape successful!          \n")  
        with open('webscrap.json', 'w') as output:
            output.write(json.dumps(web_search))
        print(f"{GREEN}Web scrape successful and result written to webscrap.json{RESET}   \n")  
        return web_search
    except :
        print(f"{RED}Tavily error occured{RESET}   \n")

# Function to write a single article with chatgpt
def getNewsArticle(result,image,scheema,siteName=""):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": f"You are a news reporter for news website called {siteName} , who shares unique view on various financial news topics with seo friendly content(content is targeted to US, UK, and UAE, consider that for seo) And for the given content create a news report in valid json format"},
            {"role": "user", "content": result['raw_content']} 
        ],
        response_format = scheema

    )
    article = json.loads(response.choices[0].message.content)
    # article = {"title":"Trump's Second Term Begins with Controversial Moves","slug":"trumps-second-term-controversial-moves","description":"President Trump pulls security clearances and signs numerous executive orders as he returns for a second term.","category":"politics","source":"https://www.foxnews.com","content":"As President Donald Trump steps into his second term as the 47th president of the United States, he is already making headlines with a series of controversial actions. Notably, Trump has revoked the security clearances of over 50 national security officials who, in a 2020 letter, described Hunter Biden's laptop allegations as having 'all the classic earmarks of a Russian information operation.' This decision has sparked discussions on how Trump plans to manage national security concerns moving forward.\n\nAdditionally, Trump's inaugural address set the stage for his policy direction, one that analysts are already calling a 'playbook' for his term. Among the most striking of Trump's first-day actions were the signing of a record number of executive orders. These orders cover a vast range of topics, signaling a swift move towards fulfilling his administration's goals.\n\nAmong Trump's headline-grabbing activities is his decision not to grant clemency to Ross Ulbricht, founder of Silk Road, despite previous indications that this would be a 'Day 1' priority. Meanwhile, a federal judge has restrained the release of the second volume of a special counsel report, indicating legal challenges that lie ahead.\n\nIn the international arena, Trump made bold statements about retaking the Panama Canal, which have elicited strong reactions from global leaders. This stance comes as Trump seeks to navigate complex geopolitical landscapes, with the world closely watching his 'America First' strategies.\n\nOn domestic policy, Trump's administration faces immediate pushback on birthright citizenship, with critics describing a recent presidential order as 'unconstitutional.' Despite the backlash, Trump's allies in the House are doubling down, introducing legislation to support his immigration agenda.","seo_title":"Trump's Bold Moves in Second Term","seo_description":"Trump revokes security clearances, signs record executive orders on first day of second term. Global and domestic challenges unfold.","keywords":["Trump second term","executive orders","security clearances","immigration policy","Panama Canal","America First"]}
    altTxt = "Image default alt text"
    if(image.get("description")!=None):
        altTxt = image.get("description")
    file_name = download_image(image_url=image.get("url"),slug=article.get("slug"))
    article.update({
        "image_url": file_name,  # Use default string if `url` is None
        "image_alt": altTxt,  # Use default string if `description` is None
        "domain":"thecapitalistjournal.com"
    })
    print(f"\r✅ {GREEN} Article generated with title:{article.get("title")} {RESET}     \n")
    return article

# Function of input prompt
def getInputPromt():
    while True:
        user_input = input(f"{BLUE}Enter your promt: {RESET}")
        promt = str(user_input)
        if promt != None and promt != "":
            print(f"Your promt is {GREEN}{promt}.{RESET}   \n")
            return promt
        else:
            print(f"{RED}Please enter a valid prompt{promt}{RESET}   \n")

# Function looped to write articles at once 
def generateNews():
    promt = getInputPromt()
    scheema={
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
                            "the_world",
                            "business_and_finance",
                            "personal_finance",
                            "economics",
                            "markets",
                            "science_and_technology",
                            "cryptocurrencies",
                        ]
                    },
                    "source": {
                        "description": "Source URL of the news",
                        "type": "string",
                        "format": "uri"
                    },
                    "content": {
                        "description": "Full content of the news article in 5-6 paragraphs with detailed view on the topic. each paragraph should be wraped inside p tag and if there are headings used wrap it with h2 tag",
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
    print(f"{BLUE}Scrpaing the web for news{RESET} ")
    web_search = scrapWeb(query=promt) 
    if web_search != None:
        output_file = "articlelist.jsonl"
        # # for each result create an article object and write to the outpur file
        with open(output_file, "a") as file:
            for i, result in enumerate(web_search["results"]):
                article = getNewsArticle(result=result,image=web_search["images"][i],scheema=scheema,siteName="ProgressKingdom")
                file.write(json.dumps(article) + "\n" )
    
# upload the articles from jsonl to the database        
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

# Generating news and produces articlelist.json
continueGeneration = True
while continueGeneration:
    generateNews()
    user_input = input("Do you want to continue? (y/n): ").strip().lower()
    if user_input != 'y':
        continueGeneration = False
    else :
        continueGeneration = True


# # Uploads to the database 
# uploadNews(apiUrl='http://localhost:3000/api/article')