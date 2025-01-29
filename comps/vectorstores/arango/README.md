# Start ArangoDB server

**Additional Links**:
- https://arangodb.com/2024/11/vector-search-in-arangodb-practical-insights-and-hands-on-examples/

## 1. Start ArangoDB via Docker

```bash
docker run -d --name arangodb -p 8529:8529 -e ARANGO_ROOT_PASSWORD=openSesame arangodb/arangodb:3.12 --experimental-vector-index true
```

## 2. Create a Vector Index

**Using `arangosh`**:

```bash
127.0.0.1:8529@_system > db.myCollection.ensureIndex(
    {
            name: "my-vector-index",
            type: "vector",
            fields: ["embedding"]
            params: { metric: "cosine", dimension: 1024, nLists: 100 }
    }
)
```

**Using the `python-arango` driver**:

```python
from arango import ArangoClient

db = ArangoClient(hosts="http://localhost:8529").db('_system', username='root', password='openSesame')

db.collection("myCollection").add_index(
    {
        "name": "my-vector-index",
        "type": "vector",
        "fields": ["embeddings"],
        "params": {
            "metric": "cosine",
            "dimension": 1024,
            "nLists": 100,
        },
    }
)
```

## 3. Use the Vector Index via the Arango Query Language (AQL)

```bash
LET query_embedding = [0.1, 0.3, 0.5, …]

FOR doc IN myCollection
    LET score = APPROX_NEAR_COSINE(doc.embedding, query_embedding)
    SORT score DESC
    LIMIT 5
    RETURN {doc, score}   
```