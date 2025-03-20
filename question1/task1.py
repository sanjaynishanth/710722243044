from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()
# api p-prime,f-fibonacci,e-even,r-random number
server_url = {
    "p": "http://20.244.56.144/test/primes",
    "f": "http://20.244.56.144/test/fibo",
    "e": "http://20.244.56.144/test/even",
    "r": "http://20.244.56.144/test/rand"
}
#initial window size
window_size = 10
window = []

@app.get("/calculate")
def calculate_avg(source: str):
    if source not in server_url:
        raise HTTPException(status_code=400, detail="Invalid")

    try:
        response = requests.get(server_url[source], timeout=0.5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=502, detail="Error fetching data")
    #if input data is in list take as list
    try:
        data = response.json()
        if isinstance(data,list):
            num=list(set(data))
        else:
            num=list(set(data.get("numbers",[])))
        
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid data received")

    # Filter valid numbers

    fnum=[]
    for n in num:
        if isinstance(n,(int,float)) and n>=0:
            fnum.append(n)

    num=fnum
    

    if not num:
        raise HTTPException(status_code=400, detail="No valid numbers")

    # Maintain the sliding window
    global window
    window.extend(num)
    window = list(set(window))  
    if len(window) > window_size:
        window = window[-window_size:]  

    avg = sum(window) / len(window)

    return {
        "windowPrevState": window[:-len(num)] if len(window) > len(num) else [],
        "windowCurrState": window,
        "numbers": num,
        "avg": round(avg, 2)
    }
