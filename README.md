# 3D Rotations

This project implements different methods for performing 3D rotations, including Euler angles, quaternions, transformation matrices, and Rodrigues' rotation formula. The aim is to explore and compare their performance in terms of execution time, memory usage, and computational efficiency.

## Prerequisites

Before running the program, you need to set up a virtual environment and install the required dependencies.

### 1. Setting Up a Virtual Environment

To ensure that the project dependencies are isolated from your system environment, you can set up a Python virtual environment. Follow these steps:

1. **Install Python 3**  
   Make sure you have Python 3.6 or higher installed. You can check your Python version by running:

   ```bash
   python --version
   ```

2. **Create a Virtual Environment**
   In the root directory of the project, create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On **Windows**, run:
     ```bash
     .\venv\Scripts\activate
     ```
   - On **macOS/Linux**, run:
     ```bash
     source venv/bin/activate
     ```

### 2. Install Dependencies

Once the virtual environment is activated, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

### 3. Running the Program

After setting up the virtual environment and installing the dependencies, you can run the Python program.

To run the main script:

```bash
python main.py
```

This will execute the program and perform 3D rotations based on the specified rotation methods (Euler, quaternion, etc.).

## Notes

- If you encounter any errors related to missing dependencies or modules, make sure the virtual environment is properly activated and that all dependencies are installed.
- The code can be modified to include other rotation methods or to compare performance across different scenarios.
