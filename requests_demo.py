import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")


jobs = []
for job in soup.find_all("div", class_="card-content"):
    job_title = job.find("h2", class_="title").text.strip()
    creator = job.find("h3", class_="company").text.strip()
    address = job.find("p", class_="location").text.strip()
    created_date = job.find("time")["datetime"]
    jobs.append((job_title, creator, address, created_date))

    print(job_title)
    print(creator)
    print(address)
    print(created_date)
    print()
