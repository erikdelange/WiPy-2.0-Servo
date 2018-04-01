# Extract all name=value pairs from a GET url and place them into a dictionary
#
# Example GET url: b"GET /?name1=0.07&name2=0.03&name3=0.13 HTTP/1.1\r\n"
#
def extract(request):
    d = dict()
    p = request.find(b"?")
    if p != -1:
        while True:
            n_start = p + 1
            n_end = request.find(b"=", n_start)
            v_start = n_end + 1
            p_space = request.find(b" ", v_start)
            p_and = request.find(b"&", v_start)
            v_end = p_space if p_and == -1 else min(p_space, p_and)
            d[request[n_start:n_end].decode("utf-8")] = request[v_start:v_end].decode("utf-8")
            p = v_end
            p = request.find(b"&", p)
            if p == -1:
                break
    return d


# Extract the value for a single name=value pair from a GET url
#
# Return value is None if name cannot be found in the request
#
def find(request, name):
    value = None
    n_start = request.find(name.encode("utf-8"))
    if n_start != -1:
        v_start = request.find(b"=", n_start) + 1
        v_end = request.find(b" ", v_start)
        value = request[v_start:v_end].decode("utf-8")
    return value
