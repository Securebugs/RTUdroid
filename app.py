from flask import Flask, render_template_string, request, jsonify
import requests, os, json
from datetime import datetime, timedelta

app = Flask(__name__)

CACHE_FILE = "cache.json"
CACHE_EXPIRY = timedelta(hours=24)
DEFAULT_BASE = "INR"
DEFAULT_TARGET = "USD"

BASE_URLS = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base}.json",
    "https://{date}.currency-api.pages.dev/v1/currencies/{base}.json"
]

FALLBACK_CURRENCIES = {
    "USD": "United States Dollar",
    "INR": "Indian Rupee",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "NZD": "New Zealand Dollar"
}

session = requests.Session()

# ---------------- Cache ----------------
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE,"r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_cache(data):
    with open(CACHE_FILE,"w") as f:
        json.dump(data,f)

def get_cached_rate(base,target,date):
    cache = load_cache()
    key = f"{base}_{target}_{date}"
    if key in cache:
        try: ts = datetime.fromisoformat(cache[key]["timestamp"])
        except: return None
        if datetime.now()-ts<CACHE_EXPIRY: return cache[key]["rate"]
    return None

def set_cached_rate(base,target,date,rate):
    cache = load_cache()
    key = f"{base}_{target}_{date}"
    cache[key] = {"rate":rate,"timestamp":datetime.now().isoformat()}
    save_cache(cache)

# ---------------- API ----------------
def fetch_conversion(base,target,date):
    cached = get_cached_rate(base,target,date)
    if cached is not None: return cached
    base_l = base.lower(); target_l = target.lower()
    for url in BASE_URLS:
        try:
            api_url = url.format(date=date,base=base_l)
            r = session.get(api_url,timeout=5)
            if r.status_code==200:
                data = r.json()
                rates_for_base = data.get(base_l)
                if isinstance(rates_for_base,dict) and target_l in rates_for_base:
                    rate = rates_for_base[target_l]
                    set_cached_rate(base,target,date,rate)
                    return rate
        except: continue
    return None

# ---------------- Flask Routes ----------------
@app.route("/", methods=["GET","POST"])
def index():
    try:
        resp = requests.get("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json",timeout=6)
        resp.raise_for_status()
        data = resp.json()
        currencies = {k.upper():v for k,v in data.items()}
    except:
        currencies = FALLBACK_CURRENCIES

    # Defaults
    from_currency = "USD"
    to_currency = "INR"
    amount = 1
    rate = None
    converted = None
    error = None
    date_used = datetime.now().strftime("%Y-%m-%d")

    chart_base = DEFAULT_BASE
    chart_target = DEFAULT_TARGET

    if request.method=="POST":
        from_currency = (request.form.get("from_currency") or from_currency).upper()
        to_currency = (request.form.get("to_currency") or to_currency).upper()
        try: amount=float(request.form.get("amount",1))
        except: amount=1
        date_input = request.form.get("date")
        date_used = date_input if date_input else "latest"
        rate = fetch_conversion(from_currency,to_currency,date_used)
        if rate is None: error="No data available"
        else: converted = round(rate*amount,6)
        chart_base = from_currency
        chart_target = to_currency

    HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>Currency Converter & Charts</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
    background: #f8f9fa;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
    margin: 0;
    padding: 1rem;
}

body.no-scroll {
    overflow: hidden;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    padding: 1.5rem;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-2px);
}

.dropdown-menu {
    max-height: 300px;
    overflow-y: auto;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
}

.search-input {
    width: 95%;
    margin: 0.5rem auto;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.button-group {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}

.chart-reload {
    float: right;
    cursor: pointer;
    font-size: 1.25rem;
    color: #333;
    transition: color 0.3s ease;
}

.chart-reload:hover {
    color: #007bff;
}

.spinner-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.7);
    z-index: 10;
    border-radius: 12px;
}

.chart-card {
    width: 100%;
}

.chart-card .card {
    height: 100%;
    padding-bottom: 2rem;
}

.chart-card canvas {
    height: 100% !important;
    width: 100% !important;
}

.form-control, .btn {
    border-radius: 6px;
}

.btn-primary {
    background: linear-gradient(45deg, #007bff, #00b7eb);
    border: none;
}

.btn-warning {
    background: linear-gradient(45deg, #ffc107, #ffdb58);
    border: none;
}

.alert {
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.notify-alert {
    background: rgba(40, 167, 69, 0.9);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    animation: slideIn 0.5s ease-in-out;
}

.notify-alert .material-icons {
    font-size: 1.2rem;
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}

h4, h6 {
    color: #1a1a1a;
    font-weight: 600;
}

#chartSection .row {
    margin: 0;
}

.explanation-list {
    list-style: none;
    padding-left: 0;
}

.explanation-list li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
}

.explanation-list li .material-icons {
    position: absolute;
    left: 0;
    top: 0.2rem;
    font-size: 1rem;
    color: #007bff;
}

@media (max-width: 768px) {
    .card {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chart-card {
        height: 200px;
    }
    
    .chart-card .card {
        padding-bottom: 1.5rem;
    }
    
    .form-control {
        font-size: 0.9rem;
    }
    
    .button-group {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
        padding: 0.75rem;
    }
    
    .notify-alert {
        position: static;
        margin: 0.5rem;
        width: calc(100% - 1rem);
    }
}

@media (min-width: 769px) {
    .chart-card {
        height: 300px;
    }
    
    .col-md-6 {
        flex: 0 0 50%;
        max-width: 50%;
    }
    
    .notify-alert {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
}
</style>
<script>
const currenciesMap = {{ currencies_json | safe }};
function filterOptions(inputId,listContainerId){
    const filter=document.getElementById(inputId).value.toLowerCase();
    const items=document.getElementById(listContainerId).querySelectorAll('button.dropdown-item');
    items.forEach(i=>i.style.display=i.textContent.toLowerCase().includes(filter)?"":"none");
}
function selectCurrency(searchInputId,hiddenInputId,toggleId,btn){
    const code=btn.dataset.code.toUpperCase();
    const name=btn.dataset.name||'';
    document.getElementById(hiddenInputId).value=code;
    document.getElementById(toggleId).textContent=code+' - '+(name||currenciesMap[code]||'');
    document.getElementById(searchInputId).value='';
    try{bootstrap.Dropdown.getInstance(document.getElementById(toggleId)).hide();}catch(e){}
}
function swapCurrencies(){
    const fromHidden=document.getElementById('from');
    const toHidden=document.getElementById('to');
    const fromToggle=document.getElementById('fromToggle');
    const toToggle=document.getElementById('toToggle');
    const tmpVal=fromHidden.value; fromHidden.value=toHidden.value; toHidden.value=tmpVal;
    const tmpText=fromToggle.textContent; fromToggle.textContent=toToggle.textContent; toToggle.textContent=tmpText;
}
function handleHash(){
    const hash=window.location.hash;
    const converter=document.getElementById('converterCard');
    const charts=document.getElementById('chartSection');
    if(hash==="#chart"){
        converter.classList.add('d-none'); 
        charts.classList.remove('d-none'); 
        loadCharts();
    } else {
        converter.classList.remove('d-none'); 
        charts.classList.add('d-none');
    }
}
window.addEventListener('hashchange',handleHash);
window.addEventListener('load',()=>{
    handleHash();
    {% if rate is not none %}
    showNotification();
    {% endif %}
});
function clearForm(){window.location.href=window.location.pathname;}
function showSpinner(cardId){
    document.querySelector("#"+cardId+" .spinner-overlay").style.display="flex";
}
function hideSpinner(cardId){
    document.querySelector("#"+cardId+" .spinner-overlay").style.display="none";
}
function showNotification(){
    document.body.classList.add('no-scroll');
    const notify = document.createElement('div');
    notify.className = 'notify-alert';
    notify.innerHTML = '<span class="material-icons">notifications</span> Conversion completed: {{ amount }} {{ from_currency }} = {{ converted }} {{ to_currency }}';
    {% if rate is not none %}
    document.getElementById('converterCard').appendChild(notify);
    {% else %}
    document.body.appendChild(notify);
    {% endif %}
    setTimeout(()=>{
        notify.style.animation = 'slideOut 0.5s ease-in-out forwards';
        setTimeout(()=>{
            notify.remove();
            document.body.classList.remove('no-scroll');
        }, 500);
    }, 3000);
}
function loadCharts(){
    const base="{{ chart_base }}";
    const target="{{ chart_target }}";
    ["lineCard","pieCard","barCard"].forEach(id=>showSpinner(id));
    fetch(`/get_chart?base=${base}&target=${target}`)
    .then(r=>r.json())
    .then(data=>{
        // Line
        const ctxLine=document.getElementById('lineChart').getContext('2d');
        new Chart(ctxLine,{
            type:'line',
            data:{
                labels:data.labels,
                datasets:[{
                    label:'1 '+base+' in '+target,
                    data:data.data,
                    borderColor:'rgba(33,150,243,1)',
                    tension:0.2
                }]
            },
            options:{
                responsive:true,
                maintainAspectRatio:false,
                scales:{
                    y:{beginAtZero:false},
                    x:{
                        reverse:true,
                        ticks:{
                            autoSkip: true,
                            maxRotation: 45,
                            minRotation: 45,
                            padding: 5
                        }
                    }
                },
                layout:{
                    padding:{
                        bottom: 10
                    }
                }
            }
        });
        hideSpinner("lineCard");
        // Pie
        const ctxPie=document.getElementById('pieChart').getContext('2d');
        new Chart(ctxPie,{
            type:'pie',
            data:{
                labels:data.labels.slice(-5),
                datasets:[{
                    data:data.data.slice(-5),
                    backgroundColor:['#ff6b6b','#4ecdc4','#45b7d1','#96ceb4','#ffeead']
                }]
            },
            options:{
                responsive:true,
                maintainAspectRatio:false,
                plugins:{
                    tooltip:{
                        callbacks:{
                            label: function(context){
                                let label = context.label || '';
                                let value = context.raw || 0;
                                return `${label}: ${value.toFixed(4)} ${target}`;
                            }
                        }
                    }
                },
                layout:{
                    padding: 10
                }
            }
        });
        hideSpinner("pieCard");
        // Bar
        const ctxBar=document.getElementById('barChart').getContext('2d');
        new Chart(ctxBar,{
            type:'bar',
            data:{
                labels:data.labels.slice(-7).map(label => label || 'Unknown Date'),
                datasets:[{
                    label: `Rate in ${target}`,
                    data:data.data.slice(-7),
                    backgroundColor:'rgba(33,150,243,0.7)'
                }]
            },
            options:{
                responsive:true,
                maintainAspectRatio:false,
                scales:{
                    y:{beginAtZero:false},
                    x:{
                        ticks:{
                            autoSkip: true,
                            maxRotation: 45,
                            minRotation: 45,
                            padding: 5
                        }
                    }
                },
                layout:{
                    padding:{
                        bottom: 10
                    }
                }
            }
        });
        hideSpinner("barCard");

        // Update explanation
        let explanation = '';
        const currentRate = data.data[data.data.length - 1];
        const previousRate = data.data[data.data.length - 2];
        let percentChange = 'N/A';
        if (previousRate > 0 && currentRate > 0) {
            percentChange = (((currentRate - previousRate) / previousRate) * 100).toFixed(2) + '%';
        }
        const validData = data.data.filter(d => d > 0);
        const highest = validData.length > 0 ? Math.max(...validData).toFixed(4) : 'N/A';
        const lowest = validData.length > 0 ? Math.min(...validData).toFixed(4) : 'N/A';
        const average = validData.length > 0 ? (validData.reduce((a, b) => a + b, 0) / validData.length).toFixed(4) : 'N/A';
        explanation = `
        <ul class="explanation-list">
            <li><span class="material-icons">trending_up</span>Currency trend for 1 ${base} to ${target}</li>
            <li><span class="material-icons">percent</span>Day-over-day percent change: ${percentChange}</li>
            <li><span class="material-icons">arrow_upward</span>Highest rate in last 30 days: ${highest}</li>
            <li><span class="material-icons">arrow_downward</span>Lowest rate in last 30 days: ${lowest}</li>
            <li><span class="material-icons">bar_chart</span>Average rate in last 30 days: ${average}</li>
        </ul>
        `;
        document.getElementById('explanationText').innerHTML = explanation;
    });
}
</script>
</head>
<body>
<div class="container my-3">
<!-- Converter -->
<div id="converterCard" class="card p-3">
    <h4><span class="material-icons">currency_exchange</span> Currency Converter</h4>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">Amount</label>
            <input type="number" class="form-control" name="amount" value="{{ amount }}" step="any" min="0" required>
        </div>

        <div class="mb-3">
            <label class="form-label">From Currency</label>
            <div class="dropdown w-100">
                <button id="fromToggle" class="btn btn-outline-secondary dropdown-toggle w-100 text-start" data-bs-toggle="dropdown">{{ from_currency }} - {{ currencies.get(from_currency,'') }}</button>
                <ul class="dropdown-menu w-100" id="fromList">
                    <li><input type="text" class="form-control search-input" id="searchFrom" onkeyup="filterOptions('searchFrom','fromList')" placeholder="Search..."></li>
                    <li><hr class="dropdown-divider"></li>
                    {% for code,name in currencies.items() %}
                    <li><button class="dropdown-item" type="button" data-code="{{ code }}" data-name="{{ name }}" onclick="selectCurrency('searchFrom','from','fromToggle',this)">{{ code }} - {{ name }}</button></li>
                    {% endfor %}
                </ul>
                <input type="hidden" name="from_currency" id="from" value="{{ from_currency }}">
            </div>
        </div>

        <div class="text-center mb-3">
            <button type="button" class="btn btn-secondary" onclick="swapCurrencies()"><span class="material-icons">swap_horiz</span></button>
        </div>

        <div class="mb-3">
            <label class="form-label">To Currency</label>
            <div class="dropdown w-100">
                <button id="toToggle" class="btn btn-outline-secondary dropdown-toggle w-100 text-start" data-bs-toggle="dropdown">{{ to_currency }} - {{ currencies.get(to_currency,'') }}</button>
                <ul class="dropdown-menu w-100" id="toList">
                    <li><input type="text" class="form-control search-input" id="searchTo" onkeyup="filterOptions('searchTo','toList')" placeholder="Search..."></li>
                    <li><hr class="dropdown-divider"></li>
                    {% for code,name in currencies.items() %}
                    <li><button class="dropdown-item" type="button" data-code="{{ code }}" data-name="{{ name }}" onclick="selectCurrency('searchTo','to','toToggle',this)">{{ code }} - {{ name }}</button></li>
                    {% endfor %}
                </ul>
                <input type="hidden" name="to_currency" id="to" value="{{ to_currency }}">
            </div>
        </div>

        <div class="mb-3">
            <label class="form-label">Date</label>
            <input type="date" class="form-control" name="date" max="{{ today }}">
        </div>

        <div class="button-group">
            <button type="submit" class="btn btn-primary">Convert</button>
            <span class="chart-dot" title="Go to chart" onclick="window.location.hash='#chart'">.</span>
            <button type="button" class="btn btn-warning" onclick="clearForm()">Clear</button>
        </div>

        {% if error %}
        <div class="alert alert-danger mt-3">{{ error }}</div>
        {% elif rate is not none %}
        <div class="alert alert-success mt-3">
            <strong>{{ amount }} {{ from_currency }} = {{ converted }} {{ to_currency }}</strong>
            <div class="small text-muted">1 {{ from_currency }} = {{ rate }} {{ to_currency }} (Date: {{ date_used }})</div>
        </div>
        {% endif %}
    </form>
</div>

<!-- Charts -->
<div id="chartSection" class="d-none my-3">
    <div class="row g-3">
        <div class="col-md-6 col-12 chart-card" id="lineCard">
            <div class="card p-3">
                <h6>Line Chart <span class="material-icons chart-reload" onclick="loadCharts()">autorenew</span></h6>
                <div class="spinner-overlay" style="display:none;"><div class="spinner-border text-primary"></div></div>
                <canvas id="lineChart"></canvas>
            </div>
        </div>

        <div class="col-md-6 col-12 chart-card" id="pieCard">
            <div class="card p-3">
                <h6>Pie Chart <span class="material-icons chart-reload" onclick="loadCharts()">autorenew</span></h6>
                <div class="spinner-overlay" style="display:none;"><div class="spinner-border text-primary"></div></div>
                <canvas id="pieChart"></canvas>
            </div>
        </div>

        <div class="col-md-6 col-12 chart-card" id="barCard">
            <div class="card p-3">
                <h6>Bar Chart <span class="material-icons chart-reload" onclick="loadCharts()">autorenew</span></h6>
                <div class="spinner-overlay" style="display:none;"><div class="spinner-border text-primary"></div></div>
                <canvas id="barChart"></canvas>
            </div>
        </div>

        <div class="col-md-6 col-12 chart-card" id="explanationCard">
            <div class="card p-3">
                <h6>Explanation</h6>
                <p id="explanationText">Currency trend analysis and insights based on latest conversion rates. Data is live and updates when you perform a conversion.</p>
            </div>
        </div>
    </div>
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body></html>
"""
    return render_template_string(HTML,
                                  currencies=currencies,
                                  currencies_json=json.dumps(currencies),
                                  from_currency=from_currency,
                                  to_currency=to_currency,
                                  amount=amount,
                                  rate=rate,
                                  converted=converted,
                                  error=error,
                                  date_used=date_used,
                                  today=datetime.now().strftime("%Y-%m-%d"),
                                  chart_base=chart_base,
                                  chart_target=chart_target)

# ---------------- Chart AJAX Endpoint ----------------
@app.route("/get_chart")
def get_chart():
    base = request.args.get("base", DEFAULT_BASE).upper()
    target = request.args.get("target", DEFAULT_TARGET).upper()
    labels = []
    data = []
    today = datetime.now()
    for i in range(30):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        rate = fetch_conversion(base,target,date)
        labels.append(date)
        data.append(rate if rate is not None else 0)
    labels.reverse()
    data.reverse()
    return jsonify({"labels":labels,"data":data})

if __name__=="__main__":
    app.run(debug=True)
