# This is was a test file on how to create a batch request to open ai to reduce cost
from tavily import TavilyClient
import json

tavily_client = TavilyClient(api_key="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")
web_search = tavily_client.search(query="What happened in United States politics in recent days?",search_depth="advanced",topic="news",days=10,max_results=10,include_images=True,include_image_descriptions=True,include_raw_content=True)


print(web_search)
with open('out.txt', 'w') as output:
    output.write(json.dumps(web_search))


# output_file = "batchinput.jsonl"
# with open(output_file, "w") as file:
#     for i, result in enumerate(web_search["results"], start=1):
#         # Generate the first request
#         if(i==1):
#             request_1 = {
#                 "custom_id": f"request-{i}",
#                 "method": "POST",
#                 "url": "/v1/chat/completions",
#                 "body": {
#                     "model": "GPT-4o",
#                     "messages": [
#                         {"role": "system", "content": "You are a news reporter for news website called ProgressKingdom who shares unique view on various news topics with seo friendly content. And for the given content create a news report in the following valid json format {title: string;// Short catchy title of the news meant to hook the user\n slug: string;// slug of the article\n description: string;// Short description of the news article\n category: string;// Which category the news belongs too from the list ['business','politics','world','lifestyle','technology','science','sports','health']\n source: string; // Source url of the news\n content: string; // News Article content in 5, 6 paragraph\n seo_title: string;// Short catchy title of the news in 50-60 characters for seo meta tags\n seo_description: string;  //Short description in 150 - 160 characters for meta tags\n keywords: string[];// list of keywords for seo meta tags \n}."},
#                         {"role": "user", "content": result['raw_content']} 
#                     ],
#                 }
#             }
#             file.write(json.dumps(request_1) + "\n")

# from openai import OpenAI
# client = OpenAI()

# batch_input_file = client.files.create(
#     file=open("batchinput.jsonl", "rb"),
#     purpose="batch"
# )

# batch_input_file_id = batch_input_file.id
# client.batches.create(
#     input_file_id=batch_input_file_id,
#     endpoint="/v1/chat/completions",
#     completion_window="24h",
#     metadata={
#         "description": "nightly eval job"
#     }
# )