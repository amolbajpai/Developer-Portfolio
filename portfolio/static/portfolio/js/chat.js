(function () {
    const storageKey = "portfolioChatSessionKey";
    const toggle = document.getElementById("chat-toggle");
    const panel = document.getElementById("chat-panel");
    const logEl = document.getElementById("chat-log");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const newBtn = document.getElementById("new-conversation");
    const closeBtn = document.getElementById("chat-close");
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");

    function getSessionKey() {
        let key = sessionStorage.getItem(storageKey);
        if (!key) {
            key = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
            sessionStorage.setItem(storageKey, key);
        }
        return key;
    }

    function setSessionKey(key) {
        sessionStorage.setItem(storageKey, key);
    }

    function appendBubble(role, content) {
        const bubble = document.createElement("div");
        bubble.className = "bubble " + role;
        bubble.textContent = content;
        logEl.appendChild(bubble);
        logEl.scrollTop = logEl.scrollHeight;
    }

    function csrfToken() {
        return csrfInput ? csrfInput.value : "";
    }

    async function loadHistory() {
        const key = getSessionKey();
        const response = await fetch("/api/chat/history/?session_key=" + encodeURIComponent(key));
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        logEl.innerHTML = "";
        (data.messages || []).forEach(function (item) {
            appendBubble(item.role, item.content);
        });
    }

    function closePanel() {
        panel.setAttribute("hidden", "");
        toggle.setAttribute("aria-expanded", "false");
    }

    function openPanel() {
        panel.removeAttribute("hidden");
        toggle.setAttribute("aria-expanded", "true");
        loadHistory();
    }

    toggle.addEventListener("click", function () {
        if (panel.hasAttribute("hidden")) {
            openPanel();
        } else {
            closePanel();
        }
    });

    closeBtn.addEventListener("click", closePanel);

    newBtn.addEventListener("click", function () {
        const key = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
        setSessionKey(key);
        logEl.innerHTML = "";
        input.focus();
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const message = input.value.trim();
        if (!message) {
            return;
        }
        appendBubble("user", message);
        input.value = "";
        const pending = document.createElement("div");
        pending.className = "bubble assistant";
        pending.textContent = "Thinking…";
        logEl.appendChild(pending);
        logEl.scrollTop = logEl.scrollHeight;

        try {
            const response = await fetch("/api/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken(),
                },
                body: JSON.stringify({
                    message: message,
                    session_key: getSessionKey(),
                }),
            });
            const data = await response.json();
            if (data.session_key) {
                setSessionKey(data.session_key);
            }
            pending.textContent = data.reply || data.error || "Unable to complete this request.";
        } catch (error) {
            pending.textContent = "Unable to reach the chat service.";
        }
    });
})();
