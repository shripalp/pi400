from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse
from stock.project import *
import re

class StockInputForm(forms.Form):
    stock = forms.CharField(label="Stock Name")
    
url = "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index"
tsx_list = get_tsx_list(url)
tsx_tickers = []
for s in tsx_list[0]:
    s = str(s)
    t = s.split('.')
    tsx_tickers.append(t[0])
    
def index(request):
    if "stock" not in request.session:
        request.session["stock"] = "No stock"
    
    stockdata = (getData(request.session["stock"]))
    
    return render(request, 'stock/index.html', {
        "stock":request.session["stock"],
        "rating":stockdata["rating"]
    })

def input(request):
    
    if request.method == "POST":
        form = StockInputForm(request.POST)
        
        if form.is_valid():
            stock_name = form.cleaned_data["stock"]
            
            r = re.compile(f"^.*{stock_name}.*$", re.IGNORECASE)
            newlist = list(filter(r.match, tsx_list[1]))
            
            if len(newlist) > 0:
                tickerlist = []
                for s in newlist:
                    i = tsx_list[1].index(s)
                    tickerlist.append(tsx_list[0][i])
                
            
            if stock_name.upper() in tsx_tickers:
                i = tsx_tickers.index(stock_name.upper())
                request.session["stock"] = tsx_list[0][i]
                return HttpResponseRedirect(reverse("stock:index"))
            
            elif len(newlist) > 0:
                request.session["stock"] = newlist
                request.session["tickers"] = tickerlist
                return render(request, "stock/input.html", {
                    "form":StockInputForm(),
                    "stock":request.session["stock"],
                    "tickers":request.session["tickers"]
                })
                  
            else:
                return render(request, "stock/input.html", {
                "form":form,
                "msg":"Invalid Name"  
            })
                
        else:
            return render(request, "stock/input.html", {
                
                "form":form
            })
        
    else:
        return render(request, "stock/input.html", {
            "form":StockInputForm(),
        })
    
