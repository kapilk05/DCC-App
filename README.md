# DCC-App Python Assignment


## Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/kapilk05/DCC-App.git
   cd DCC-App
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

---

## Running the Application

1. Start the Flask server:
   ```sh
   python server.py
   ```
   ![Flask Server](images/flask server.png)
2. The object transformations are defined under assignment.blend
   data object is containing object data that we store the transformation on 
   these changes are reflected in the flask terminal when run <br>
   <img src="images/transformations from blender.png" alt="Flask Server Showing Transformations" width="600"> <br> <br> 
   and the same can be seen on the running server at http://127.0.0.1:5000/get-transformations <br> <br> <br> 
   <img src="images/flask server showing transformations.png" alt="Flask Server Showing Transformations" width="600">



### Inventory  (`page.py`)
- Add an item to inventory <br>
- Remove an item <br>
  <img src="images/return button.png" alt="Flask Server Showing Transformations" width="600"> <br>


- List all items <br>

![Inventory](images/inventory.png)

### Flask API (`server.py`)
- `POST /add-item`: Add a new item with name and quantity
- `POST /remove-item`: Remove an item by name
- `GET /inventory`: Retrieve the entire inventory
  
---
Alternately you can use `pyinstaller` to package the application to run without a python enviornment

```sh
pip install pyinstaller
pyinstaller --onefile server.py
pyinstaller --onefile page.py
```

This will generate executable files in the `dist/` folder.

---

you can run python server.exe or python page.exe


This project video is at : 

