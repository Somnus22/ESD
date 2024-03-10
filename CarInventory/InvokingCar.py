from invokes import invoke_http

results = invoke_http("http://localhosg:5000/cars", method= "GET")

print(results)