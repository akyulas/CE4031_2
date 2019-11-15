# CE4031

## Installing Dependencies

### Manual Installation
1. [Python 3.6.6 - Python 3.7.5](https://www.python.org/downloads/) - [PSF Licence](https://docs.python.org/3/license.html)

### Required Python Libraries
1. [MatPlotLib](https://matplotlib.org/) - [PSF Licence](https://docs.python.org/3/license.html)
2. [NumPy](https://numpy.org/) - [NumPy License](https://numpy.org/license.html)
3. [NetworkX](https://networkx.github.io/) - [NetworkX License](https://raw.githubusercontent.com/networkx/networkx/master/LICENSE.txt)
4. [Psycopg2](http://initd.org/psycopg/) - [Psycopg2 License](http://initd.org/psycopg/license/)
5. [Pytest](https://docs.pytest.org/en/latest/) - [Pytest License](https://docs.pytest.org/en/latest/license.html)
6. [SciPy](https://www.scipy.org/index.html) - [SciPy License](https://www.scipy.org/scipylib/license.html)

### Installation Steps
1. Once Python has been installed, input in _cmd_ : `python -m pip install -r requirements.txt`

## Launch GUI
1. Navigate to the src directory
2. Run the following Python command: `python main.py`
3. The GUI is best viewed in full screen mode
4. On the Homepage connect to the database by filling in the required relevant information.
5. For e.g. Database URL: 'localhost', Database Name: 'TPC-H', Database Port: '5433' (5432 by default), User: 'postgres', Password: 'password' and click 'Submit'
6. In the Query Page, fill in the two queries text box with SQL queries. The output will display how the query tree has evolved from query 1 to query 2.
7. In the Query Plan Tree Page, the tree graph of the two query plans can be seen and compared.

## Run test cases
1. Navigate to the test directory
2. Update your database information in the global variables: host, DB_NAME, user, password, port in the “test_difference_in_natural_language.py”
3. Run the following Python command: `python -m pytest test_difference_in_natural_language.py`
