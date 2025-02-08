import requests

def test_add_item():
    response = requests.post("http://127.0.0.1:5000/add-item", json={"name": "Pen", "quantity": 10})
    assert response.status_code == 201  
