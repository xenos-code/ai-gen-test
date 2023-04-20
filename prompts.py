# prompts.py

prompts = {
    "system_message": (
        
        """
You are an AI language model. Your task is to follow the provided outline and ensure that the content is well-structured, SEO-friendly, and addresses the key points in each section.
Make sure to use clear, concise language and provide practical advice, examples, and tips where applicable.


""")
    
    ,
    "definition_prompt": "Please provide a short, clear and concise definition for the marketing term '{}'.",
    
    
    "article_prompt": (
        
        """
Please write an informative article about the marketing term '{}' following the given outline:\n\n{}\n
Please provide the output in semantic HTML format (there is no need for the H1).{}"""),
    
    "related_links_prompt": (
        
        """
        
In your HTML output, incorporate the following related links into the article text by using relevant anchor text when applicable. 
If a link is not directly relevant to the text, include it in the 'related terms' section. Here are the related links to incorporate:\n\n{}.

""")
}
