import requests
import re
from bs4 import BeautifulSoup
from py2neo import Graph, NodeMatcher, RelationshipMatcher
from py2neo.data import Node, Relationship

graph = Graph("http://localhost:32779/db/data/" ,password="a95150087")

base_url = "https://en.wikipedia.org"
start_urls = ["https://en.wikipedia.org/wiki/Property"]

depth = 0
def crawler(start_urls, depth, graph):
    print("depth:{}".format(depth))
    if depth <=2:
        child_refs = []
        for url in start_urls:
            h1 = findH1(url)
            exist = checkNode(graph, link=url)
            a = Node("page", name=h1, link=url)

            if exist == False:
                graph.create(a)
                node_a = NodeMatcher(graph).match(link=url).first()
            else:
                node_a = NodeMatcher(graph).match(link=url).first()

            result = requests.get(url)
            if result.status_code == 200:
                c = result.content
            else:
                print(start_result.status_code)
            soup = BeautifulSoup(c, "html.parser")

            refs = soup.find_all("a")
            refs = [tag.get("href") for tag in refs]
            refs = [base_url + tag for tag in refs if bool(re.match("^/wiki",str(tag))) == True]
            refs = [tag for tag in refs if bool(re.search("Category",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Wikipedia:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Special:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Help:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Portal:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("File:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Main_Page",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Talk:",str(tag))) == False]
            refs = [tag for tag in refs if bool(re.search("Template:",str(tag))) == False]
            #print(refs)
            refs = refs
            child_refs.extend(refs)
            for g_link in refs:
                child_h1 = findH1(g_link)
                b = Node("page", name=child_h1, link=g_link)
                if checkNode(graph, link=g_link) == False:
                    graph.create(b)
                    node_b = NodeMatcher(graph).match(link=g_link).first()
                else:
                    node_b = NodeMatcher(graph).match(link=g_link).first()

                if checkRelation(graph, [node_a,node_b], "links_to") == False:
                    ab = Relationship(node_a, "links_to", node_b)
                    graph.create(ab)

        print("length of urls: {}".format(len(child_refs)))
        depth += 1

        return crawler(child_refs,depth,graph)
    else:
        return

def findH1(url):
    result = requests.get(url)

    if result.status_code == 200:
        c = result.content
    else:
        print(start_result.status_code)

    soup = BeautifulSoup(c, "html.parser")
    h1 = soup.find_all("h1", "firstHeading")

    if len(h1) != 1:
        print("h1 is not unique or empty")
    else:
        h1 = h1[0].string

    return h1

def checkNode(graph, link):
    matcher = NodeMatcher(graph)
    m = matcher.match(link=link).first()
    if m is None:
        return False
    else:
        return True

def checkRelation(graph, nodes, r_type):
    matcher = RelationshipMatcher(graph)
    m = matcher.match(nodes = nodes, r_type = r_type).first()
    if m is None:
        return False
    else:
        return True


crawler(start_urls, depth, graph)
