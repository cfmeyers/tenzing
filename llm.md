# tenzing Overfiew
I'm writing a Python CLI called `tenzing` that will interact with the Basecamp (project management software) API via the basecampy3 Python library.

`tenzing` will use the following libraries:
- click to build the command line interface
- basecampy and requests to interact with the Basecamp API
- sqlite to persist the information we download from Basecamp
- Pydantic to model the objects we get from Basecamp

`@Basecamp 3 API` are the docs for the actual Basecamp 3 API.
`@Basecampy3` are the docs for the Python package we're using.
I'm passing in the authentication information as env variables for basecampy3.
Provided you initialize the module with `Basecamp3.from_environment()` it will read them in automatically (see the basecampy3 docs).

In general, I like to code with the "Functional core, imperative shell" concept introduce by Gary Bernhardt.
This means:
- keep the core logic out of cli.py as much as possible...that module is just an interface between the user and the core logic.
- make a seperate models.py module to hold the Pydantic models.


# Test Guidance
I'm also using pytest to write and run my tests.
My guidance for writing tests:
- You will group all the tests for the given function/class within a class.
- each python module should have a corresponding test module with the same name, but with `test_` prepended to it.
- Each test method will test a single thing about the function/class.
- The test methods will be named like `test_it_does_X`, or if it's a class with method e.g. `run_calc`, then `test_run_calc_returns_X` or `test_run_calc_raises_Y_when_`.
- You will avoid using fixtures unless I ask for them; instead you'll use literal strings or lists or dicts etc.
- You will keep your test inputs as simple and small as possible.
- You will use the arrange-act-assert test style.
- The variable you'll use to capture the evaluation of the code under test will be called `actual` and the variable you'll use to compare to `actual` will be called `expected`.
- When you do the final comparison it should be `assert expected == actual`.

Remember to keep the tests as simple as possible...they will be used to illustrate how to use the class/function under test.
