from elasticsearch import Elasticsearch
import warnings

warnings.filterwarnings("ignore")

host = '95.217.191.79'
# host = '13.233.103.143'
#host = '10.47.98.164'
port = 9200
url = f'https://{host}:{port}'
username = 'elastic'
password = 'revelastic'
#password = 'abg@elastic'


es = Elasticsearch([url],
                   http_auth=(username, password),
                   verify_certs=False, timeout=100
                   )



print(es.ping())