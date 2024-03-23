from invokes import invoke_http

results = invoke_http("http://localhost:5000/cars", method= "GET")

print(results)