document.addEventListener("DOMContentLoaded", () => {
    const terminals = document.querySelectorAll(".termynal");
    terminals.forEach(el => new Termynal(el));
});


function copyText(text, button) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            button.textContent = "✅ Copiado!";
            setTimeout(() => button.textContent = "📋 Copiar", 2000);
        }).catch(err => {
            console.error("Erro ao copiar:", err);
        });
    } else {
        // Fallback para ambientes sem HTTPS
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed"; // Evita rolagem
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            document.execCommand("copy");
            button.textContent = "✅ Copiado!";
            setTimeout(() => button.textContent = "📋 Copiar", 2000);
        } catch (err) {
            console.error("Fallback falhou:", err);
        }

        document.body.removeChild(textarea);
    }
}

/*
 * Licence MIT - Copyright (c) 2024 Kamil Krzyśków (HRY)
 */

function updateFontPreference(event) {
    console.debug(event);
    let cssRaw = "";
    let root = "";

    const text = event.target.dataset["text"];
    const code = event.target.dataset["code"];
    const src = event.target.dataset["src"];

    if (src !== "") {
        cssRaw += `@import url('${src}');`;
    }
    if (text !== "") {
        root += `--md-text-font: "${text}";`;
    }
    if (code !== "") {
        root += `--md-code-font: "${code}";`;
    }
    if (root !== "") {
        cssRaw += `:root { ${root} }`
    }

    // update style
    const loadedPreferences = __md_get(preferencesKey);
    loadedPreferences["__global"]["cssRaw"] = cssRaw;
    __md_set(preferencesKey, loadedPreferences);
    loadSetPreferences();
}

function startLoop(interval) {
    renderLogoAnimation();

    setInterval(() => {
        renderLogoAnimation();
    }, interval);
}

/*
    This is run immediately when loaded to limit UI elements flashing.
*/
(() => {
    const fonts = document.querySelectorAll("#md-fonts");
    fonts.forEach((font) => {
        let event_type = (font.tagName.toLowerCase() === "a") ? "click" : "change";
        font.addEventListener(event_type, updateFontPreference);
    });

    startLoop(9000);
})();
