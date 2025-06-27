const clickHandler = function () {
    let currentAddr = Cookies.get('address') || "https://127.0.0.1/";
    let addr = prompt("Set your HOPE server address", currentAddr);
    Cookies.set('address', addr, currentAddr);
    location.reload();
};
const setAddress = function () {
    let cookieAddr = Cookies.get('address');
    if (!cookieAddr) {
        cookieAddr = "[SERVER_ADDRESS]"
    }
    for (const cell of document.getElementsByTagName('code')) {
        cell.innerHTML = cell.innerHTML.replace('[SERVER_ADDRESS]', cookieAddr);
    }
};
// addEventListener('click', function(e) {
//     setTimeout(setAddress, 500);
// })
addEventListener('load', function (e) {
    setAddress();
    let btn = document.getElementById("set-address");
    if (btn) {
        btn.addEventListener('click', clickHandler);
    }
});

var open = window.XMLHttpRequest.prototype.open,
    send = window.XMLHttpRequest.prototype.send, onReadyStateChange;

function sendReplacement(data) {
    console.warn('Sending HTTP request data : ', data);

    if (this.onreadystatechange) {
        this._onreadystatechange = this.onreadystatechange;
    }
    this.onreadystatechange = onReadyStateChangeReplacement;
    return send.apply(this, arguments);
}

function onReadyStateChangeReplacement() {
    if (this.readyState === XMLHttpRequest.DONE) {
        setTimeout(setAddress, 100);
    }
    if (this._onreadystatechange) {
        return this._onreadystatechange.apply(this, arguments);
    }

}

window.XMLHttpRequest.prototype.send = sendReplacement;
