import httpx
import bs4
import json
import os


# ----------------------------------------
# FUNCTIONS
# ----------------------------------------

def scan(url):
    matching_ingredients = []
    
    categories = os.listdir("ingredients")
    ingredients_count = 0
            
    try:
        r = httpx.get(url)
    except httpx.ConnectError:
        raise Exception("Invalid URL")
    
    if r.status_code != 200:
        raise Exception(f"Error: Invalid Request Status Code ({r.status_code})")
    
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    
    headers = r.headers
    
    
    # ----------------------------------------
    # INGREDIENTS SCANNER
    # ----------------------------------------
    
    for category in categories:
        ingredients = os.listdir(f"ingredients/{category}")
        ingredients_count += len(ingredients)
        
        for ingredient in ingredients:
            with open(f"ingredients/{category}/{ingredient}", "r") as f:
                ingredient_data = json.loads(f.read())
            
            for tag_check in ingredient_data["checks"]["tags"]:
                tags = soup.find_all(tag_check["tag"])
                for tag in tags:
                    # check for tag attribute (value is None)
                    if tag_check["value"] is None and tag.get(tag_check["attribute"]) != None:
                        if f"{category}/{ingredient}" not in matching_ingredients:
                            matching_ingredients.append(f"{category}/{ingredient}")
                            
                    # check for tag content (attribute is not None) with wildcards      
                    elif tag.get(tag_check["attribute"]) != None and "*" in tag_check["value"]:
                        checks = tag_check["value"].split("*")
                        successful_checks = 0
                        for check in checks:
                            if check in tag.get(tag_check["attribute"]):
                                successful_checks += 1
                            
                        if successful_checks == len(checks):
                            if f"{category}/{ingredient}" not in matching_ingredients:
                                matching_ingredients.append(f"{category}/{ingredient}")
                                    
                    # check for tag content (attribute is not None)
                    elif tag.get(tag_check["attribute"]) != None and tag_check["value"] in tag.get(tag_check["attribute"]):
                        if f"{category}/{ingredient}" not in matching_ingredients:
                            matching_ingredients.append(f"{category}/{ingredient}")
                            
                    # check for tag content (attribute is None)
                    elif tag_check["attribute"] is None and tag_check["value"] in tag.text:
                        if f"{category}/{ingredient}" not in matching_ingredients:
                            matching_ingredients.append(f"{category}/{ingredient}")
                    
                    # check for <meta name="generator" content="generator name"> tag
                    # to enable this check, set the tag to "meta", the attribute to "generator"
                    elif tag_check["tag"] == "meta" and tag.get("name") == "generator":
                        if tag_check["value"] in tag.get("content"):
                            if f"{category}/{ingredient}" not in matching_ingredients:
                                matching_ingredients.append(f"{category}/{ingredient}")
                            
            # TODO: Check header capitalization
                            
            for header_check in ingredient_data["checks"]["headers"]:
                # check request header
                if header_check["header"] in headers:
                    if header_check["value"] is None:
                        if f"{category}/{ingredient}" not in matching_ingredients:
                            matching_ingredients.append(f"{category}/{ingredient}")
                    elif header_check["value"] in headers[header_check["header"]]:
                        if f"{category}/{ingredient}" not in matching_ingredients:
                            matching_ingredients.append(f"{category}/{ingredient}")
    
    # ----------------------------------------
    
    matching_ingredients_data = []
    
    for ingredient in matching_ingredients:
        with open(f"ingredients/{ingredient}", "r") as f:
            ingredient_category = ingredient.split("/")[0]
            ingredient_data = json.loads(f.read())
            
            matching_ingredients_data.append({
                "name": ingredient_data["name"],
                "category": ingredient_category,
                "icon": ingredient_data["icon"]
            })
    
    return {
        "url": url,
        "total_categories": len(categories),
        "total_ingredients": ingredients_count,
        "matching_ingredients": len(matching_ingredients),
        "matches": matching_ingredients_data
    }