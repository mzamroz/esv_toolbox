# Skrypt do obsługi ciasteczek w przeglądarce
COOKIE_SCRIPT = """
<script>
// Funkcja do ustawiania ciasteczka
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

// Funkcja do pobierania ciasteczka
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

// Funkcja do usuwania ciasteczka
function eraseCookie(name) {   
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

// Sprawdzenie, czy w ciasteczku są dane sesji
document.addEventListener('DOMContentLoaded', function() {
    const sessionData = getCookie('bc_integrator_session');
    if (sessionData) {
        try {
            const sessionObj = JSON.parse(sessionData);
            // Sprawdzenie, czy sesja nie wygasła
            if (sessionObj.session_expiry && sessionObj.session_expiry > (Date.now() / 1000)) {
                // Jeśli są dane sesji, wysyłamy je do Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: sessionObj
                }, '*');
            } else {
                // Jeśli sesja wygasła, usuwamy ciasteczko
                eraseCookie('bc_integrator_session');
            }
        } catch (e) {
            console.error('Błąd podczas parsowania danych sesji:', e);
            eraseCookie('bc_integrator_session');
        }
    }
});

// Nasłuchiwanie na wiadomości od Streamlit
window.addEventListener('message', function(event) {
    if (event.data.type === 'streamlit:setSessionCookie') {
        setCookie('bc_integrator_session', event.data.value, 1); // Ciasteczko ważne przez 1 dzień
    } else if (event.data.type === 'streamlit:clearSessionCookie') {
        eraseCookie('bc_integrator_session');
    }
});
</script>
"""

# Skrypt do ustawiania ciasteczka
def get_set_cookie_script(session_data):
    return f"""
<script>
window.parent.postMessage({{
    type: 'streamlit:setSessionCookie',
    value: '{session_data}'
}}, '*');
</script>
"""

# Skrypt do usuwania ciasteczka
CLEAR_COOKIE_SCRIPT = """
<script>
window.parent.postMessage({
    type: 'streamlit:clearSessionCookie'
}, '*');
</script>
""" 