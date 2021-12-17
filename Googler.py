from bs4 import BeautifulSoup
import requests
import urllib.parse


def google(search_string: str, num_results: int = 1) -> list[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
    search_string = urllib.parse.quote(search_string)
    search_url = f"https://www.google.com/search?q={search_string}+-corona"
    print(search_url)
    req = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")
    t = soup.find_all("h3")

    result = []
    c = 0
    while len(result) < num_results:
        tag = t[c]
        # print(tag.find("a"))
        # print(tag.get_text())
        if "adurl" in tag or tag.get_text() == "Annoncer":
            c += 1
            continue
        # print(tag)
        # print(tag.parent.get("href"))
        link = tag.parent.get("href")
        header = tag.get_text()
        result.append(header + " : " + "<"+link+">" if link else "error")
        c += 1

    # for tag in t[:num_results]:
    #     print(tag)
    #     link = tag.parent.get("href")
    #     header = tag.get_text()
    #     result.append(header + " : " + "error" if link else link)
    return result


if __name__ == "__main__":
    print(google("raspberry pi", 3))
